#!/usr/bin/env python3
import os, re, json
from pathlib import Path

POSTS_DIR = Path("posts")
OUTPUT_JSON = Path("docs/posts.json")

FRONT_MATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*", re.DOTALL | re.MULTILINE)

def read_front_matter(text: str) -> str:
    m = FRONT_MATTER_RE.search(text)
    return m.group(1) if m else ""

def _dedupe(seq):
    seen=set(); out=[]
    for x in seq:
        if x not in seen:
            seen.add(x); out.append(x)
    return out

def _parse_inline_list(s: str):
    parts = re.findall(r'"([^"]+)"|\'([^\']+)\'|([^,\n]+)', s)
    vals=[]
    for a,b,c in parts:
        v=(a or b or c).strip()
        if v: vals.append(v)
    return _dedupe(vals)

def _parse_block_list(block: str):
    vals=[]
    for line in block.splitlines():
        m = re.search(r'\s*-\s*(?:"([^"]+)"|\'([^\']+)\'|(.*))$', line)
        if m:
            v=(m.group(1) or m.group(2) or m.group(3) or "").strip()
            if v: vals.append(v)
    return _dedupe(vals)

def extract_field_list(fm: str, field: str):
    m_inline = re.search(rf'(?ms)^\s*{field}\s*:\s*\[(.*?)\]\s*$', fm)
    if m_inline:
        return _parse_inline_list(m_inline.group(1))
    m_block = re.search(rf'(?ms)^\s*{field}\s*:\s*\n((?:\s*-\s*.*\n)+)', fm)
    if m_block:
        return _parse_block_list(m_block.group(1))
    return []

def extract_scalar(fm: str, field: str):
    m = re.search(rf'(?mi)^\s*{field}:\s*(?:"([^"]+)"|\'([^\']+)\'|(.+))\s*$', fm)
    if not m: return None
    for g in m.groups():
        if g and g.strip():
            return g.strip()
    return None

def extract_title(fm: str):
    return extract_scalar(fm, "title")

def extract_date(fm: str):
    return extract_scalar(fm, "date")

def extract_description(fm: str):
    return extract_scalar(fm, "description")

def extract_image(fm: str):
    # 1) scalar: image:, thumbnail:, cover:, featured:, featured-image:
    for key in ("image", "thumbnail", "cover", "featured", "featured-image"):
        v = extract_scalar(fm, key)
        if v: return v

    # 2) inline map: image: {src: ..., href: ...}
    m_inline = re.search(r'(?ms)^\s*image\s*:\s*\{(.*?)\}\s*$', fm)
    if m_inline:
        body = m_inline.group(1)
        for key in ("src", "href", "path"):
            m = re.search(rf'{key}\s*:\s*(?:"([^"]+)"|\'([^\']+)\'|([^,\n]+))', body)
            if m:
                return (m.group(1) or m.group(2) or m.group(3) or "").strip()

    # 3) block map:
    m_block = re.search(r'(?ms)^\s*image\s*:\s*\n((?:\s+.+\n)+)', fm)
    if m_block:
        block = m_block.group(1)
        for key in ("src", "href", "path"):
            m = re.search(rf'^\s+{key}\s*:\s*(?:"([^"]+)"|\'([^\']+)\'|(.+))\s*$', block, re.MULTILINE)
            if m:
                return (m.group(1) or m.group(2) or m.group(3) or "").strip()

    return None

def extract_post_metadata(qmd_file: Path):
    text = qmd_file.read_text(encoding="utf-8", errors="ignore")
    fm = read_front_matter(text)
    if not fm:
        return None

    title = extract_title(fm)
    if not title:
        return None

    tags = extract_field_list(fm, "tags")
    categories = extract_field_list(fm, "categories")
    date = extract_date(fm)
    description = extract_description(fm)
    image = extract_image(fm)

    href = str(qmd_file.with_suffix(".html")).replace(os.sep, "/")
    return {
        "title": title,
        "href": href,
        "tags": tags,
        "categories": categories,
        "date": date,
        "description": description,
        "image": image,
    }

def collect_posts():
    items=[]
    for root, _, files in os.walk(POSTS_DIR):
        for name in files:
            if name.endswith(".qmd"):
                meta = extract_post_metadata(Path(root)/name)
                if meta: items.append(meta)
    return items

def save_json(posts):
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(posts, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"✅ {len(posts)} posts saved to {OUTPUT_JSON}")

if __name__ == "__main__":
    save_json(collect_posts())

