from flask import Blueprint
from functools import wraps
from models.models import Turn, db, Round
from flask import session, jsonify, request
from util.decorators import (
    session_required,
    check_user_is_codebreaker,
    check_round_is_valid,
)
from util.enum import StatusEnum
from util.game_logic import is_guess_proper_format, calculate_result
import json

round_bp = Blueprint("round_bp", __name__)


@round_bp.route("/<round_id>", methods=["GET"])
@session_required
@check_round_is_valid
def get_round_details(round_id):
    try:
        round = request.round
        game = round.game
        round_ended = round.status == StatusEnum.COMPLETED
        all_turns = Turn.query.filter_by(round_id=round.id).all()
        max_turns, num_turns_used = 0, 0
        max_turns, is_multiplayer, num_holes, num_colors = (
            game.difficulty.max_turns,
            game.is_multiplayer,
            game.difficulty.num_holes,
            game.difficulty.num_colors,
        )

        if all_turns:
            num_turns_used = len(all_turns)

        turn_history = [
            {
                "turn_num": turn.turn_num,
                "guess": json.loads(turn.guess),
                "result": json.loads(turn.result),
            }
            for turn in all_turns
        ]

        response_data = {
            "id": round_id,
            "is_multiplayer": is_multiplayer,
            "turns_used": num_turns_used,
            "turns_remaining": max_turns - num_turns_used,
            "turn_history": turn_history,
            "round_ended": round_ended,
        }

        if round_ended:
            response_data["secret_code"] = json.loads(round.secret_code)

        return (
            jsonify(response_data),
            200,
        )
    except Exception as e:
        error_message = str(e)
        status_code = getattr(e, "code", 500)
        return jsonify({"message": error_message}), status_code


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
        turns_remaining = max_turns - curr_turn_num
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
            jsonify(
                {
                    "message": "Successfully made turn.",
                    "turns_remaining": turns_remaining,
                    "guess": guess_encoded,
                    "result": result_encoded,
                }
            ),
            201,
        )
    except Exception as e:
        error_message = str(e)
        status_code = getattr(e, "code", 500)
        return jsonify({"message": error_message}), status_code


# TODO:
# @round_bp.route('/<round_id>/secret-code')
# @session_required
# def get_secret_code():
