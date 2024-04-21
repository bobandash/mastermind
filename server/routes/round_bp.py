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
from sqlalchemy.exc import SQLAlchemyError
import logging

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
        return ErrorResponse.handle_error("Round does not exist in game", 404)

    try:
        all_turns = (
            Turn.query.filter_by(round_id=round.id).order_by(Turn.turn_num.asc()).all()
        )
    except SQLAlchemyError as e:
        logging.error(f"Error fetching all turns in round: {str(e)}")
        return ErrorResponse.handle_error("Turns were not able to be fetched", 503)
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
        "round_num": round.round_num,
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
    if request.content_type != "application/json":
        return ErrorResponse.handle_error("Guess was not provided.", 415)

    round, user = request.round, request.user
    secret_code = json.loads(round.secret_code)
    game = round.game
    data = request.get_json()
    guess = data.get("guess")
    curr_turn_num = len(round.turns) + 1
    max_turns, num_colors = (
        game.difficulty.max_turns,
        game.difficulty.num_colors,
    )

    if not guess:
        return ErrorResponse.handle_error("Guess was not provided in payload.", 400)
    elif not is_guess_proper_format(guess, secret_code, num_colors):
        return ErrorResponse.handle_error(
            "Guess was not provided in correct format.", 400
        )
    elif round.status == StatusEnum.COMPLETED or round.status == StatusEnum.TERMINATED:
        return ErrorResponse.handle_error(
            "Move cannot be made in completed/terminated round.", 400
        )
    elif curr_turn_num > max_turns:
        return ErrorResponse.handle_error(
            "Cannot make move (exceeds number of turns possible).", 400
        )

    result = calculate_result(guess, secret_code)
    won_round = result.get("won_round", False)

    try:
        new_turn = Turn(
            round=round,
            turn_num=curr_turn_num,
            guess=json.dumps(guess),
            result=json.dumps(result),
        )
    except (TypeError, ValueError):
        return ErrorResponse.handle_error("Error creating new turn", 400)

    try:
        if won_round or curr_turn_num == max_turns:
            round.status = StatusEnum.COMPLETED
            # Point calculation is based on amt of turns taken, and the winner of the game has the LEAST amt of points
            # If the winner could not guess the code in turns allocated, they get a penalty of 5 points added
            if won_round:
                round.points = curr_turn_num
            else:
                round.points = curr_turn_num + 5
                if game.is_multiplayer == False:
                    game.winner = user
                    game.status = StatusEnum.COMPLETED
                # TODO: handle multiplayer logic, single player only has one round
        db.session.add(new_turn)
        db.session.commit()
    except (SQLAlchemyError, ValueError) as e:
        db.session.rollback()
        logging.error(f"Error creating game: {str(e)}")
        return ErrorResponse.handle_error(
            "Creating new turn failed. Please check the provided data.",
            500,
        )

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


@round_bp.route("/<round_id>/secret-code", methods=["GET"])
@session_required
@check_user_in_round
def get_secret_code(round_id):
    user = request.user
    round = request.round
    secret_code = json.loads(round.secret_code)
    if (
        user.id == round.code_breaker_id and round.status == StatusEnum.COMPLETED
    ) or user.id != round.code_breaker_id:
        return jsonify({"secret_code": secret_code}), 200
    return ErrorResponse.handle_error(
        "Round is still in progress, cannot view secret code.", 401
    )
