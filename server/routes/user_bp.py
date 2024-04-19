from flask import Blueprint, request, session, jsonify
from models.models import User, db
from util.decorators import session_required

user_bp = Blueprint("user_bp", __name__)


# TODO: add stats
@user_bp.route("/me", methods=["GET"])
@session_required
def get_user_details():
    user = request.user
    if request.method == "GET":
        if not user.username:
            # Return anonymous as the username if not found
            return jsonify({"id": user.id, "username": ""}), 200
        else:
            return jsonify({"id": user.id, "username": user.username}), 200


@user_bp.route("/me", methods=["PATCH"])
@session_required
def change_username():
    user = request.user
    data = request.get_json()
    new_username = data.get("username")
    if not new_username:
        return jsonify({"message": "Username was not provided"}), 400
    if len(new_username) > 20:
        return (
            jsonify(
                {
                    "error": {
                        "code": "badRequest",
                        "message": "Username cannot exceed 20 characters.",
                    }
                }
            ),
            400,
        )
    user.username = new_username
    db.session.commit()
    return (
        jsonify(
            {
                "id": user.id,
                "message": "Successfully updated username",
                "username": new_username,
            }
        ),
        200,
    )
