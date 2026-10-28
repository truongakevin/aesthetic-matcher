import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
from aesthetic_catalog import display_name, upsert_aesthetics
from summarized_aesthetics import aesthetics
from wiki_aesthetics import wiki_aesthetics

spec = importlib.util.spec_from_file_location('sync', BACKEND.parents[1] / 'research/catalog/sync_aesthetics_wiki.py')
sync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync)


class CatalogTests(unittest.TestCase):
    def test_preserves_prompts_and_idempotent(self):
        old = ['Goth, dark clothing', 'Retired category, description']
        result = upsert_aesthetics(old, [' goth ', 'New Name', 'new name'])
        self.assertEqual(result, old + ['New Name'])
        self.assertEqual(upsert_aesthetics(result, ['New Name']), result)

    def test_comma_title_is_not_truncated_or_duplicated(self):
        wiki = ['Comma, Title', 'Goth']
        self.assertEqual(display_name('Comma, Title', wiki), 'Comma, Title')
        self.assertEqual(upsert_aesthetics(['Comma, Title, description'], wiki), ['Comma, Title, description', 'Goth'])

    def test_real_catalog_preserves_all_original_prompts(self):
        combined = upsert_aesthetics(aesthetics, wiki_aesthetics)
        self.assertEqual(combined[:len(aesthetics)], aesthetics)
        self.assertGreater(len(combined), len(aesthetics))
        self.assertEqual(upsert_aesthetics(combined, wiki_aesthetics), combined)

    def test_parser_excludes_navigation_and_deduplicates(self):
        payload = {'parse': {'text': {'*': '<a href="/wiki/Home" title="Home">Home</a><div class="twocolumn"><ul><li><a href="/wiki/Goth" title="Goth">Goth</a></li><li><a href="/wiki/Goth" title="goth">goth</a></li></ul></div>'}}}
        self.assertEqual(sync.extract_wiki_labels(payload), ['Goth'])
        with self.assertRaises(ValueError):
            sync.extract_wiki_labels({'parse': {'text': {'*': 'error page'}}})

    def test_refresh_retains_previous_and_failure_does_not_replace(self):
        import json
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            catalog = root / 'wiki.py'
            sync.write_wiki_catalog(catalog, ['Previously Imported'])
            source = root / 'source.json'
            source.write_text(json.dumps({'parse': {'text': {'*': '<div class="twocolumn"><li><a href="/wiki/New" title="New">New</a></li></div>'}}}))
            argv = ['sync', '--apply', '--input-json', str(source), '--wiki-catalog', str(catalog), '--output', str(root / 'report.json')]
            with patch.object(sys, 'argv', argv):
                self.assertEqual(sync.main(), 0)
                self.assertEqual(sync.load_matcher_labels(catalog, 'wiki_aesthetics', False), ['New', 'Previously Imported'])
                before = catalog.read_bytes()
                self.assertEqual(sync.main(), 0)
                self.assertEqual(catalog.read_bytes(), before)
                source.write_text('{}')
                self.assertEqual(sync.main(), 1)
                self.assertEqual(catalog.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
