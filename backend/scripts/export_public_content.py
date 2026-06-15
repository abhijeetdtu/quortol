from __future__ import annotations

import json
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.features.podcast.config import get_podcast_config
from backend.features.podcast.repository import load_podcast_episodes, serialize_podcast_for_export

BLOGS_DIR = PROJECT_ROOT / "backend" / "blogs"
SERIES_DIR = BLOGS_DIR / "series"
DB_CANDIDATES = [
    PROJECT_ROOT / "backend" / "instance" / "quortol.db",
    PROJECT_ROOT / "instance" / "quortol.db",
]


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", (value or "").strip().lower())
    return slug.strip("-")


def _iter_blog_markdown_files():
    top_level = BLOGS_DIR.glob("*.md")
    series_posts = SERIES_DIR.rglob("*.md") if SERIES_DIR.exists() else []
    return sorted([*top_level, *series_posts])


def _default_slug_for_path(path: Path) -> str:
    relative = path.relative_to(BLOGS_DIR)
    if relative.parent == Path("."):
        return _slugify(path.stem)
    without_suffix = relative.with_suffix("")
    return _slugify(str(without_suffix).replace("\\", "/"))


def _parse_datetime(value):
    if not value:
        return None
    raw = value.strip().strip('"').strip("'")
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(raw)
        if parsed.tzinfo is not None:
            return parsed.astimezone(timezone.utc).replace(tzinfo=None)
        return parsed
    except ValueError:
        pass

    for fmt in ("%Y-%m-%d", "%B %d, %Y", "%b %d, %Y", "%B %Y", "%b %Y"):
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue

    return None


def _parse_file_mtime(path: Path):
    try:
        return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).replace(tzinfo=None)
    except OSError:
        return None


def _extract_date_from_body(body: str):
    body_head = "\n".join(body.splitlines()[:40])
    candidates = [
        r"\*\*Date:\*\*\s*([A-Za-z]+\s+\d{1,2},\s+\d{4}|[A-Za-z]+\s+\d{4})",
        r"\*Published:\s*([A-Za-z]+\s+\d{1,2},\s+\d{4})\*",
        r"\*\s*By[^\n|]*\|\s*([A-Za-z]+\s+\d{1,2},\s+\d{4})\*",
    ]
    for pattern in candidates:
        match = re.search(pattern, body_head, flags=re.IGNORECASE)
        if not match:
            continue
        parsed = _parse_datetime(match.group(1))
        if parsed:
            return parsed

    return None


def _derive_excerpt(content: str, max_len: int = 220):
    for paragraph in content.split("\n\n"):
        cleaned = paragraph.strip()
        if not cleaned or cleaned == "---" or cleaned.startswith("#"):
            continue
        single_line = " ".join(cleaned.split())
        if len(single_line) <= max_len:
            return single_line
        return single_line[: max_len - 3].rstrip() + "..."
    return ""


def _parse_tags(raw_tags: str):
    if not raw_tags:
        return []
    if "\n" in raw_tags:
        return [
            line.strip().lstrip("-").strip().strip('"').strip("'")
            for line in raw_tags.splitlines()
            if line.strip().startswith("-")
        ]
    if raw_tags.startswith("[") and raw_tags.endswith("]"):
        raw_tags = raw_tags[1:-1]
    return [tag.strip().strip('"').strip("'") for tag in raw_tags.split(",") if tag.strip()]


def _extract_first_image_url(content: str):
    if not content:
        return ""

    markdown_match = re.search(r"!\[[^\]]*]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)", content)
    if markdown_match and markdown_match.group(1):
        return markdown_match.group(1)

    html_match = re.search(r"<img[^>]+src=[\"']([^\"']+)[\"']", content, flags=re.IGNORECASE)
    if html_match and html_match.group(1):
        return html_match.group(1)

    return ""


