from flask import Blueprint, request, jsonify
from models.models import Game, Difficulty, Round, db
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
    is_multiplayer, difficulty, max_turns, num_holes, num_colors = (
        data.get("is_multiplayer"),
        data.get("difficulty"),
        data.get("max_turns"),
        data.get("num_holes"),
        data.get("num_colors"),
    )

    if (
        not all(isinstance(value, int) for value in [max_turns, num_holes, num_colors])
        or difficulty not in difficulty_names
        or not isinstance(is_multiplayer, bool)
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
            }
            return jsonify(game_data), 201
        except (SQLAlchemyError, ValueError) as e:
            db.session.rollback()
            logging.error(f"Error creating game: {str(e)}")
            return ErrorResponse.handle_error(
                "Game creation failed. Please check the provided data.",
                500,
            )
    # TODO: handle multiplayer when creating game
    return ErrorResponse.handle_error(
        "Multiplayer mode has not been created yet.",
        400,
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
                        if round.status == StatusEnum.COMPLETED
                        or (user.id != round.code_breaker_id)
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
    if len(game.rounds) >= game.num_rounds:
        return ErrorResponse.handle_error(
            "Cannot create any more rounds. Game is on last round.", 400
        )

    if game.rounds and game.rounds[-1].status == StatusEnum.IN_PROGRESS:
        return ErrorResponse.handle_error(
            "Cannot create a round. Previous round is still in progress.", 400
        )

    if game.is_multiplayer == False:
        num_holes, num_colors = game.difficulty.num_holes, game.difficulty.num_colors
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
                status=StatusEnum.IN_PROGRESS,
                code_breaker_id=user.id,
                round_num=1,
                secret_code=secret_code,
            )
            if game.status == StatusEnum.NOT_STARTED:
                game.status = StatusEnum.IN_PROGRESS
            db.session.add(round)
            db.session.commit()
        except (SQLAlchemyError, ValueError) as e:
            db.session.rollback()
            logging.error(f"Error creating game: {str(e)}")
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
                }
            ),
            201,
        )
    else:
        # TODO: handle multiplayer
        data = request.get_json()
        secret_code = data.get("secret_code")
        if not secret_code:
            return ErrorResponse.handle_error("User did not provide secret code.", 400)
    return jsonify({"message": "Test"}), 200


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
