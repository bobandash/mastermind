from flask import Blueprint
from models.models import Turn, db
from flask import session, jsonify, request
from util.decorators import (
    session_required,
    check_user_is_codebreaker,
    check_round_is_valid,
    check_user_in_round,
)
from util.enum import StatusEnum
from util.game_logic import is_guess_proper_format, calculate_result
from util.json_errors import ErrorResponse
import json


round_bp = Blueprint("round_bp", __name__)


@round_bp.route("/<round_id>", methods=["GET"])
@session_required
@check_round_is_valid
def get_round_details(round_id):
    round = request.round
    game = round.game

    # If the user passes the game id into args
    # this will ensure that the round is in the game
    game_id = request.args.get("game_id")
    if game_id and game.id != int(game_id):
        return ErrorResponse.not_found("Round is not in game id.")

    all_turns = (
        Turn.query.filter_by(round_id=round.id).order_by(Turn.turn_num.asc()).all()
    )
    max_turns = game.difficulty.max_turns
    num_turns_used = len(all_turns) if all_turns else 0
    turn_history = [
        {
            "id": turn.id,
            "turn_num": turn.turn_num,
            "guess": json.loads(turn.guess),
            "result": json.loads(turn.result),
        }
        for turn in all_turns
    ]

    secret_code = None
    if round.status == StatusEnum.COMPLETED:
        secret_code = json.loads(round.secret_code)
    response_data = {
        "id": round_id,
        "status": round.status.name,
        "turns_used": num_turns_used,
        "turns_remaining": max_turns - num_turns_used,
        "turns": turn_history,
        "secret_code": secret_code,
    }

    return (
        jsonify(response_data),
        200,
    )


@round_bp.route("/<round_id>/turns", methods=["POST"])
@session_required
@check_user_is_codebreaker
def make_move(round_id):
    round, user = request.round, request.user
    secret_code = json.loads(round.secret_code)
    game = round.game
    data = request.json
    guess = data.get("guess")
    curr_turn_num = len(round.turns) + 1
    max_turns, num_colors = (
        game.difficulty.max_turns,
        game.difficulty.num_colors,
    )
    if not data or (data and not guess):
        return jsonify({"message": "Guess was not passed in the request."}), 400

    elif not is_guess_proper_format(guess, secret_code, num_colors):
        return jsonify({"message": "Guess is not in the proper format."}), 400

    elif round.status == StatusEnum.COMPLETED or round.status == StatusEnum.TERMINATED:
        return (
            jsonify({"message": "Move cannot be made in completed/terminated round."}),
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

    #! TODO: FOR SOME REASON, game's status does not update
    if result["won_round"]:
        round.points = curr_turn_num
        # TODO: handle multiplayer logic in future, single player only has one round
        if game.is_multiplayer == False:
            game.winner = user
            game.status = StatusEnum.COMPLETED
    db.session.add(new_turn)
    db.session.commit()
    return (
        jsonify(
            {
                "id": new_turn.id,
                "turn_num": curr_turn_num,
                "guess": guess,
                "result": result,
            }
        ),
        201,
    )


#! TODO: ADD VALIDATION FOR SECRET CODE
# @round_bp.route('/<round_id>/secret-code')
# @session_required
# @check_user_in_round
# def get_secret_code():
