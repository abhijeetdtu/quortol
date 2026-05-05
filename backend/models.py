from .extensions import db
from flask_login import UserMixin
from .auth import UserMixin as AuthUserMixin
from datetime import datetime

class User(UserMixin, AuthUserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(100), unique=True)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    agents = db.relationship('Agent', secondary='user_agent_access', back_populates='users')

class Agent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.Text)
    endpoint_url = db.Column(db.String(500))  # External agent API
    status = db.Column(db.String(20))  # active, inactive, maintenance
    capabilities = db.Column(db.JSON)  # List of capability names
    
    # Relationships
    users = db.relationship('User', secondary='user_agent_access', back_populates='agents')

# Association table for user-agent access
user_agent_access = db.Table('user_agent_access',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('agent_id', db.Integer, db.ForeignKey('agent.id'), primary_key=True)
)

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    slug = db.Column(db.String(200), unique=True)
    content = db.Column(db.Text)  # Markdown or plain text
    excerpt = db.Column(db.Text)
    published_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    
    # Relationships
    tags = db.relationship('Tag', secondary='post_tag', backref='posts')

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    slug = db.Column(db.String(100), unique=True)

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    slug = db.Column(db.String(100))

# Many-to-many relationship for posts and tags
post_tag = db.Table('post_tag',
    db.Column('post_id', db.Integer, db.ForeignKey('blog_post.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    slug = db.Column(db.String(200), unique=True)
    description = db.Column(db.Text)
    long_description = db.Column(db.Text)
    image_url = db.Column(db.String(500))
    live_url = db.Column(db.String(500))
    repo_url = db.Column(db.String(500))
    published_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    techstacks = db.relationship('TechStack', secondary='project_techstack', backref='projects')

class TechStack(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    category = db.Column(db.String(100))  # frontend, backend, database, etc.

# Many-to-many relationship for projects and techstacks
project_techstack = db.Table('project_techstack',
    db.Column('project_id', db.Integer, db.ForeignKey('project.id'), primary_key=True),
    db.Column('techstack_id', db.Integer, db.ForeignKey('tech_stack.id'), primary_key=True)
)
