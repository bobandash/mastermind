from flask import Blueprint

user_bp = Blueprint("user_bp", __name__)


@user_bp.route("/")
def index():
    return user_bp("hello")
