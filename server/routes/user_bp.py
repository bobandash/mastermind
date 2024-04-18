from flask import Blueprint, request, session, jsonify
from models.models import User, db

user_bp = Blueprint("user_bp", __name__)


@user_bp.route("/me", methods=["GET", "PATCH"])
def user_username_operations():
    user_id = session.get("user_id")
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "Unauthorized access"}), 401
    if request.method == "GET":
        if not user.username:
            # Return anonymous as the username if not found
            return jsonify({"username": "Anonymous"}), 200
        else:
            return jsonify({"username": user.username}), 200
    if request.method == "PATCH":
        new_username = request.args.get("username")
        if not new_username:
            return jsonify({"message": "You did not provide a new username"}), 400
        user.username = new_username
        db.session.commit()
        return (
            jsonify(
                {"message": "Successfully updated username", "username": new_username}
            ),
            200,
        )
