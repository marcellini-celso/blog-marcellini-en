import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import atualizar_ultimos_posts as home

class HomeUpdatesTests(unittest.TestCase):
    def test_sources_accept_yaml_dates_and_skip_drafts(self):
        with tempfile.TemporaryDirectory() as tmp:
            previous = Path.cwd()
            try:
                os.chdir(tmp)
                Path("posts").mkdir()
                for name, published, draft in [("a", '"2025-09-02"', "false"), ("b", "2025-09-03", "false"), ("c", "2025-09-04", "true")]:
                    Path(f"posts/{name}.qmd").write_text(f'---\ntitle: "Post {name}"\ndate: {published}\ndraft: {draft}\n---\nText')
                posts = home.coletar_posts()
                self.assertEqual([p["date"] for p in posts], ["2025-09-02", "2025-09-03"])
            finally:
                os.chdir(previous)

    def test_separates_articles_lessons_and_excludes_guides(self):
        posts = [{"title": "Test", "date": "2025-09-01", "href": path} for path in [
            "posts/physics/article.html", "posts/physics/guide-physics.html",
            "posts/physics/index.html", "posts/courses/mathematics/1.9.html",
            "posts/courses/mathematics/1.10.html"]]
        self.assertEqual([p["href"] for p in home.ultimos_posts(posts, tipo="artigos")], ["posts/physics/article.html"])
        self.assertTrue(home.ultimos_posts(posts, tipo="aulas")[0]["href"].endswith("1.10.html"))

    def test_refresh_keeps_both_panels_and_surrounding_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            previous = Path.cwd()
            try:
                os.chdir(tmp)
                Path("index.qmd").write_text("Before\n<!-- inicio-ultimos-posts -->\nOld\n<!-- fim-ultimos-posts -->\nAfter")
                posts = [{"title": "Article", "date": "2025-09-02", "href": "posts/physics/a.html"},
                         {"title": "Lesson", "date": "2025-09-03", "href": "posts/courses/mathematics/b.html"}]
                with patch.object(home, "coletar_posts", return_value=posts):
                    home.atualizar()
                result = Path("index.qmd").read_text()
                self.assertTrue(result.startswith("Before\n"))
                self.assertTrue(result.endswith("\nAfter"))
                self.assertEqual(result.count("{.home-update-panel}"), 2)
                self.assertIn("02 Sep 2025", result)
                self.assertIn("Recent articles", result)
                self.assertIn("New lessons", result)
            finally:
                os.chdir(previous)

if __name__ == "__main__":
    unittest.main()
