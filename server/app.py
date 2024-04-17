from flask import Flask
from dotenv import load_dotenv
from models.models import db
from flask_migrate import Migrate
from routes import auth_bp, game_bp, round_bp, user_bp

# TODO: for the mvp, will implement with JWT Token to save time; look into Redis and session tokens (not huge priority)


def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config.from_object("config.Config")
    db.init_app(app)
    migrate = Migrate(app, db)
    app.register_blueprint(auth_bp.auth_bp, url_prefix="/auth")
    app.register_blueprint(user_bp.user_bp, url_prefix="/users")
    app.register_blueprint(game_bp.game_bp, url_prefix="/games")
    app.register_blueprint(round_bp.round_bp, url_prefix="/rounds")
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=8000)
