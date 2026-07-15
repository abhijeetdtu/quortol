from __future__ import annotations

from pathlib import Path

from backend.blog_markdown import (
    default_slug_for_path,
    iter_blog_markdown_files,
    markdown_to_spoken_text,
    parse_markdown_file,
)


def test_iter_blog_markdown_files_includes_top_level_and_series(tmp_path):
    blogs_dir = tmp_path / "blogs"
    series_dir = blogs_dir / "series" / "history"
    blogs_dir.mkdir()
    series_dir.mkdir(parents=True)
    top_level = blogs_dir / "alpha-post.md"
    nested = series_dir / "beta-post.md"
    top_level.write_text("# Alpha", encoding="utf-8")
    nested.write_text("# Beta", encoding="utf-8")

    files = iter_blog_markdown_files(blogs_dir=blogs_dir)

    assert files == [top_level, nested]


def test_parse_markdown_file_uses_shared_slug_rules_for_nested_posts(tmp_path):
    blogs_dir = tmp_path / "blogs"
    series_dir = blogs_dir / "series" / "deep-dives"
    series_dir.mkdir(parents=True)
    post_path = series_dir / "india-politics.md"
    post_path.write_text(
        "---\n"
        "title: Political Currents\n"
        "tags:\n"
        "  - politics\n"
        "  - india\n"
        "---\n\n"
        "# Ignored heading\n\n"
        "Opening paragraph.",
        encoding="utf-8",
    )

    parsed = parse_markdown_file(post_path, blogs_dir=blogs_dir)

    assert parsed.title == "Political Currents"
    assert parsed.slug == default_slug_for_path(post_path, blogs_dir=blogs_dir)
    assert parsed.tags == ["politics", "india"]
    assert parsed.excerpt == "Opening paragraph."


def test_markdown_to_spoken_text_strips_code_urls_and_flattens_tables():
    markdown = """
# Headline

Visit https://example.com for more.

![Chart](chart.png)

```python
print("hello")
```

| Year | Value |
| ---- | ----- |
| 2024 | 12 |

- first point
1. second point
"""

    spoken = markdown_to_spoken_text(markdown)

    assert "https://example.com" not in spoken
    assert "chart.png" not in spoken
    assert "Code example omitted." in spoken
    assert "Section: Headline" in spoken
    assert "Table: Year, Value ; 2024, 12" in spoken
    assert "- first point" in spoken
    assert "- second point" in spoken


def test_markdown_to_spoken_text_removes_inline_source_citations_but_keeps_prose_links():
    markdown = """
Claim supported by archives [Source One](https://example.com/source-one); [Source Two](https://example.com/source-two).

This [linked phrase](https://example.com/phrase) remains part of the spoken sentence.
"""

    spoken = markdown_to_spoken_text(markdown)

    assert "Source One" not in spoken
    assert "Source Two" not in spoken
    assert "Claim supported by archives." in spoken
    assert "linked phrase remains part of the spoken sentence." in spoken


def test_markdown_to_spoken_text_removes_image_lines_and_standalone_italic_captions():
    markdown = """
Before image.

![Dust Bowl refugees camped alongside the highway near Bakersfield, California, November 1935 — the road as both escape route and destination.](dustbowl.jpg)
*Along the highway near Bakersfield, California. Dorothea Lange, 1935. Farm Security Administration, Library of Congress. Public domain.*

After image.
"""

    spoken = markdown_to_spoken_text(markdown)

    assert "Dust Bowl refugees camped alongside" not in spoken
    assert "Dorothea Lange" not in spoken
    assert "Before image." in spoken
    assert "After image." in spoken
