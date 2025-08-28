#!/bin/bash
set -e

# Paths
TAGS_FREQ="tags_freq.txt"
TAGS_FILE="tags.qmd"
TAGS_DIR="tags"
TAGCLOUD_SCRIPT="nuvem_tags.py"     # script Python que gera a nuvem
TAGCLOUD_OUT="tag_cloud.png"        # novo nome do arquivo de imagem
POSTS_JSON="docs/posts.json"
TEMP_SCRIPT="generate_tag_pages_temp.py"

# Garante a pasta e (re)gera frequências/listas
mkdir -p "$TAGS_DIR"
python3 generate_tags.py

# Cabeçalho do tags.qmd
cat > "$TAGS_FILE" <<'EOF'
---
title: "Tags"
format: html
page-layout: full
---

::: {.tag-nuvem}
![](tag_cloud.png){width=100%}
:::

## 📚 All Tags

::: {.tag-grid}
EOF

# Geração dos cards de tags
while read -r line; do
  freq=$(echo "$line" | awk '{print $1}')
  tag=$(echo "$line" | cut -d' ' -f2-)
  slug=$(echo "$tag" | tr '[:upper:]' '[:lower:]' | sed 's/ /-/g' | sed 's/[ç]/c/g' | iconv -f utf8 -t ascii//TRANSLIT)
  echo "<a href=\"/tags/$slug.html\" class=\"tag-card\">$tag ($freq)</a>" >> "$TAGS_FILE"
done < "$TAGS_FREQ"

echo ":::" >> "$TAGS_FILE"

# Gera a nuvem de tags com o novo nome de arquivo
python3 "$TAGCLOUD_SCRIPT" --freq-file "$TAGS_FREQ" --out "$TAGCLOUD_OUT"

# Script Python temporário para gerar páginas por tag (links absolutos)
cat > "$TEMP_SCRIPT" <<'EOF'
import json
from pathlib import Path
from collections import defaultdict
import unicodedata

POSTS_JSON = Path("docs/posts.json")
TAGS_DIR = Path("tags")

def slugify(tag: str) -> str:
    tag = tag.lower().replace(" ", "-").replace("ç", "c")
    tag = unicodedata.normalize("NFKD", tag).encode("ascii", "ignore").decode("ascii")
    return tag

def load_posts():
    with open(POSTS_JSON, encoding="utf-8") as f:
        return json.load(f)

def group_by_tag(posts):
    tags_dict = defaultdict(list)
    for post in posts:
        for tag in post.get("tags", []):
            tags_dict[tag].append({
                "title": post.get("title", ""),
                "href": post.get("href", ""),
            })
    return tags_dict

def generate_pages(tags_dict):
    TAGS_DIR.mkdir(exist_ok=True)
    for tag, posts in tags_dict.items():
        slug = slugify(tag)
        path = TAGS_DIR / f"{slug}.qmd"
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"---\ntitle: \"{tag}\"\nformat: html\n---\n\n")
            f.write("[⬅ Back to All Tags](../tags.qmd)\n\n")
            f.write(f"## Posts with the **{tag}** tag\n\n")
            for post in posts:
                f.write(f"- [{post['title']}](/{post['href']})\n")
        print(f"✅ Page generated: {path}")

if __name__ == "__main__":
    posts = load_posts()
    tags = group_by_tag(posts)
    generate_pages(tags)
EOF

# Executa e limpa
python3 "$TEMP_SCRIPT"
rm "$TEMP_SCRIPT"

echo "✅ Tags pages updated successfully (tag cloud: $TAGCLOUD_OUT)."

