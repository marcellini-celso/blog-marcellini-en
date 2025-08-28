#!/bin/bash
set -euo pipefail

CATS_FILE="categories.qmd"
CATS_DIR="categories"
POSTS_JSON="docs/posts.json"
TEMP_SCRIPT="generate_category_pages_temp.py"

mkdir -p "$CATS_DIR"

cat > "$TEMP_SCRIPT" <<'PY'
import json, unicodedata, html
from pathlib import Path
from collections import defaultdict
from datetime import datetime

POSTS_JSON = Path("docs/posts.json")
CATS_DIR   = Path("categories")
CATS_FILE  = Path("categories.qmd")

FALLBACK_IMG = "/images/banner.png"

def slugify(text: str) -> str:
    t = text.lower().strip().replace(" ", "-").replace("ç", "c")
    t = unicodedata.normalize("NFKD", t).encode("ascii","ignore").decode("ascii")
    return t

def load_posts():
    with POSTS_JSON.open(encoding="utf-8") as f:
        return json.load(f)

def parse_date(d):
    try:
        return datetime.strptime(d, "%Y-%m-%d")
    except Exception:
        return datetime.min  # sem data vai pro fim

def group_by_category(posts):
    counts = defaultdict(int)
    groups = defaultdict(list)
    for p in posts:
        for c in p.get("categories", []) or []:
            counts[c] += 1
            groups[c].append(p)
    return counts, groups

def write_categories_qmd(counts):
    with CATS_FILE.open("w", encoding="utf-8") as f:
        f.write("""---
title: "Categories"
format: html
page-layout: full
---

## 📚 All Categories

::: {.tag-grid}
""")
        for cat, freq in sorted(counts.items(), key=lambda x: (-x[1], x[0].lower())):
            slug = slugify(cat)
            f.write(f'<a href="/categories/{slug}.html" class="tag-card">{html.escape(cat)} ({freq})</a>\n')
        f.write(":::\n")

def card_html(p: dict) -> str:
    title = html.escape(p.get("title", ""))
    href  = "/" + p.get("href","").lstrip("/")
    desc  = p.get("description") or ""
    desc  = html.escape(desc) if desc else ""
    img   = p.get("image") or FALLBACK_IMG
    tags  = p.get("tags") or []

    # Começar cada tag de bloco na coluna 0 para o Pandoc não escapar
    parts = []
    parts.append('<div class="card">')
    parts.append(f'<a class="card-link" href="{href}">')
    if img:
        parts.append(f'<div class="card-image"><img src="{"/" + img.lstrip("/")}" alt="{title}"></div>')
    parts.append('<div class="card-content">')
    parts.append(f'<h3 class="card-title">{title}</h3>')
    if desc:
        parts.append(f'<p class="card-desc">{desc}</p>')
    if tags:
        chips = " ".join(f'<span class="chip">#{html.escape(t)}</span>' for t in tags[:6])
        parts.append(f'<div class="chips">{chips}</div>')
    parts.append('</div>')   # .card-content
    parts.append('</a>')
    parts.append('</div>')   # .card
    return "\n".join(parts)

def write_category_pages(groups):
    CATS_DIR.mkdir(exist_ok=True)
    for cat, posts in groups.items():
        slug = slugify(cat)
        out = CATS_DIR / f"{slug}.qmd"
        posts_sorted = sorted(
            posts,
            key=lambda p: (parse_date(p.get("date")), p.get("title","").lower()),
            reverse=True
        )
        with out.open("w", encoding="utf-8") as f:
            f.write(f"---\ntitle: \"{cat}\"\nformat: html\npage-layout: full\n---\n\n")
            f.write("[⬅ Back to All Categories](../categories.qmd)\n\n")
            f.write(f"## Posts in **{html.escape(cat)}**\n\n")
            f.write("::: {.cards-grid}\n")
            for p in posts_sorted:
                f.write(card_html(p) + "\n")
            f.write(":::\n")
        print(f"✅ Page generated: {out}")

if __name__ == "__main__":
    posts = load_posts()
    counts, groups = group_by_category(posts)
    write_categories_qmd(counts)
    write_category_pages(groups)
PY

python3 "$TEMP_SCRIPT"
rm -f "$TEMP_SCRIPT"

echo "✅ Categories updated with correct grid and card layout."

