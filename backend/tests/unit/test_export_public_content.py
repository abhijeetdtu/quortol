from __future__ import annotations

import importlib.util
from pathlib import Path


MODULE_PATH = (
    Path(__file__).resolve().parents[2] / "scripts" / "export_public_content.py"
)
SPEC = importlib.util.spec_from_file_location("export_public_content", MODULE_PATH)
export_public_content = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(export_public_content)


def test_load_blogs_sorts_by_published_at_desc(monkeypatch):
    first = {"slug": "older", "published_at": "2026-05-01T00:00:00"}
    second = {"slug": "newer", "published_at": "2026-06-15T09:30:00"}
    third = {"slug": "middle", "published_at": "2026-05-20T12:00:00"}

    paths = [Path("b.md"), Path("a.md"), Path("c.md")]
    parsed_by_path = {
        paths[0]: first,
        paths[1]: second,
        paths[2]: third,
    }

    monkeypatch.setattr(export_public_content, "_iter_blog_markdown_files", lambda: paths)
    monkeypatch.setattr(
        export_public_content,
        "_parse_markdown_file",
        lambda path: parsed_by_path[path],
    )

    blogs = export_public_content._load_blogs()

    assert [blog["slug"] for blog in blogs] == ["newer", "middle", "older"]


def test_parse_markdown_file_includes_existing_audiobook(tmp_path, monkeypatch):
    blog_path = tmp_path / "recorded-post.md"
    blog_path.write_text("# Recorded Post\n\nContent.", encoding="utf-8")
    audiobook = tmp_path / "audiobooks" / "recorded-post" / "audiobook.wav"
    audiobook.parent.mkdir(parents=True)
    audiobook.write_bytes(b"RIFF")
    monkeypatch.setattr(export_public_content, "BLOGS_DIR", tmp_path)
    monkeypatch.setattr(export_public_content, "AUDIOBOOKS_DIR", tmp_path / "audiobooks")

    parsed = export_public_content._parse_markdown_file(blog_path)

    assert parsed["audio_url"] == "/static/audiobooks/recorded-post/audiobook.wav"


def test_parse_markdown_file_uses_null_audio_url_without_recording(tmp_path, monkeypatch):
    blog_path = tmp_path / "text-only.md"
    blog_path.write_text("# Text Only\n\nContent.", encoding="utf-8")
    monkeypatch.setattr(export_public_content, "BLOGS_DIR", tmp_path)
    monkeypatch.setattr(export_public_content, "AUDIOBOOKS_DIR", tmp_path / "audiobooks")

    parsed = export_public_content._parse_markdown_file(blog_path)

    assert parsed["audio_url"] is None
