from flask import Flask, jsonify
from pathlib import Path

try:
    from .extensions import db
except ImportError:
    # Support direct script execution where relative imports are unavailable.
    from backend.extensions import db

# Dash import for data storytelling
try:
    from dash import Dash, page_registry
except ImportError:
    Dash = None

def create_app(config_class=None, enable_dash=True):
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
    from .routes.agent import agent_bp
    from .routes.auth import auth_bp
    
    # Register short-form feed API blueprint
    from .features.short_form import create_short_form_blueprint
    short_form_bp = create_short_form_blueprint()
    app.register_blueprint(short_form_bp)

    from .features.podcast import create_podcast_blueprints
    podcast_api_bp, podcast_public_bp = create_podcast_blueprints()
    app.register_blueprint(podcast_api_bp)
    app.register_blueprint(podcast_public_bp)
    
    app.register_blueprint(blog_bp, url_prefix='/api/blog')
    app.register_blueprint(agent_bp, url_prefix='/api/agents')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    # Register Dash application
    dash_enabled = False
    dashboard_catalog = None
    if enable_dash and Dash is not None:
        try:
            from .dashboards import register_dashboards, serialize_dashboard_registry
            dash_assets_path = Path(__file__).resolve().parent / 'dashboards' / 'assets'
            dash_app = Dash(
                __name__,
                server=app,
                url_base_pathname='/data-storytelling-app/',
                use_pages=True,
                pages_folder="",
                assets_folder=str(dash_assets_path),
                suppress_callback_exceptions=True,
                external_stylesheets=[
                    "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css",
                ],
            )
            register_dashboards(dash_app)
            dashboard_catalog = serialize_dashboard_registry(page_registry)
            dash_enabled = True
        except Exception:
            app.logger.exception('Failed to initialize data storytelling Dash app')
    elif enable_dash:
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

    @app.get('/api/data-storytelling/dashboards')
    def data_storytelling_dashboards():
        if dashboard_catalog is None:
            return jsonify({
                'error': 'Data Storytelling is unavailable because Dash is not initialized.'
            }), 503
        return jsonify({'dashboards': dashboard_catalog})
    
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
