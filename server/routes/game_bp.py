from flask import Blueprint, request, jsonify
import requests
from models.models import Game, User, Difficulty, Round, db
from util.decorators import session_required
from util.enum import DifficultyEnum, StatusEnum
import json


game_bp = Blueprint("game_bp", __name__)


@game_bp.route("/", methods=["POST"])
@session_required
def create_new_game():
    # TODO: handle validation of these fields
    user = request.user
    difficulty_names = [member.name for member in DifficultyEnum]
    is_multiplayer, difficulty, max_turns, num_holes, num_colors = (
        request.args.get("is_multiplayer", type=bool),
        request.args.get("difficulty", type=str),
        request.args.get("max_turns", type=int),
        request.args.get("num_holes", type=int),
        request.args.get("num_colors", type=int),
    )
    if not all([is_multiplayer, difficulty]):
        return jsonify({"message": "Game settings must be provided."}), 400
    if difficulty not in difficulty_names:
        return jsonify({"message": "Difficulty is not valid."}), 400
    # TODO: Handle validation for num_holes and num_colors to make sure it's ok
    if difficulty == DifficultyEnum.CUSTOM.name and not all(
        [max_turns, num_holes, num_colors]
    ):
        return jsonify({"message": "Custom difficulty settings are not valid."}), 400

    # TODO: handle multiplayer functionality with sockets
    # TODO: handle custom functionality
    # Case: Single player functionality
    if is_multiplayer == False:
        if difficulty != DifficultyEnum.CUSTOM.name:
            # there is only one normal and hard in the database
            curr_difficulty = Difficulty.query.filter_by(mode=difficulty).first()
            num_holes, num_colors = (
                curr_difficulty.num_holes,
                curr_difficulty.num_colors,
            )
            params = {
                "num": num_holes,
                "min": 0,
                "max": num_colors - 1,
                "col": 1,
                "base": 10,
                "format": "plain",
            }
            # random code is in format 1\n2\n, etc
            random_code = (
                requests.get(f"https://www.random.org/clients/http/api", params).text
            ).split("\n")
            random_code = json.dumps(random_code)
            # Single player games are initialized with one round
            new_game = Game(
                is_multiplayer=is_multiplayer,
                difficulty=curr_difficulty,
                status=StatusEnum.IN_PROGRESS.name,
            )
            new_round = Round(
                game=new_game,
                status=StatusEnum.IN_PROGRESS,
                code_breaker=user,
                round_num=1,
                secret_code=random_code,
            )
            db.session.add(new_game)
            db.session.add(new_round)
            db.session.commit()
            return jsonify({"message": "Game has been successfully created"}), 200
        else:
            # TODO: custom difficulty
            return jsonify({"message": "TODO"}), 400
    # TODO multiplayer
    return jsonify({"message": "TODO"}), 400


# @game_bp.route("/<game_id>/rounds", methods=["POST"])
# @session_required
# def create_new_round(game_id):


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
