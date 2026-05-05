# Quortol Flask Application

def create_app():
    from .app import create_app as create_flask_app
    return create_flask_app()

if __name__ == '__main__':
    from .app import create_app
    app = create_app()
    app.run(debug=True)
