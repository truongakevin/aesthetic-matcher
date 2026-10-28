#!/usr/bin/env python3
"""Compare Aesthetics Wiki's current list with the matcher catalog.

By default writes a discovery report. --apply merges labels into the checked-in
backend snapshot. Existing prompts and previously imported labels are retained.
The service reads that snapshot at startup, never fetches Wiki data per request.
"""

from __future__ import annotations

import argparse
import ast
from datetime import datetime, timezone
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from typing import Any
from urllib.request import Request, urlopen


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CATALOG = REPO_ROOT / "backend/image-analysis/summarized_aesthetics.py"
DEFAULT_OUTPUT = REPO_ROOT / "research/catalog/generated/aesthetics-wiki-diff.json"
DEFAULT_WIKI_CATALOG = REPO_ROOT / "backend/image-analysis/wiki_aesthetics.py"
WIKI_PAGE_URL = "https://aesthetics.fandom.com/wiki/List_of_Aesthetics"
WIKI_API_URL = (
    "https://aesthetics.fandom.com/api.php"
    "?action=parse&page=List_of_Aesthetics&prop=text&format=json&origin=%2A"
)
USER_AGENT = "AestheticMatcherLab/0.1 (catalog research)"


def normalize_name(value: str) -> str:
    """Normalize superficial differences while preserving distinct labels."""
    return re.sub(r"\s+", " ", value).strip().casefold()


def load_matcher_labels(path: Path, variable="aesthetics", split_prompts=True) -> list[str]:
    """Read first-field labels from the backend's Python literal safely."""
    module = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    value: Any | None = None
    for node in module.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == variable
            for target in node.targets
        ):
            value = ast.literal_eval(node.value)
            break

    if not isinstance(value, list):
        raise ValueError(f"No list assignment named 'aesthetics' found in {path}")

    labels: list[str] = []
    for prompt in value:
        if not isinstance(prompt, str):
            raise ValueError(f"Catalog entry is not a string: {prompt!r}")
        label = (prompt.split(",", 1)[0] if split_prompts else prompt).strip()
        if label:
            labels.append(label)
    return labels


class AestheticListParser(HTMLParser):
    """Collect linked titles from list items inside alphabetical list columns."""

    def __init__(self) -> None:
        super().__init__()
        self._div_depth = 0
        self._column_depth: int | None = None
        self._list_item_depth = 0
        self.labels: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "div":
            self._div_depth += 1
            classes = (attributes.get("class") or "").split()
            if self._column_depth is None and "twocolumn" in classes:
                self._column_depth = self._div_depth
        elif self._column_depth is not None and tag == "li":
            self._list_item_depth += 1
        elif (
            self._column_depth is not None
            and self._list_item_depth > 0
            and tag == "a"
        ):
            title = attributes.get("title")
            href = attributes.get("href") or ""
            if title and href.startswith("/wiki/"):
                self.labels.append(title)

    def handle_endtag(self, tag: str) -> None:
        if self._column_depth is not None and tag == "li" and self._list_item_depth:
            self._list_item_depth -= 1
        if tag == "div":
            if self._column_depth == self._div_depth:
                self._column_depth = None
                self._list_item_depth = 0
            self._div_depth -= 1


def extract_wiki_labels(payload: dict[str, Any]) -> list[str]:
    """Extract titles listed in the wiki page's alphabetical columns."""
    try:
        html = payload["parse"]["text"]["*"]
    except (KeyError, TypeError) as exc:
        raise ValueError("Unexpected MediaWiki response: missing parse.text HTML") from exc
    if not isinstance(html, str):
        raise ValueError("Unexpected MediaWiki response: parse.text HTML is not text")

    parser = AestheticListParser()
    parser.feed(html)
    if not parser.labels:
        raise ValueError("No entries found in the wiki's alphabetical lists")

    labels: dict[str, str] = {}
    for title in parser.labels:
        clean_title = re.sub(r"\s+", " ", title).strip()
        labels.setdefault(normalize_name(clean_title), clean_title)
    return sorted(labels.values(), key=str.casefold)


def fetch_wiki_payload() -> dict[str, Any]:
    request = Request(WIKI_API_URL, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def build_report(current: list[str], discovered: list[str]) -> dict[str, Any]:
    current_by_key = {normalize_name(label): label for label in current}
    discovered_by_key = {normalize_name(label): label for label in discovered}

    added = [
        discovered_by_key[key]
        for key in sorted(discovered_by_key.keys() - current_by_key.keys())
    ]
    missing = [
        current_by_key[key]
        for key in sorted(current_by_key.keys() - discovered_by_key.keys())
    ]
    shared = current_by_key.keys() & discovered_by_key.keys()

    return {
        "schema_version": 1,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "source": {
            "name": "Aesthetics Wiki",
            "page_url": WIKI_PAGE_URL,
            "api_url": WIKI_API_URL,
        },
        "counts": {
            "matcher": len(current_by_key),
            "wiki": len(discovered_by_key),
            "shared": len(shared),
            "new_candidates": len(added),
            "not_on_current_wiki_list": len(missing),
        },
        "new_candidates": added,
        "not_on_current_wiki_list": missing,
    }


def write_wiki_catalog(path: Path, labels: list[str]) -> None:
    """Write the current wiki labels as deterministic Python source."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        '"""Generated Aesthetics Wiki labels. Run the catalog sync to update."""',
        "",
        "wiki_aesthetics = [",
    ]
    lines.extend(f"    {label!r}," for label in labels)
    lines.extend(["]", ""])
    temporary = path.with_suffix(".py.tmp")
    temporary.write_text("\n".join(lines), encoding="utf-8")
    temporary.replace(path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Upsert the current wiki labels into the backend's generated catalog.",
    )
    parser.add_argument("--wiki-catalog", type=Path, default=DEFAULT_WIKI_CATALOG)
    parser.add_argument(
        "--input-json",
        type=Path,
        help="Use a saved MediaWiki response instead of making a network request.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        current = load_matcher_labels(args.catalog)
        if args.input_json:
            payload = json.loads(args.input_json.read_text(encoding="utf-8"))
        else:
            payload = fetch_wiki_payload()
        discovered = extract_wiki_labels(payload)
        previous = load_matcher_labels(args.wiki_catalog, "wiki_aesthetics", False) if args.wiki_catalog.exists() else []
        merged = {normalize_name(label): label for label in previous}
        for label in discovered:
            merged.setdefault(normalize_name(label), label)
        retained = sorted(merged.values(), key=str.casefold)
        report = build_report(current, discovered)
        report["retained_wiki_labels"] = len(retained)
        report["new_since_snapshot"] = sorted(set(merged) - {normalize_name(x) for x in previous})
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Catalog sync failed: {exc}", file=sys.stderr)
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    if args.apply:
        write_wiki_catalog(args.wiki_catalog, retained)
    counts = report["counts"]
    print(
        f"Compared {counts['matcher']} matcher labels with {counts['wiki']} wiki pages: "
        f"{counts['new_candidates']} new candidates, "
        f"{counts['not_on_current_wiki_list']} matcher-only labels."
    )
    print(f"Report: {args.output}")
    if args.apply:
        print(f"Updated wiki catalog: {args.wiki_catalog}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
