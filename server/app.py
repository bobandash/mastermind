from flask import Flask
from dotenv import load_dotenv
from models.models import db
from flask_migrate import Migrate
from flask_session import Session
from routes import auth_bp, game_bp, round_bp, user_bp
from routes.auth_bp import bcrypt
from flask_cors import CORS
from flask import Blueprint


def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config.from_object("config.Config")
    CORS(app, supports_credentials=True)
    db.init_app(app)
    bcrypt.init_app(app)
    server_session = Session(app)
    migrate = Migrate(app, db)
    api_v1 = Blueprint("api_v1", __name__)
    app.register_blueprint(auth_bp.auth_bp, url_prefix="/v1.0/auth")
    app.register_blueprint(user_bp.user_bp, url_prefix="/v1.0/users")
    app.register_blueprint(game_bp.game_bp, url_prefix="/v1.0/games")
    app.register_blueprint(round_bp.round_bp, url_prefix="/v1.0/rounds")
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=8000)
