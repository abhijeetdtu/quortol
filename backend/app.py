from flask_sqlalchemy import SQLAlchemy
from flask import Flask

db = SQLAlchemy()

def create_app(config_class=None):
    if config_class is None:
        from .config import Config
        config_class = Config
    
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    from .auth import init_login_manager
    init_login_manager(app)
    
    # Register blueprints
    from .routes.blog import blog_bp
    from .routes.portfolio import portfolio_bp
    from .routes.agent import agent_bp
    from .routes.auth import auth_bp
    from .routes.pokhi_wikipedia import pokhi_wikipedia_bp
    app.register_blueprint(blog_bp, url_prefix='/api/blog')
    app.register_blueprint(portfolio_bp, url_prefix='/api/portfolio')
    app.register_blueprint(agent_bp, url_prefix='/api/agents')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(pokhi_wikipedia_bp, url_prefix='/api/pokhi/wikipedia')
    
    # Create database tables
    with app.app_context():
        db.create_all()
        from .seeds import seed_blog_posts_from_markdown
        seed_blog_posts_from_markdown(db)
    
    return app

if __name__ == '__main__':
    if __package__:
        app = create_app()
    else:
        import os
        import sys
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        from backend.app import create_app as package_create_app
        app = package_create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
