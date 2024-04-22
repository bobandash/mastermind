from flask import Blueprint, request, jsonify
from models.models import Game, Difficulty, Round, db, WaitingRoom
from util.decorators import session_required, check_user_in_game
from util.enum import DifficultyEnum, StatusEnum
from util.game_logic import get_random_secret_code
from util.json_errors import ErrorResponse
import json
from sqlalchemy.exc import SQLAlchemyError
import logging
import requests

game_bp = Blueprint("game_bp", __name__)


@game_bp.route("/", methods=["POST"])
@session_required
def create_new_game():
    if request.content_type != "application/json":
        return ErrorResponse.handle_error("Game settings were not provided.", 415)

    user = request.user
    data = request.get_json()
    difficulty_names = [member.name for member in DifficultyEnum]
    # all fields needed for single player
    is_multiplayer, difficulty, max_turns, num_holes, num_colors = (
        data.get("is_multiplayer"),
        data.get("difficulty"),
        data.get("max_turns"),
        data.get("num_holes"),
        data.get("num_colors"),
    )
    # fields specifically needed for multiplayer
    num_rounds, room_id = data.get("num_rounds"), data.get("room_id")

    if (
        not all(isinstance(value, int) for value in [max_turns, num_holes, num_colors])
        or difficulty not in difficulty_names
        or not isinstance(is_multiplayer, bool)
        or (
            is_multiplayer == True
            and not all(isinstance(value, int) for value in [num_rounds, room_id])
        )
    ):
        return ErrorResponse.handle_error(
            "A required field is missing or in an incorrect format.", 400
        )

    try:
        curr_difficulty = Difficulty.query.filter(
            Difficulty.max_turns == max_turns,
            Difficulty.mode == difficulty,
            Difficulty.num_holes == num_holes,
            Difficulty.num_colors == num_colors,
        ).first()
    except SQLAlchemyError as e:
        logging.error(f"Error fetching current difficulty: {str(e)}")
        return ErrorResponse.handle_error("Difficulty was not able to be fetched.", 503)

    if not curr_difficulty:
        return ErrorResponse.handle_error("Difficulty does not exist.", 404)

    if is_multiplayer == False:
        try:
            new_game = Game(
                is_multiplayer=is_multiplayer,
                difficulty=curr_difficulty,
                status=StatusEnum.NOT_STARTED.name,
                num_rounds=1,
            )
            new_game.players.append(user)
            db.session.add(new_game)
            db.session.commit()
            game_data = {
                "id": new_game.id,
                "is_multiplayer": is_multiplayer,
                "difficulty": curr_difficulty.mode.name,
                "players": [player.id for player in new_game.players],
                "created_at": new_game.created_at,
                "num_rounds": new_game.num_rounds,
            }
            return jsonify(game_data), 201
        except (SQLAlchemyError, ValueError) as e:
            db.session.rollback()
            logging.error(f"Error creating game: {str(e)}")
            return ErrorResponse.handle_error(
                "Game creation failed. Please check the provided data.",
                500,
            )
    else:
        try:
            waiting_room = WaitingRoom.query.get(room_id)
        except:
            return ErrorResponse.handle_error("Error fetching waiting room", 503)

        if not waiting_room:
            return ErrorResponse.handle_error("Waiting room not found", 404)

        if user.waiting_room_id != room_id:
            return ErrorResponse.handle_error("User is not inside waiting room", 400)

        if not user.is_host:
            return ErrorResponse.handle_error(
                "User is unauthorized to start the game", 401
            )

        if len(waiting_room.players) < 2:
            return ErrorResponse.handle_error(
                "Not enough players to start the game", 400
            )

        try:
            new_game = Game(
                is_multiplayer=True,
                difficulty=curr_difficulty,
                status=StatusEnum.NOT_STARTED.name,
                num_rounds=num_rounds,
            )
            for player in waiting_room.players:
                new_game.players.append(player)
            db.session.add(new_game)
            db.session.commit()
            game_data = {
                "id": new_game.id,
                "is_multiplayer": is_multiplayer,
                "difficulty": curr_difficulty.mode.name,
                "players": [player.id for player in new_game.players],
                "created_at": new_game.created_at,
                "num_rounds": new_game.num_rounds,
            }
            return jsonify(game_data), 201
        except (ValueError, SQLAlchemyError) as e:
            db.session.rollback()
            logging.error(f"Error creating game: {str(e)}")
            return ErrorResponse.handle_error(
                "Game creation failed. Please check the provided data.",
                500,
            )


