from flask import Blueprint
from models.models import Turn, db
from flask import session, jsonify, request
from util.decorators import (
    session_required,
    check_user_is_codebreaker,
    check_user_in_round,
)
from util.enum import StatusEnum
from util.game_logic import (
    is_code_valid,
    calculate_result,
)
from util.json_errors import ErrorResponse
import json
from sqlalchemy.exc import SQLAlchemyError
import logging

round_bp = Blueprint("round_bp", __name__)


@round_bp.route("/<round_id>", methods=["GET"])
@session_required
@check_user_in_round
def get_round_details(round_id):
    user = request.user
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

    # Hide the secret code if user is not the code breaker and
    # Round is still in progress
    secret_code = None
    is_code_breaker = round.code_breaker_id == user.id
    if round.secret_code and (
        not is_code_breaker or round.status == StatusEnum.COMPLETED
    ):
        secret_code = json.loads(round.secret_code)

    return (
        jsonify(
            {
                "id": round_id,
                "status": round.status.name,
                "round_num": round.round_num,
                "turns_used": num_turns_used,
                "turns_remaining": max_turns - num_turns_used,
                "turns": turn_history,
                "secret_code": secret_code,
                "code_breaker_id": round.code_breaker_id,
            }
        ),
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
    max_turns, num_colors, num_holes = (
        game.difficulty.max_turns,
        game.difficulty.num_colors,
        game.difficulty.num_holes,
    )

    if not guess:
        return ErrorResponse.handle_error("Guess was not provided in payload.", 400)
    elif not is_code_valid(guess, num_holes, num_colors):
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
            is_last_round = len(game.rounds) == game.num_rounds
            round.status = StatusEnum.COMPLETED
            if is_last_round:
                game.status = StatusEnum.COMPLETED
            # Point calculation is based on amt of turns taken, and the winner of the game has the LEAST amt of points
            # If the winner could not guess the code in turns allocated, they get a penalty of 5 points added
            if won_round:
                round.points = curr_turn_num
            else:
                round.points = curr_turn_num + 5
            if game.is_multiplayer == False and won_round:
                game.winner = user
            elif game.is_multiplayer and is_last_round:
                player_to_points = {player.id: 0 for player in game.players}
                player_ids = list(player_to_points.keys())
                if len(player_ids) != 2:
                    raise ValueError("Multiplayer was not configured properly.")
                for round in game.rounds:
                    player_to_points[round.code_breaker_id] += round.points
                if player_to_points[player_ids[0]] < player_to_points[player_ids[1]]:
                    game.winner_id = player_ids[0]
                elif player_to_points[player_ids[1]] < player_to_points[player_ids[0]]:
                    game.winner_id = player_ids[1]

        db.session.add(new_turn)
        db.session.commit()
    except (SQLAlchemyError, ValueError) as e:
        db.session.rollback()
        logging.error(f"Error creating new turn: {str(e)}")
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


# Allows code maker to add secret code and change game status to in progress
@round_bp.route("/<round_id>/secret-code", methods=["PATCH"])
@session_required
@check_user_in_round
def add_secret_code(round_id):
    if request.content_type != "application/json":
        return ErrorResponse.handle_error("Secret code not provided.", 415)
    user = request.user
    round = request.round
    difficulty = round.game.difficulty
    num_holes, num_colors = difficulty.num_holes, difficulty.num_colors

    data = request.get_json()
    secret_code = data.get("secret_code")
    if not secret_code:
        return ErrorResponse.handle_error("Secret code was not provided.", 400)

    if not is_code_valid(secret_code, num_holes, num_colors):
        return ErrorResponse.handle_error("Secret code provided was invalid.", 400)

    if round.status != StatusEnum.NOT_STARTED:
        return ErrorResponse.handle_error(
            "Cannot change secret code after a game already started.", 401
        )

    is_user_code_maker = user.id != round.code_breaker
    if is_user_code_maker and round.status == StatusEnum.NOT_STARTED:
        try:
            round.status = StatusEnum.IN_PROGRESS
            round.secret_code = json.dumps(secret_code)
            db.session.commit()
            return (
                jsonify({"message": "Secret code has been successfully updated."}),
                200,
            )
        except (SQLAlchemyError, ValueError) as e:
            db.session.rollback()
            logging.error(f"Error creating game: {str(e)}")
            return ErrorResponse.handle_error(
                "Creating new turn failed. Please check the provided data.",
                500,
            )

    # case user is not code maker
    return ErrorResponse.handle_error("Unauthorized access.", 401)


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
