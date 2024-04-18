from flask import Blueprint
from functools import wraps
from models.models import Turn, db
from flask import session, jsonify, request
from util.decorators import session_required, check_user_is_codebreaker
from util.enum import StatusEnum
from util.game_logic import is_guess_proper_format, calculate_result
import json

round_bp = Blueprint("round_bp", __name__)


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
