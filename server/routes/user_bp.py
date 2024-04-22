from flask import Blueprint, request, session, jsonify
from models.models import User, db
from util.decorators import session_required
from util.json_errors import ErrorResponse
from sqlalchemy.exc import SQLAlchemyError
import logging

user_bp = Blueprint("user_bp", __name__)


@user_bp.route("/me", methods=["GET"])
@session_required
def get_user_details():
    user = request.user
    res_data = {
        "id": user.id,
        "username": user.username if user.username else "",
        "email": user.email if user.email else "",
        "is_host": user.is_host,
    }
    return jsonify(res_data), 200


@user_bp.route("/me/username", methods=["PATCH"])
@session_required
def change_username():
    if request.content_type != "application/json":
        return ErrorResponse.handle_error("Username was not provided.", 415)

    data = request.get_json()
    user = request.user
    new_username = data.get("username")
    if not new_username:
        return ErrorResponse.handle_error("Username was not provided.", 400)
    if len(new_username) > 20:
        return ErrorResponse.handle_error("Username cannot exceed 20 characters.", 400)
    try:
        user.username = new_username
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"Error updating username for user {user.id}: {str(e)}")
        return ErrorResponse.handle_error("Could not update username.", 503)

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
