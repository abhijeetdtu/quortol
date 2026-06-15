from __future__ import annotations

from .blog_markdown import BLOGS_DIR, iter_blog_markdown_files, parse_markdown_file, slugify
from .models import BlogPost, Tag


def seed_blog_posts_from_markdown(db):
    """
    Upsert blog posts from markdown files in backend/blogs and backend/blogs/series.

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

    markdown_files = iter_blog_markdown_files()
    for md_file in markdown_files:
        parsed = parse_markdown_file(md_file)
        post = BlogPost.query.filter_by(slug=parsed.slug).first()
        if not post:
            post = BlogPost(slug=parsed.slug)
            db.session.add(post)

        post.title = parsed.title
        post.content = parsed.content
        post.excerpt = parsed.excerpt
        if post.published_at is None or parsed.has_explicit_published_at:
            post.published_at = parsed.published_at
        if post.updated_at is None or parsed.has_explicit_updated_at:
            post.updated_at = parsed.updated_at

        post.tags.clear()
        for tag_name in parsed.tags:
            tag_slug = slugify(tag_name)
            tag = Tag.query.filter_by(slug=tag_slug).first()
            if not tag:
                tag = Tag(name=tag_name, slug=tag_slug)
                db.session.add(tag)
            post.tags.append(tag)

    db.session.commit()
