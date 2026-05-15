from datetime import datetime, timezone
from pathlib import Path
import re

from .models import BlogPost, Tag

BLOGS_DIR = Path(__file__).resolve().parent / "blogs"


def _slugify(value):
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower())
    return slug.strip("-")


def _derive_excerpt(content, max_len=220):
    for paragraph in content.split("\n\n"):
        cleaned = paragraph.strip()
        if not cleaned or cleaned.startswith("#"):
            continue
        single_line = " ".join(cleaned.split())
        if len(single_line) <= max_len:
            return single_line
        return single_line[: max_len - 3].rstrip() + "..."
    return ""


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


def _extract_date_from_body(body):
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


def _parse_file_mtime(path):
    try:
        return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).replace(tzinfo=None)
    except OSError:
        return None


def _parse_tags(raw_tags):
    if not raw_tags:
        return []
    # Handle YAML list style:
    # tags:
    #   - foo
    #   - bar
    if "\n" in raw_tags:
        return [
            line.strip().lstrip("-").strip().strip('"').strip("'")
            for line in raw_tags.splitlines()
            if line.strip().startswith("-")
        ]
    if raw_tags.startswith("[") and raw_tags.endswith("]"):
        raw_tags = raw_tags[1:-1]
    return [tag.strip().strip('"').strip("'") for tag in raw_tags.split(",") if tag.strip()]


def _parse_markdown_file(path):
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

    slug = metadata.get("slug") or _slugify(path.stem)
    excerpt = metadata.get("excerpt") or _derive_excerpt(body)
    tags = _parse_tags(metadata.get("tags", ""))
    parsed_published_at = (
        _parse_datetime(metadata.get("published_at"))
        or _parse_datetime(metadata.get("date"))
        or _extract_date_from_body(body)
    )
    file_mtime = _parse_file_mtime(path)
    published_at = parsed_published_at or file_mtime or datetime.utcnow()
    updated_at = _parse_datetime(metadata.get("updated_at")) or published_at

    return {
        "title": title,
        "slug": slug,
        "excerpt": excerpt,
        "content": body.strip(),
        "tags": tags,
        "published_at": published_at,
        "updated_at": updated_at,
    }


def seed_blog_posts_from_markdown(db):
    """
    Upsert blog posts from markdown files in backend/blogs.

    Supports simple frontmatter:
    ---
    title: My Post
    slug: my-post
    excerpt: Short summary
    tags: tag one, tag two
    published_at: 2026-05-05T09:00:00
    updated_at: 2026-05-05T09:00:00
    ---
    """
    BLOGS_DIR.mkdir(parents=True, exist_ok=True)

    markdown_files = sorted(BLOGS_DIR.glob("*.md"))
    for md_file in markdown_files:
        parsed = _parse_markdown_file(md_file)
        post = BlogPost.query.filter_by(slug=parsed["slug"]).first()
        if not post:
            post = BlogPost(slug=parsed["slug"])
            db.session.add(post)

        post.title = parsed["title"]
        post.content = parsed["content"]
        post.excerpt = parsed["excerpt"]
        post.published_at = parsed["published_at"]
        post.updated_at = parsed["updated_at"]

        post.tags.clear()
        for tag_name in parsed["tags"]:
            tag_slug = _slugify(tag_name)
            tag = Tag.query.filter_by(slug=tag_slug).first()
            if not tag:
                tag = Tag(name=tag_name, slug=tag_slug)
                db.session.add(tag)
            post.tags.append(tag)

    db.session.commit()
