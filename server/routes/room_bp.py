from flask import Blueprint, request, jsonify
from string import ascii_uppercase
import random
from models.models import WaitingRoom, db
from sqlalchemy.exc import SQLAlchemyError
import logging
from util.json_errors import ErrorResponse
from util.decorators import session_required

room_bp = Blueprint("room_bp", __name__)


# Checks waiting room and generates unique code
def generate_unique_code(length):
    while True:
        code = ""
        for _ in range(length):
            code += random.choice(ascii_uppercase)
        try:
            waiting_room = WaitingRoom.query.filter_by(code=code).first()
            if not waiting_room:
                break
        except SQLAlchemyError as e:
            raise SQLAlchemyError("Rooms were not able to be fetched.")
    return code


@room_bp.route("/", methods=["POST"])
@session_required
def create_room():
    user = request.user
    try:
        code = generate_unique_code(6)
    except SQLAlchemyError as e:
        logging.error(f"Error fetching all waiting rooms: {str(e)}")
        return ErrorResponse.handle_error("Waiting rooms not able to be fetched.", 503)

    try:
        waiting_room = WaitingRoom(code=code)
        waiting_room.players.append(user)
    except (TypeError, ValueError):
        return ErrorResponse.handle_error(
            "Error creating new waiting room. Does not match format.", 400
        )
    try:
        db.session.add(waiting_room)
        db.session.commit()
        return jsonify(
            {
                "id": waiting_room.id,
                "code": waiting_room.code,
                "players": [
                    {"id": player.id, "username": player.username}
                    for player in waiting_room.players
                ],
            }
        )
    except (SQLAlchemyError, ValueError) as e:
        db.session.rollback()
        logging.error(f"Error creating new waiting room: {str(e)}")
        return ErrorResponse.handle_error(
            "Error creating new waiting room.",
            500,
        )


@room_bp.route("/join", methods=["POST"])
@session_required
def join_room():
    if request.content_type != "application/json":
        return ErrorResponse.handle_error("Username was not provided.", 415)
    user = request.user
    code = request.get_json().get("code")
    if not code:
        return ErrorResponse.handle_error("Code not provided.", 400)
    waiting_room = WaitingRoom.query.filter_by(code=code).first()
    if not waiting_room:
        return ErrorResponse.handle_error("Code is invalid.", 400)
    if len(waiting_room.players) >= 2:
        return ErrorResponse.handle_error(
            "Room is full.", 403
        )  # TODO; find more appropriate error code

    try:
        waiting_room.players.append(user)
        db.session.commit()
        return jsonify(
            {
                "id": waiting_room.id,
                "code": waiting_room.code,
                "players": [
                    {"id": player.id, "username": player.username}
                    for player in waiting_room.players
                ],
            }
        )
    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"Error creating new waiting room: {str(e)}")
        return ErrorResponse.handle_error(
            "Error creating new waiting room.",
            500,
        )


@room_bp.route("/<room_id>", methods=["GET"])
@session_required
def get_room_info(room_id):
    user = request.user
    try:
        waiting_room = WaitingRoom.query.get(room_id)
    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"Error getting waiting room: {str(e)}")
        return ErrorResponse.handle_error(
            "Error getting waiting room.",
            503,
        )

    player_ids = [player.id for player in waiting_room.players]
    if user.id not in player_ids:
        return ErrorResponse.handle_error("User is not a part of waiting room", 401)

    return (
        jsonify(
            {
                "id": waiting_room.id,
                "code": waiting_room.code,
                "players": [
                    {"id": player.id, "username": player.username}
                    for player in waiting_room.players
                ],
            }
        ),
        200,
    )
