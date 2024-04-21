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


@session_required
@room_bp.route("/", methods=["POST"])
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
                "players": [player.id for player in waiting_room.players],
            }
        )
    except (SQLAlchemyError, ValueError) as e:
        db.session.rollback()
        logging.error(f"Error creating new waiting room: {str(e)}")
        return ErrorResponse.handle_error(
            "Error creating new waiting room.",
            500,
        )