def _parse_markdown_file(path: Path):
    text = path.read_text(encoding="utf-8")
    metadata = {}
    body = text

    frontmatter_match = re.match(r"^---\s*\r?\n(.*?)\r?\n---\s*\r?\n?", text, flags=re.DOTALL)
    if frontmatter_match:
        frontmatter = frontmatter_match.group(1)
        body = text[frontmatter_match.end():]
        lines = frontmatter.splitlines()
        idx = 0
        while idx < len(lines):
            line = lines[idx]
            if ":" not in line:
                idx += 1
                continue
            key, value = line.split(":", 1)
            key = key.strip().lower()
            value = value.strip()
            if key == "tags" and value == "":
                list_lines = []
                idx += 1
                while idx < len(lines) and lines[idx].strip().startswith("-"):
                    list_lines.append(lines[idx].strip())
                    idx += 1
                metadata[key] = "\n".join(list_lines)
                continue
            metadata[key] = value
            idx += 1

    title = metadata.get("title")
    if not title:
        for line in body.splitlines():
            if line.startswith("# "):
                title = line[2:].strip()
                break
    if not title:
        title = path.stem.replace("-", " ").replace("_", " ").title()

    slug = metadata.get("slug") or _default_slug_for_path(path)
    excerpt = metadata.get("excerpt") or _derive_excerpt(body)
    tags = _parse_tags(metadata.get("tags", ""))
    published_at = (
        _parse_datetime(metadata.get("published_at"))
        or _parse_datetime(metadata.get("date"))
        or _extract_date_from_body(body)
        or _parse_file_mtime(path)
        or datetime.utcnow()
    )
    updated_at = _parse_datetime(metadata.get("updated_at")) or published_at
    featured_image = metadata.get("featured_image", "").strip().strip('"').strip("'")
    featured_image_caption = metadata.get("featured_image_caption", "").strip().strip('"').strip("'")

    if not featured_image:
        featured_image = _extract_first_image_url(body)

    return {
        "id": slug,
        "title": title,
        "slug": slug,
        "excerpt": excerpt,
        "content": body.strip(),
        "published_at": published_at.isoformat(),
        "updated_at": updated_at.isoformat(),
        "tags": [{"id": _slugify(tag), "name": tag, "slug": _slugify(tag)} for tag in tags],
        "featured_image": featured_image,
        "featured_image_caption": featured_image_caption,
    }


def _resolve_db_path():
    for candidate in DB_CANDIDATES:
        if candidate.exists():
            return candidate
    return None


def _load_projects():
    db_path = _resolve_db_path()
    if db_path is None:
        return []

    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row

    try:
        projects = connection.execute(
            """
            SELECT id, title, slug, description, long_description, image_url, live_url, repo_url, published_at
            FROM project
            ORDER BY published_at DESC
            """
        ).fetchall()

        tech_rows = connection.execute(
            """
            SELECT pts.project_id, ts.id, ts.name, ts.category
            FROM project_techstack AS pts
            JOIN tech_stack AS ts ON ts.id = pts.techstack_id
            ORDER BY ts.name ASC
            """
        ).fetchall()
    except sqlite3.DatabaseError:
        return []
    finally:
        connection.close()

    tech_by_project = {}
    for row in tech_rows:
        tech_by_project.setdefault(row["project_id"], []).append(
            {
                "id": row["id"],
                "name": row["name"],
                "category": row["category"],
            }
        )

    serialized = []
    for row in projects:
        serialized.append(
            {
                "id": row["id"],
                "title": row["title"],
                "slug": row["slug"],
                "description": row["description"] or "",
                "long_description": row["long_description"] or "",
                "image_url": row["image_url"] or "",
                "live_url": row["live_url"] or "",
                "repo_url": row["repo_url"] or "",
                "published_at": row["published_at"] or "",
                "techstacks": tech_by_project.get(row["id"], []),
            }
        )

    return serialized


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    podcast_config = get_podcast_config()
    payload = {
        "blogs": [_parse_markdown_file(path) for path in _iter_blog_markdown_files()],
        "projects": _load_projects(),
        "podcasts": [
            serialize_podcast_for_export(episode, config=podcast_config)
            for episode in load_podcast_episodes()
        ],
    }
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
