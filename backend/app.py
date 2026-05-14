from flask import Flask
from pathlib import Path

try:
    from .extensions import db
except ImportError:
    # Support direct script execution where relative imports are unavailable.
    from backend.extensions import db

# Dash import for data storytelling
try:
    from dash import Dash
except ImportError:
    Dash = None

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
    
    # Register Dash application
    dash_enabled = False
    if Dash is not None:
        try:
            from .dashboards import register_dashboards
            dash_assets_path = Path(__file__).resolve().parent / 'dashboards' / 'assets'
            dash_app = Dash(
                __name__,
                server=app,
                url_base_pathname='/data-storytelling-app/',
                use_pages=True,
                pages_folder="",
                assets_folder=str(dash_assets_path),
                suppress_callback_exceptions=True
            )
            register_dashboards(dash_app)
            dash_enabled = True
        except Exception:
            app.logger.exception('Failed to initialize data storytelling Dash app')
    else:
        app.logger.warning('Dash is not installed; data storytelling app was not initialized.')

    if not dash_enabled:
        @app.route('/data-storytelling-app/')
        @app.route('/data-storytelling-app/<path:_path>')
        def data_storytelling_unavailable(_path=''):
            return (
                'Data Storytelling is unavailable because Dash is not initialized. '
                'Install backend dependencies and restart the backend server.',
                503
            )
    
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
