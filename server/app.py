from flask import Flask, json
from dotenv import load_dotenv
from models.models import db
from flask_migrate import Migrate
from flask_session import Session
from routes import auth_bp, game_bp, round_bp, user_bp, room_bp
from routes.auth_bp import bcrypt
from flask_cors import CORS
from flask import Blueprint
from werkzeug.exceptions import HTTPException
from util.json_errors import ErrorResponse
from events import socketio


def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config.from_object("config.Config")
    CORS(app, supports_credentials=True)
    db.init_app(app)
    bcrypt.init_app(app)
    socketio.init_app(app)
    server_session = Session(app)
    migrate = Migrate(app, db)

    # Generic Error handler so try, except is not needed for every route
    @app.errorhandler(HTTPException)
    def handle_exception(e):
        error_message = str(e)
        status_code = getattr(e, "code", 500)
        return ErrorResponse.handle_error(error_message, status_code)

    app.register_blueprint(auth_bp.auth_bp, url_prefix="/v1.0/auth")
    app.register_blueprint(user_bp.user_bp, url_prefix="/v1.0/users")
    app.register_blueprint(game_bp.game_bp, url_prefix="/v1.0/games")
    app.register_blueprint(round_bp.round_bp, url_prefix="/v1.0/rounds")
    app.register_blueprint(room_bp.room_bp, url_prefix="/v1.0/rooms")
    return app, socketio


if __name__ == "__main__":
    app, socketio = create_app()
    socketio.run(app, debug=True)
