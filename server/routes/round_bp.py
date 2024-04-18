from flask import Blueprint
from functools import wraps
from models.models import Turn, db
from flask import session, jsonify, request
from util.decorators import session_required, check_user_is_codebreaker
from util.enum import StatusEnum
import json

round_bp = Blueprint("round_bp", __name__)


def is_guess_proper_format(guess, secret_code, num_colors):
    if len(secret_code) != len(guess):
        return False
    if not all([isinstance(g, int) for g in guess]):
        return False
    if max(guess) >= num_colors or min(guess) < 0:
        return False
    return True


def calculate_result(guess, secret_code):
    black_pegs = 0
    white_pegs = 0
    remaining_pegs_guess = {}
    remaining_pegs_secret_code = {}
    for i in range(len(guess)):
        if guess[i] == secret_code[i]:
            black_pegs += 1
        else:
            remaining_pegs_guess[guess[i]] = remaining_pegs_guess.get(guess[i], 0) + 1
            remaining_pegs_secret_code[secret_code[i]] = (
                remaining_pegs_secret_code.get(secret_code[i], 0) + 1
            )

    for key in remaining_pegs_guess.keys():
        if key in remaining_pegs_secret_code:
            white_pegs += min(
                remaining_pegs_guess[key], remaining_pegs_secret_code[key]
            )
    won_round = black_pegs == len(guess)
    correct_numbers = white_pegs + black_pegs
    is_plural = correct_numbers > 1
    if not white_pegs and not black_pegs:
        message = "All incorrect."
    else:
        message = f"{correct_numbers} correct number{'s' if is_plural else ''} and {black_pegs} correct location"
    return {
        "won_round": won_round,
        "black_pegs": black_pegs,
        "white_pegs": white_pegs,
        "message": message,
    }


@round_bp.route("/<round_id>/turns", methods=["POST"])
@session_required
@check_user_is_codebreaker
def make_move(round_id):
    try:
        round, user = request.round, request.user
        secret_code = json.loads(round.secret_code)
        curr_game = round.game
        data = request.json
        guess = data.get("guess")
        curr_turn_num = len(round.turns) + 1
        max_turns, num_colors = (
            curr_game.difficulty.max_turns,
            curr_game.difficulty.num_colors,
        )
        if not data or (data and not guess):
            return jsonify({"message": "Guess was not passed in the request."}), 400

        elif not is_guess_proper_format(guess, secret_code, num_colors):
            return jsonify({"message": "Guess is not in the proper format."}), 400

        elif (
            round.status == StatusEnum.COMPLETED
            or round.status == StatusEnum.TERMINATED
        ):
            return (
                jsonify(
                    {"message": "Move cannot be made in completed/terminated round."}
                ),
                400,
            )
        elif curr_turn_num > max_turns:
            return (
                jsonify(
                    {"message": "Cannot make move (exceeds number of turns possible.)"}
                ),
                400,
            )
        result = calculate_result(guess, secret_code)
        result_encoded, guess_encoded = json.dumps(result), json.dumps(guess)
        new_turn = Turn(
            round=round,
            turn_num=curr_turn_num,
            guess=guess_encoded,
            result=result_encoded,
        )
        if result["won_round"] or curr_turn_num == max_turns:
            round.status = StatusEnum.COMPLETED

        if result["won_round"]:
            round.points = curr_turn_num
            # TODO: handle multiplayer logic in future, single player only has one round
            if curr_game.is_multiplayer == False:
                curr_game.winner = user
                curr_game.status = StatusEnum.COMPLETED
        db.session.add(new_turn)
        db.session.commit()
        return (
            jsonify({"message": "Successfully made turn.", "result": result_encoded}),
            201,
        )
    except Exception as e:
        error_message = str(e)
        status_code = getattr(e, "code", 500)
        return jsonify({"message": error_message}), status_code
