from flask import Blueprint, request, jsonify
import requests
from models.models import Game, User, Difficulty, Round, db
from util.decorators import session_required, user_inside_game
from util.enum import DifficultyEnum, StatusEnum
import json


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

    # Case: Single player functionality
    if is_multiplayer == False:
        if difficulty != DifficultyEnum.CUSTOM.name:
            # there should be only one NORMAL and HARD in the database
            curr_difficulty = Difficulty.query.filter_by(mode=difficulty).first()
            num_holes, num_colors = (
                curr_difficulty.num_holes,
                curr_difficulty.num_colors,
            )
        else:
            curr_difficulty = Difficulty.query.filter(
                Difficulty.max_turns == max_turns,
                Difficulty.mode == DifficultyEnum.CUSTOM.name,
                Difficulty.num_holes == num_holes,
                Difficulty.num_colors == num_colors,
            ).first()
            if not curr_difficulty:
                return jsonify({"message": "Custom difficulty does not exist"}), 400

        new_game = Game(
            is_multiplayer=is_multiplayer,
            difficulty=curr_difficulty.id,
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

    # TODO handle multiplayer
    return jsonify({"message": "Did not handle multiplayer yet"}), 400


# Generates random secret code
# TODO: If have time, add this functionality to the multiplayer game
@game_bp.route("/<game_id>/random-code", methods=["GET"])
@session_required
def generate_secret_code(game_id):
    user = request.user
    game = Game.query.get(game_id)
    if not game:
        return jsonify({"message": "Game does not exist."}), 400
    if user not in game.players:
        return jsonify({"message": "User is in not in game."}), 400
    num_holes, num_colors = game.difficulty.num_holes, game.difficulty.num_colors
    try:
        params = {
            "num": num_holes,
            "min": 0,
            "max": num_colors - 1,
            "col": 1,
            "base": 10,
            "format": "plain",
        }
        random_code = requests.get(
            "https://www.random.org/integers", params=params
        ).text.split("\n")[:-1]
        int_random_code = json.dumps(list(map(int, random_code)))
        return jsonify({"secret_code": int_random_code}), 200
    except:
        return jsonify({"message": "Error generating secret code"}), 500
