"""Refresh the separate recent-article and course-lesson panels."""
from datetime import date
from pathlib import Path
import re
import yaml

def coletar_posts():
    posts = []
    for source in sorted(Path("posts").rglob("*.qmd")):
        text = source.read_text(encoding="utf-8")
        match = re.match(r"\A---\s*\n(.*?)\n---(?:\s*\n|$)", text, re.S)
        if not match:
            continue
        metadata = yaml.safe_load(match.group(1)) or {}
        if metadata.get("draft") is True or not metadata.get("title") or not metadata.get("date"):
            continue
        published = str(metadata["date"])[:10]
        date.fromisoformat(published)
        posts.append({"title": metadata["title"], "date": published,
                      "href": source.with_suffix(".html").as_posix()})
    return posts


def _ordem_natural(caminho):
    return tuple((p.isdigit(), int(p) if p.isdigit() else p.lower())
                 for p in re.split(r"(\d+)", caminho))

def ultimos_posts(posts, quantidade=15, tipo=None):
    if tipo not in (None, "artigos", "aulas"):
        raise ValueError("Invalid publication type")
    candidates = [post for post in posts if post.get("date")
                  and Path(post["href"]).name != "index.html"
                  and not Path(post["href"]).name.startswith("guide-")
                  and not post["href"].endswith("-estatico.html")]
    if tipo is not None:
        candidates = [p for p in candidates
                      if p["href"].startswith("posts/courses/") == (tipo == "aulas")]
    return sorted(candidates, key=lambda p: (p["date"], _ordem_natural(p["href"])),
                  reverse=True)[:quantidade]

def _area(post):
    path = post["href"]
    if "/programming/ai/" in path:
        return "Artificial Intelligence"
    for pasta, nome in (("mathematics", "Mathematics"), ("statistics", "Statistics"),
                        ("physics", "Physics"), ("programming", "Programming"),
                        ("personal", "Personal Blog"), ("biographies", "Biographies")):
        if f"/{pasta}/" in path:
            return nome
    return "Blog"

def _lista(posts):
    if not posts:
        return "More reading is on the way."
    entries = []
    for post in posts:
        title = post["title"].replace("[", "\\[").replace("]", "\\]")
        published = date.fromisoformat(post["date"]).strftime("%d %b %Y")
        entries.append(f'- [{title}]({post["href"]})  \n'
                       f'  [{_area(post)}]{{.home-topic}} · [{published}]{{.home-date}}')
    return "\n\n".join(entries)

def atualizar():
    index = Path("index.qmd")
    content = index.read_text(encoding="utf-8")
    start, end = "<!-- inicio-ultimos-posts -->", "<!-- fim-ultimos-posts -->"
    if content.count(start) != 1 or content.count(end) != 1 or content.index(start) > content.index(end):
        raise ValueError("Latest-post markers are missing, duplicated, or reversed")
    posts = coletar_posts()
    if not ultimos_posts(posts):
        raise ValueError("No dated posts found; home preserved")
    articles = ultimos_posts(posts, quantidade=6, tipo="artigos")
    lessons = ultimos_posts(posts, quantidade=6, tipo="aulas")
    panels = ('::: {.home-updates}\n\n'
              '::: {.home-update-panel}\n\n'
              '### 📝 Recent articles {#recent-articles}\n\n'
              + _lista(articles) + '\n\n:::\n\n'
              '::: {.home-update-panel}\n\n'
              '### 🎓 New lessons {#new-lessons}\n\n'
              + _lista(lessons) + '\n\n:::\n\n:::\n')
    replacement = start + "\n" + panels + "\n" + end
    content = re.sub(re.escape(start) + r".*?" + re.escape(end), lambda _: replacement, content, flags=re.S)
    index.write_text(content, encoding="utf-8")
    print(f"Updated {len(articles)} articles and {len(lessons)} lessons")

if __name__ == "__main__":
    atualizar()
