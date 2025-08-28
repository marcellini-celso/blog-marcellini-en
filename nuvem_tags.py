#!/usr/bin/env python3
import os
import unicodedata
import argparse
from wordcloud import WordCloud
import matplotlib.pyplot as plt  # noqa: F401  (ensures matplotlib backend is available)

DEFAULT_FREQ_FILE = "tags_freq.txt"
DEFAULT_OUTPUT = "nuvem_tags.png"  # keep current filename to preserve compatibility

def load_frequencies(path: str):
    """Read frequency file and return a dict {tag: count}."""
    if not os.path.exists(path):
        print(f"❌ File '{path}' not found.")
        return {}

    freqs = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 2:
                try:
                    count = int(parts[0])
                    tag = unicodedata.normalize("NFC", " ".join(parts[1:]).strip())
                    if tag:
                        freqs[tag] = count
                except ValueError:
                    print(f"⚠️ Could not parse line (ignored): {line.strip()}")
    return freqs

def build_wordcloud(freqs: dict, out_path: str, width: int, height: int, colormap: str):
    """Generate a tag word cloud image."""
    if not freqs:
        print("⚠️ No valid frequencies found.")
        return

    wc = WordCloud(
        width=width,
        height=height,
        background_color="white",
        colormap=colormap,
        font_path=None,     # set a font path if you need specific glyph coverage
        prefer_horizontal=0.8,
        margin=5,
    )
    wc.generate_from_frequencies(freqs)
    wc.to_file(out_path)
    print(f"✅ Tag cloud saved as '{out_path}'")

def parse_args():
    p = argparse.ArgumentParser(description="Generate a tag word cloud image.")
    p.add_argument("--freq-file", default=DEFAULT_FREQ_FILE, help="Path to the frequencies file (default: tags_freq.txt)")
    p.add_argument("--out", default=DEFAULT_OUTPUT, help="Output image path (default: nuvem_tags.png)")
    p.add_argument("--width", type=int, default=1000, help="Image width (default: 1000)")
    p.add_argument("--height", type=int, default=500, help="Image height (default: 500)")
    p.add_argument("--colormap", default="tab20c", help="Matplotlib colormap (default: tab20c)")
    return p.parse_args()

if __name__ == "__main__":
    args = parse_args()
    freqs = load_frequencies(args.freq_file)
    build_wordcloud(freqs, args.out, args.width, args.height, args.colormap)

