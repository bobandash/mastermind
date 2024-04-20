from flask import Blueprint, request, session, jsonify
from models.models import User, db
from util.decorators import session_required
from util.json_errors import ErrorResponse

user_bp = Blueprint("user_bp", __name__)


# TODO: Add Stats
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
        return ErrorResponse.bad_request("Username was not provided.")
    if len(new_username) > 20:
        return ErrorResponse.bad_request("Username cannot exceed 20 characters.")
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
