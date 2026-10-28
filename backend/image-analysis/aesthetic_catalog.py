"""Merge Wiki names without replacing existing descriptive prompts."""


def normalize_name(value):
    return ' '.join(value.split()).casefold()


def display_name(prompt, wiki_labels):
    """Preserve complete Wiki titles, including titles containing commas."""
    key = normalize_name(prompt)
    for label in sorted(wiki_labels, key=len, reverse=True):
        name = normalize_name(label)
        if key == name or key.startswith(name + ','):
            return label
    return prompt.split(',', 1)[0].strip()


def upsert_aesthetics(existing_prompts, wiki_labels):
    combined = list(existing_prompts)
    known = {normalize_name(display_name(p, wiki_labels)) for p in existing_prompts}
    for label in wiki_labels:
        label = ' '.join(label.split())
        key = normalize_name(label)
        if key and key not in known:
            combined.append(label)
            known.add(key)
    return combined
