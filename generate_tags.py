#!/usr/bin/env python3
import json
import sys
import unicodedata
from collections import Counter
from pathlib import Path

# Same interface/outputs, except the HTML filename (now generated_tag_list.html)
JSON_FILE = Path("docs/posts.json")
FREQ_FILE = Path("tags_freq.txt")
QMD_FILE  = Path("tags.qmd")
HTML_FILE = Path("generated_tag_list.html")   # ← renamed

def load_tags(json_file: Path):
    """Load unique tags per post from posts.json (NFC-normalized)."""
    if not json_file.exists():
        print(f"❌ File not found: {json_file}", file=sys.stderr)
        return []

    try:
        with json_file.open(encoding="utf-8") as f:
            posts = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in {json_file}: {e}", file=sys.stderr)
        return []

    tags = []
    for post in posts:
        unique_tags = set()
        for tag in post.get("tags", []):
            tag_norm = unicodedata.normalize("NFC", tag.strip())
            if tag_norm:
                unique_tags.add(tag_norm)
        tags.extend(unique_tags)
    return tags

def generate_reports(tags):
    """Write tags_freq.txt, tags.qmd and generated_tag_list.html."""
    counts = Counter(tags)
    # Sort by descending frequency, then alphabetically (case-insensitive)
    ordered = sorted(counts.items(), key=lambda x: (-x[1], x[0].lower()))

    # tags_freq.txt
    FREQ_FILE.write_text(
        "".join(f"{freq} {tag}\n" for tag, freq in ordered),
        encoding="utf-8"
    )

    # tags.qmd (simple list; update_tags.sh builds the grid later)
    QMD_FILE.write_text(
        "# Tags\n\n" + "".join(f"- **{tag}** ({freq})\n" for tag, freq in ordered),
        encoding="utf-8"
    )

    # generated_tag_list.html
    with HTML_FILE.open("w", encoding="utf-8") as f:
        f.write("<html><head><meta charset='utf-8'><title>Tags</title></head><body>\n")
        f.write("<h1>Tag List</h1>\n<ul>\n")
        for tag, freq in ordered:
            f.write(f"<li><b>{tag}</b> ({freq})</li>\n")
        f.write("</ul></body></html>\n")

if __name__ == "__main__":
    tags = load_tags(JSON_FILE)
    if not tags:
        print("❌ No tags found (or posts.json missing/invalid).")
    else:
        generate_reports(tags)
        print("✅ Tag files generated successfully (including generated_tag_list.html).")

