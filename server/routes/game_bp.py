from flask import Blueprint, request, jsonify
from models.models import Game, Difficulty, Round, db
from util.decorators import session_required, check_user_in_game
from util.enum import DifficultyEnum, StatusEnum
from util.code import get_random_secret_code
from util.json_errors import ErrorResponse
import json

game_bp = Blueprint("game_bp", __name__)


@game_bp.route("/", methods=["POST"])
@session_required
def create_new_game():
    user = request.user
    try:
        data = request.get_json()
    except:
        return ErrorResponse.bad_request("Game settings were not provided properly.")

    difficulty_names = [member.name for member in DifficultyEnum]
    is_multiplayer, difficulty, max_turns, num_holes, num_colors = (
        data.get("is_multiplayer"),
        data.get("difficulty"),
        data.get("max_turns"),
        data.get("num_holes"),
        data.get("num_colors"),
    )
    if (
        not all(
            value is not None
            for value in [is_multiplayer, difficulty, max_turns, num_holes, num_colors]
        )
        or difficulty not in difficulty_names
    ):
        return ErrorResponse.bad_request("A required field is missing or incorrect.")

    curr_difficulty = Difficulty.query.filter(
        Difficulty.max_turns == max_turns,
        Difficulty.mode == difficulty,
        Difficulty.num_holes == num_holes,
        Difficulty.num_colors == num_colors,
    ).first()

    if not curr_difficulty:
        return ErrorResponse.bad_request(
            "Cannot process the request because difficulty is missing."
        )

    # Case: Single player functionality
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
        except:
            return ErrorResponse.bad_request(
                "Game could not be created due to a format not matching the database."
            )
    # TODO Handle Multiplayer
    return jsonify({"message": "Did not handle multiplayer yet"}), 400


# TODO: handle multiplayer, code breaker should be allowed to view secret_code for ongoing round
@game_bp.route("/<game_id>", methods=["GET"])
@session_required
@check_user_in_game
def get_game_details(game_id):
    game = request.game
    difficulty = game.difficulty
    rounds_data = []
    for round in game.rounds:
        round_dict = {
            "id": round.id,
            "status": round.status.name,
            "code_breaker_id": round.code_breaker_id,
            "round_num": round.round_num,
            "points": round.points,
            "secret_code": json.loads(round.secret_code),
        }  # TODO: decide if want to include turns, for now there's no point
        if round.status == StatusEnum.IN_PROGRESS:
            round_dict["secret_code"] = None
        rounds_data.append(round_dict)

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
            "rounds": rounds_data,
        }
    )


@game_bp.route("/<game_id>/rounds", methods=["POST"])
@session_required
@check_user_in_game
def create_game_rounds(game_id):
    user = request.user
    game = request.game
    if len(game.rounds) >= game.num_rounds:
        return ErrorResponse.bad_request(
            "Cannot create any more rounds. Game is on last round."
        )

    if game.rounds and game.rounds[-1].status == StatusEnum.IN_PROGRESS:
        return ErrorResponse.bad_request(
            "Cannot create a round. Previous round is still in progress."
        )

    if game.is_multiplayer == False:
        num_holes, num_colors = game.difficulty.num_holes, game.difficulty.num_colors
        try:
            secret_code = get_random_secret_code(num_holes, num_colors)
        except:
            return ErrorResponse.bad_request(
                "Failed to generate computer's secret code."
            )

        new_round = Round(
            game_id=game.id,
            status=StatusEnum.IN_PROGRESS,
            code_breaker_id=user.id,
            round_num=1,
            secret_code=secret_code,
        )
        if game.status == StatusEnum.NOT_STARTED:
            game.status = StatusEnum.IN_PROGRESS
        db.session.add(new_round)
        db.session.commit()
        round_data = {
            "id": new_round.id,
            "code_breaker_id": user.id,
            "round_num": 1,
        }
        return (
            jsonify(round_data),
            201,
        )
    else:
        # TODO: handle multiplayer
        data = request.get_json()
        secret_code = data.get("secret_code")
        if not secret_code:
            return ErrorResponse.bad_request("User did not provide secret code.")
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
        return jsonify({"secret_code": random_code}), 200
    except:
        return ErrorResponse.server_error("Error generating secret code.")
