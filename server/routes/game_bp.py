from flask import Blueprint, request, jsonify
from models.models import Game, User, Difficulty, Round, db
from util.decorators import session_required, check_user_in_game
from util.enum import DifficultyEnum, StatusEnum
from util.code import get_random_secret_code

game_bp = Blueprint("game_bp", __name__)


@game_bp.route("/", methods=["POST"])
@session_required
def create_new_game():
    user = request.user
    try:
        data = request.get_json()
    except:
        return (
            jsonify({"message": "Game settings is not provided in correct format."}),
            415,
        )
    difficulty_names = [member.name for member in DifficultyEnum]
    is_multiplayer, difficulty, max_turns, num_holes, num_colors = (
        data.get("is_multiplayer"),
        data.get("difficulty"),
        data.get("max_turns"),
        data.get("num_holes"),
        data.get("num_colors"),
    )
    if is_multiplayer is None or difficulty is None:
        return jsonify({"message": "Game settings must be provided."}), 400
    if difficulty not in difficulty_names:
        return jsonify({"message": "Difficulty is not valid."}), 400
    if difficulty == DifficultyEnum.CUSTOM.name and not all(
        [max_turns, num_holes, num_colors]
    ):
        return jsonify({"message": "Custom difficulty settings are not valid."}), 400

    curr_difficulty = Difficulty.query.filter(
        Difficulty.max_turns == max_turns,
        Difficulty.mode == DifficultyEnum.CUSTOM.name,
        Difficulty.num_holes == num_holes,
        Difficulty.num_colors == num_colors,
    ).first()
    if not curr_difficulty:
        return jsonify({"message": "Custom difficulty does not exist"}), 400

    # Case: Single player functionality
    if is_multiplayer == False:
        try:
            new_game = Game(
                is_multiplayer=is_multiplayer,
                difficulty=curr_difficulty,
                status=StatusEnum.IN_PROGRESS.name,
            )
            new_game.players.append(user)
            db.session.add(new_game)
            db.session.commit()

            game_data = {
                "id": new_game.id,
                "is_multiplayer": is_multiplayer,
                "difficulty": curr_difficulty.mode.name,
                "players": [player.id for player in new_game.players],
            }
            return jsonify(game_data), 201
        except:
            return jsonify({"message": "Could not create game."}), 400

    # TODO handle multiplayer
    return jsonify({"message": "Did not handle multiplayer yet"}), 400


# TODO: Get game overview of all rounds, maybe to keep track of score in the future?
# @game_bp.route('/<game_id>/rounds', methods=["GET"])
# def get_and_create_game_rounds():


@game_bp.route("/<game_id>/rounds", methods=["POST"])
@session_required
@check_user_in_game
def create_game_rounds(game_id):
    user = request.user
    game = request.game
    if len(game.rounds) >= game.num_rounds:
        return (
            jsonify(
                {"message": "Cannot create any more rounds. Game is on last round."}
            ),
            400,
        )

    if game.rounds and game.rounds[-1].status == StatusEnum.IN_PROGRESS:
        return (
            jsonify(
                {
                    "message": "Cannot create a round. Previous round is still in progress."
                }
            ),
            400,
        )

    if game.is_multiplayer == False:
        num_holes, num_colors = game.difficulty.num_holes, game.difficulty.num_colors
        try:
            secret_code = get_random_secret_code(num_holes, num_colors)
        except:
            return (
                jsonify({"message": "Failed to generate computer's secret code."}),
                400,
            )
        new_round = Round(
            game_id=game.id,
            status=StatusEnum.IN_PROGRESS,
            code_breaker_id=user.id,
            round_num=1,
            secret_code=secret_code,
        )
        db.session.add(new_round)
        db.session.commit()
        round_data = {
            "id": new_round.id,
            "code_breaker_id": user.id,
            "round_num": 1,
        }
        return (
            jsonify(
                {"message": "Successfully created round.", "round_data": round_data}
            ),
            201,
        )
    else:
        # TODO: handle multiplayer
        data = request.get_json()
        secret_code = data.get("secret_code")
        if not secret_code:
            return jsonify({"message": "User did not provide secret code."}), 400
    return jsonify({"message": "Test"}), 200


# Generates random secret code
# TODO: If have time, add this functionality to the multiplayer game
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
        return jsonify({"message": "Error generating secret code"}), 500
