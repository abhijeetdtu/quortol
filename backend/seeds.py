from datetime import datetime
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
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _parse_tags(raw_tags):
    if not raw_tags:
        return []
    if raw_tags.startswith("[") and raw_tags.endswith("]"):
        raw_tags = raw_tags[1:-1]
    return [tag.strip() for tag in raw_tags.split(",") if tag.strip()]


def _parse_markdown_file(path):
    text = path.read_text(encoding="utf-8")
    metadata = {}
    body = text

    if text.startswith("---\n"):
        parts = text.split("---\n", 2)
        if len(parts) == 3:
            frontmatter = parts[1]
            body = parts[2]
            for line in frontmatter.splitlines():
                if ":" not in line:
                    continue
                key, value = line.split(":", 1)
                metadata[key.strip().lower()] = value.strip()

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
    published_at = _parse_datetime(metadata.get("published_at")) or datetime.utcnow()
    updated_at = _parse_datetime(metadata.get("updated_at")) or datetime.utcnow()

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
