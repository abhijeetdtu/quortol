from flask import Blueprint, request, jsonify
from ..models import Project, TechStack, project_techstack
from ..app import db

portfolio_bp = Blueprint('portfolio', __name__)

@portfolio_bp.route('/', methods=['GET'])
def get_projects():
    projects = Project.query.order_by(Project.published_at.desc()).all()
    return jsonify([
        {
            'id': project.id,
            'title': project.title,
            'slug': project.slug,
            'description': project.description,
            'image_url': project.image_url,
            'live_url': project.live_url,
            'repo_url': project.repo_url,
            'published_at': project.published_at.isoformat(),
            'techstacks': [
                {
                    'id': tech.id,
                    'name': tech.name,
                    'category': tech.category
                }
                for tech in project.techstacks
            ]
        }
        for project in projects
    ])

@portfolio_bp.route('/<slug>', methods=['GET'])
def get_project(slug):
    project = Project.query.filter_by(slug=slug).first_or_404()
    return jsonify({
        'id': project.id,
        'title': project.title,
        'slug': project.slug,
        'description': project.description,
        'long_description': project.long_description,
        'image_url': project.image_url,
        'live_url': project.live_url,
        'repo_url': project.repo_url,
        'published_at': project.published_at.isoformat(),
        'techstacks': [
            {
                'id': tech.id,
                'name': tech.name,
                'category': tech.category
            }
            for tech in project.techstacks
        ]
    })

@portfolio_bp.route('/techstacks', methods=['GET'])
def get_techstacks():
    techstacks = TechStack.query.all()
    return jsonify([
        {
            'id': tech.id,
            'name': tech.name,
            'category': tech.category
        }
        for tech in techstacks
    ])

@portfolio_bp.route('/create', methods=['POST'])
def create_project():
    data = request.get_json()
    
    if not data.get('title'):
        return jsonify({'error': 'Title required'}), 400
    
    # Generate slug from title
    slug = data['title'].lower().replace(' ', '-').replace('_', '-')
    
    # Check if slug already exists
    if Project.query.filter_by(slug=slug).first():
        slug = f"{slug}-{len(Project.query.filter(Project.slug.startswith(slug)).all())}"
    
    project = Project(
        title=data['title'],
        slug=slug,
        description=data.get('description', ''),
        long_description=data.get('long_description', ''),
        image_url=data.get('image_url', ''),
        live_url=data.get('live_url', ''),
        repo_url=data.get('repo_url', ''),
        published_at=db.func.now()
    )
    
    # Handle tech stacks
    if data.get('techstacks'):
        for tech_name in data['techstacks']:
            tech = TechStack.query.filter_by(name=tech_name).first()
            if not tech:
                # Extract category if provided (format: "name - category")
                if ' - ' in tech_name:
                    name, category = tech_name.split(' - ', 1)
                    tech = TechStack(name=name, category=category)
                else:
                    tech = TechStack(name=tech_name, category='general')
                db.session.add(tech)
            project.techstacks.append(tech)
    
    db.session.add(project)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'project': {
            'id': project.id,
            'slug': project.slug
        }
    }), 201
