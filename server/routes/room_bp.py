from flask import Blueprint, request, jsonify
from string import ascii_uppercase
import random
from models.models import WaitingRoom, Difficulty, db
from sqlalchemy.exc import SQLAlchemyError
import logging
from util.json_errors import ErrorResponse
from util.decorators import session_required, check_user_in_waiting_room
from util.enum import DifficultyEnum

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
        normal_difficulty = Difficulty.query.filter_by(
            mode=DifficultyEnum.NORMAL
        ).first()
    except SQLAlchemyError as e:
        logging.error(f"Error fetching normal difficulty {str(e)}")
        return ErrorResponse.handle_error(
            "Normal difficulty not able to be fetched.", 503
        )

    try:
        waiting_room = WaitingRoom(
            code=code, difficulty=normal_difficulty, num_rounds=2
        )
        waiting_room.players.append(user)
        user.is_host = True
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
                    {
                        "id": player.id,
                        "username": player.username,
                        "is_host": player.is_host,
                    }
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
        return ErrorResponse.handle_error("Room is full.", 403)

    # User joins a waiting room that they already are in
    player_ids_in_room = [player.id for player in waiting_room.players]
    if user.id in player_ids_in_room:
        return jsonify(
            {
                "id": waiting_room.id,
                "code": waiting_room.code,
                "players": [
                    {
                        "id": player.id,
                        "username": player.username,
                        "is_host": player.is_host,
                    }
                    for player in waiting_room.players
                ],
            }
        )

    try:
        user.is_host = (
            False  # the person joining a pre-existing waiting room cannot be a host
        )
        waiting_room.players.append(user)
        db.session.commit()
        return jsonify(
            {
                "id": waiting_room.id,
                "code": waiting_room.code,
                "players": [
                    {
                        "id": player.id,
                        "username": player.username,
                        "is_host": player.is_host,
                    }
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
@check_user_in_waiting_room
def get_room_info(room_id):
    waiting_room = request.waiting_room
    difficulty = waiting_room.difficulty
    return (
        jsonify(
            {
                "id": waiting_room.id,
                "code": waiting_room.code,
                "players": [
                    {
                        "id": player.id,
                        "username": player.username,
                        "is_host": player.is_host,
                    }
                    for player in waiting_room.players
                ],
                "difficulty": {
                    "id": difficulty.id,
                    "mode": difficulty.mode.name,
                    "max_turns": difficulty.max_turns,
                    "num_holes": difficulty.num_holes,
                    "num_colors": difficulty.num_colors,
                },
                "num_rounds": waiting_room.num_rounds,
            }
        ),
        200,
    )


@room_bp.route("/<room_id>", methods=["PATCH"])
@session_required
@check_user_in_waiting_room
def update_game_settings(room_id):
    user = request.user
    waiting_room = request.waiting_room
    is_host = user.is_host
    if request.content_type != "application/json":
        return ErrorResponse.handle_error("Game settings were not provided.", 415)
    if not is_host:
        return ErrorResponse.handle_error("Unauthorized access.", 401)

    data = request.get_json()
    difficulty, max_turns, num_holes, num_colors, rounds = (
        data.get("difficulty"),
        data.get("max_turns"),
        data.get("num_holes"),
        data.get("num_colors"),
        data.get("rounds"),
    )

    difficulty_names = [member.name for member in DifficultyEnum]
    if difficulty not in difficulty_names:
        return ErrorResponse.handle_error("Difficulty is not valid.", 400)

    if not rounds or (rounds and rounds not in [2, 4, 6]):
        return ErrorResponse.handle_error("Rounds are not valid", 400)

    if not all(isinstance(x, int) for x in [max_turns, num_holes, num_colors]):
        return ErrorResponse.handle_error("Round settings are not valid.", 400)

    # Check if difficulty exists
    try:
        curr_difficulty = Difficulty.query.filter(
            Difficulty.max_turns == max_turns,
            Difficulty.mode == difficulty,
            Difficulty.num_holes == num_holes,
            Difficulty.num_colors == num_colors,
        ).first()
        if not curr_difficulty:
            return ErrorResponse.handle_error("Difficulty is not valid.", 400)
    except SQLAlchemyError as e:
        return ErrorResponse.handle_error("Error fetching difficulty", 503)

    try:
        waiting_room.difficulty = curr_difficulty
        waiting_room.num_rounds = rounds
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"Error updating the waiting room settings: {str(e)}")
        return ErrorResponse.handle_error(
            "Error updating the waiting room settings", 503
        )

    return (
        jsonify(
            {
                "id": waiting_room.id,
                "num_rounds": waiting_room.num_rounds,
                "difficulty": {
                    "id": curr_difficulty.id,
                    "mode": curr_difficulty.mode.name,
                    "max_turns": curr_difficulty.max_turns,
                    "num_holes": curr_difficulty.num_holes,
                    "num_colors": curr_difficulty.num_colors,
                },
            }
        ),
        200,
    )
