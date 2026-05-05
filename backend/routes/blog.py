from flask import Blueprint, request, jsonify, render_template
from ..models import BlogPost, Tag, Category, post_tag
from ..app import db

blog_bp = Blueprint('blog', __name__)

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
            'tags': [tag.name for tag in post.tags]
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
        ]
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
