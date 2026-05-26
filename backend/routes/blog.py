from pathlib import Path
import re

from flask import Blueprint, request, jsonify, abort, send_from_directory
from ..models import BlogPost, Tag, Category
from ..extensions import db

blog_bp = Blueprint('blog', __name__)
BLOG_IMAGES_DIR = (Path(__file__).resolve().parent.parent / 'blogs' / 'images').resolve()
BLOGS_DIR = (Path(__file__).resolve().parent.parent / 'blogs').resolve()
SERIES_DIR = BLOGS_DIR / 'series'
_FEATURED_IMAGE_CACHE = {
    'signature': None,
    'by_slug': {}
}


def _slugify(value):
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", (value or '').strip().lower())
    return slug.strip("-")


def _iter_blog_markdown_files():
    top_level = BLOGS_DIR.glob("*.md")
    series_posts = SERIES_DIR.rglob("*.md") if SERIES_DIR.exists() else []
    return sorted([*top_level, *series_posts])


def _default_slug_for_path(path):
    relative = path.relative_to(BLOGS_DIR)
    if relative.parent == Path('.'):
        return _slugify(path.stem)
    without_suffix = relative.with_suffix('')
    return _slugify(str(without_suffix).replace('\\', '/'))


def _blog_files_signature():
    files = _iter_blog_markdown_files()
    return tuple(
        (path.name, path.stat().st_mtime_ns, path.stat().st_size)
        for path in files
    )


def _parse_frontmatter(path):
    try:
        text = path.read_text(encoding='utf-8')
    except OSError:
        return {}

    frontmatter_match = re.match(r"^---\s*\r?\n(.*?)\r?\n---\s*\r?\n?", text, flags=re.DOTALL)
    if not frontmatter_match:
        return {}

    metadata = {}
    for raw_line in frontmatter_match.group(1).splitlines():
        if ":" not in raw_line:
            continue
        key, value = raw_line.split(":", 1)
        metadata[key.strip().lower()] = value.strip().strip('"').strip("'")

    return metadata


def _featured_image_index():
    signature = _blog_files_signature()
    if _FEATURED_IMAGE_CACHE['signature'] == signature:
        return _FEATURED_IMAGE_CACHE['by_slug']

    by_slug = {}
    for md_file in _iter_blog_markdown_files():
        metadata = _parse_frontmatter(md_file)
        slug = metadata.get('slug') or _default_slug_for_path(md_file)
        if not slug:
            continue
        by_slug[slug] = {
            'featured_image': metadata.get('featured_image', ''),
            'featured_image_caption': metadata.get('featured_image_caption', ''),
        }

    _FEATURED_IMAGE_CACHE['signature'] = signature
    _FEATURED_IMAGE_CACHE['by_slug'] = by_slug
    return by_slug


def _featured_fields_for_slug(slug):
    data = _featured_image_index().get(slug, {})
    return {
        'featured_image': data.get('featured_image', ''),
        'featured_image_caption': data.get('featured_image_caption', ''),
    }


def _extract_first_image_url(content):
    if not content:
        return ''

    markdown_match = re.search(r"!\[[^\]]*]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)", content)
    if markdown_match and markdown_match.group(1):
        return markdown_match.group(1)

    html_match = re.search(r"<img[^>]+src=[\"']([^\"']+)[\"']", content, flags=re.IGNORECASE)
    if html_match and html_match.group(1):
        return html_match.group(1)

    return ''


def _image_fields_for_post(post):
    image_fields = _featured_fields_for_slug(post.slug)
    if not image_fields['featured_image']:
        image_fields['featured_image'] = _extract_first_image_url(post.content)
    return image_fields

@blog_bp.route('/', methods=['GET'])
def get_posts():
    posts = BlogPost.query.order_by(BlogPost.published_at.desc()).all()
    return jsonify([
        {
            'id': post.id,
            'title': post.title,
            'slug': post.slug,
            'excerpt': post.excerpt,
            'published_at': post.published_at.isoformat(),
            'tags': [tag.name for tag in post.tags],
            **_image_fields_for_post(post),
        }
        for post in posts
    ])

@blog_bp.route('/<slug>', methods=['GET'])
def get_post(slug):
    post = BlogPost.query.filter_by(slug=slug).first_or_404()
    return jsonify({
        'id': post.id,
        'title': post.title,
        'slug': post.slug,
        'content': post.content,
        'excerpt': post.excerpt,
        'published_at': post.published_at.isoformat(),
        'updated_at': post.updated_at.isoformat(),
        'tags': [
            {
                'id': tag.id,
                'name': tag.name,
                'slug': tag.slug
            }
            for tag in post.tags
        ],
        **_image_fields_for_post(post),
    })

@blog_bp.route('/tags', methods=['GET'])
def get_tags():
    tags = Tag.query.all()
    return jsonify([
        {
            'id': tag.id,
            'name': tag.name,
            'slug': tag.slug
        }
        for tag in tags
    ])

@blog_bp.route('/categories', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    return jsonify([
        {
            'id': category.id,
            'name': category.name,
            'slug': category.slug
        }
        for category in categories
    ])

@blog_bp.route('/images/<path:filename>', methods=['GET'])
def get_blog_image(filename):
    normalized = (filename or '').replace('\\', '/')
    if not normalized or normalized.startswith('/'):
        abort(404)

    parts = [part for part in normalized.split('/') if part not in ('', '.')]
    if not parts or any(part == '..' for part in parts):
        abort(404)

    candidate = (BLOG_IMAGES_DIR / Path(*parts)).resolve()
    if BLOG_IMAGES_DIR not in candidate.parents:
        abort(404)

    if not candidate.is_file():
        abort(404)

    relative_path = candidate.relative_to(BLOG_IMAGES_DIR)
    return send_from_directory(BLOG_IMAGES_DIR, str(relative_path).replace('\\', '/'))

@blog_bp.route('/create', methods=['POST'])
def create_post():
    data = request.get_json()
    
    if not all([data.get('title'), data.get('content')]):
        return jsonify({'error': 'Title and content required'}), 400
    
    # Generate slug from title
    slug = data['title'].lower().replace(' ', '-').replace('_', '-')
    
    # Check if slug already exists
    if BlogPost.query.filter_by(slug=slug).first():
        slug = f"{slug}-{len(BlogPost.query.filter(BlogPost.slug.startswith(slug)).all())}"
    
    post = BlogPost(
        title=data['title'],
        slug=slug,
        content=data['content'],
        excerpt=data.get('excerpt', ''),
        published_at=db.func.now(),
        updated_at=db.func.now()
    )
    
    # Handle tags
    if data.get('tags'):
        for tag_name in data['tags']:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name, slug=tag_name.lower().replace(' ', '-'))
                db.session.add(tag)
            post.tags.append(tag)
    
    db.session.add(post)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'post': {
            'id': post.id,
            'slug': post.slug
        }
    }), 201