# TODO: Code breaker should be allowed to view secret_code for ongoing round
@game_bp.route("/<game_id>", methods=["GET"])
@session_required
@check_user_in_game
def get_game_details(game_id):
    user = request.user
    game = request.game
    difficulty = game.difficulty

    return jsonify(
        {
            "id": game.id,
            "status": game.status.name,
            "difficulty": {
                "mode": difficulty.mode.name,
                "max_turns": difficulty.max_turns,
                "num_holes": difficulty.num_holes,
                "num_colors": difficulty.num_colors,
            },
            "rounds": [
                {
                    "id": round.id,
                    "status": round.status.name,
                    "code_breaker_id": round.code_breaker_id,
                    "round_num": round.round_num,
                    "points": round.points,
                    "secret_code": (
                        json.loads(round.secret_code)
                        if round.secret_code
                        and (
                            round.status == StatusEnum.COMPLETED
                            or (user.id != round.code_breaker_id)
                        )
                        # Rounds can only have two players max, so if the user isn't the code breaker, they are the code maker
                        else None
                    ),
                }
                for round in game.rounds
            ],
            "is_multiplayer": game.is_multiplayer,
        }
    )


@game_bp.route("/<game_id>/rounds", methods=["POST"])
@session_required
@check_user_in_game
def create_game_rounds(game_id):
    user = request.user
    game = request.game
    code_breaker_id = user.id
    round_num = 1
    if len(game.rounds) >= game.num_rounds:
        return ErrorResponse.handle_error(
            "Cannot create any more rounds. Game is on last round.", 400
        )

    if game.rounds and (
        game.rounds[-1].status == StatusEnum.IN_PROGRESS
        or game.rounds[-1].status == StatusEnum.NOT_STARTED
    ):
        return ErrorResponse.handle_error(
            "Cannot create a round. Previous round is still in progress.", 400
        )

    # Initially sets the first code breaker to be the host of the multiplayer game
    # Unless there are previous rounds, then go in sequential order
    if game.is_multiplayer and game.rounds and game.rounds[-1]:
        round_num = len(game.rounds) + 1
        prev_code_breaker = game.rounds[-1].code_breaker_id
        playerIds = [player.id for player in game.players]
        if code_breaker_id == prev_code_breaker:
            for playerId in playerIds:
                if code_breaker_id != playerId:
                    playerId = code_breaker_id
                    break

    num_holes, num_colors = game.difficulty.num_holes, game.difficulty.num_colors
    secret_code = None

    if not game.is_multiplayer:
        try:
            # Calls external API
            secret_code = get_random_secret_code(num_holes, num_colors)
        except requests.exceptions.RequestException as e:
            logging.error(f"Error generating computer's secret code: {str(e)}")
            return ErrorResponse.handle_error(
                f"Failed to generate computer's secret code.", 500
            )

    try:
        round = Round(
            game_id=game.id,
            status=(
                StatusEnum.IN_PROGRESS
                if not game.is_multiplayer
                else StatusEnum.NOT_STARTED
            ),
            code_breaker_id=code_breaker_id,
            round_num=round_num,
            secret_code=secret_code,
        )
        if game.status == StatusEnum.NOT_STARTED:
            game.status = StatusEnum.IN_PROGRESS
        db.session.add(round)
        db.session.commit()
    except (SQLAlchemyError, ValueError) as e:
        db.session.rollback()
        logging.error(f"Error creating round: {str(e)}")
        return ErrorResponse.handle_error(
            "Round creation failed. Please check the provided data.",
            500,
        )

    return (
        jsonify(
            {
                "id": round.id,
                "code_breaker_id": user.id,
                "round_num": 1,
                "status": round.status.name,
            }
        ),
        201,
    )


# Generates random secret code
@game_bp.route("/<game_id>/random-code", methods=["GET"])
@session_required
@check_user_in_game
def generate_secret_code(game_id):
    game = request.game
    num_holes, num_colors = game.difficulty.num_holes, game.difficulty.num_colors
    try:
        random_code = get_random_secret_code(num_holes, num_colors)
    except requests.exceptions.RequestException as e:
        logging.error(f"Error generating computer's secret code: {str(e)}")
        return ErrorResponse.handle_error(
            f"Failed to generate computer's secret code.", 500
        )

    return jsonify({"secret_code": random_code}), 200
