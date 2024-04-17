from flask import Blueprint

game_bp = Blueprint("game_bp", __name__)


@game_bp.route("/")
def index():
    return game_bp("hello")
