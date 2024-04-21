from flask import Flask, json
from dotenv import load_dotenv
from models.models import db
from flask_migrate import Migrate
from flask_session import Session
from routes import auth_bp, game_bp, round_bp, user_bp
from routes.auth_bp import bcrypt
from flask_cors import CORS
from flask import Blueprint
from werkzeug.exceptions import HTTPException
from util.json_errors import ErrorResponse


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

    # Generic Error handler so try, except is not needed for every route
    @app.errorhandler(HTTPException)
    def handle_exception(e):
        error_message = str(e)
        status_code = getattr(e, "code", 500)
        if status_code == 400:
            return ErrorResponse.bad_request(error_message)
        elif status_code == 401:
            return ErrorResponse.not_authorized(error_message)
        elif status_code == 404:
            return ErrorResponse.not_found(error_message)
        elif status_code == 500:
            return ErrorResponse.server_error(error_message)
        return ErrorResponse.unexpected_error(error_message, status_code)

    app.register_blueprint(auth_bp.auth_bp, url_prefix="/v1.0/auth")
    app.register_blueprint(user_bp.user_bp, url_prefix="/v1.0/users")
    app.register_blueprint(game_bp.game_bp, url_prefix="/v1.0/games")
    app.register_blueprint(round_bp.round_bp, url_prefix="/v1.0/rounds")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=8000)
