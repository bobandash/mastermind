from flask import Blueprint, jsonify

auth_bp = Blueprint("auth_bp", __name__)


@auth_bp.route("/")
def index():
    return jsonify("hello")
