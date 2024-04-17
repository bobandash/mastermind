from flask import Blueprint

round_bp = Blueprint("round_bp", __name__)


@round_bp.route("/")
def index():
    return round_bp("hello")
