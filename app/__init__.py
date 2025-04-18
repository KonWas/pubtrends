from flask import Flask


def create_app():
    app = Flask(__name__, static_folder='static')

    # Register blueprints
    from app.api.routes import api_bp
    from app.routes import main_bp

    app.register_blueprint(api_bp)
    app.register_blueprint(main_bp)

    return app