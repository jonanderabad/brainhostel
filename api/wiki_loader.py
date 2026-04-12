"""Loads and concatenates all wiki .md articles into a single string for the agent system prompt."""

import os


def load_wiki(wiki_dir: str = None) -> str:
    if wiki_dir is None:
        wiki_dir = os.path.join(os.path.dirname(__file__), "..", "wiki")

    wiki_dir = os.path.abspath(wiki_dir)

    if not os.path.isdir(wiki_dir):
        raise ValueError(f"Wiki directory not found: {wiki_dir}")

    md_files = sorted(
        f for f in os.listdir(wiki_dir) if f.endswith(".md")
    )

    if not md_files:
        raise ValueError(f"No .md files found in: {wiki_dir}")

    parts = []
    for filename in md_files:
        filepath = os.path.join(wiki_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read().strip()
        parts.append(f"=== ARTÍCULO: {filename} ===\n{content}")

    return "\n\n".join(parts)
