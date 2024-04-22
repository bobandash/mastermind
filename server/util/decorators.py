from functools import wraps
from models.models import User, Game, Round, WaitingRoom
from flask import session, jsonify, request
from util.json_errors import ErrorResponse
from sqlalchemy.exc import SQLAlchemyError
import logging


# Checks if session is valid and passes the user down as a request
# If invalid, returns 401 unauthorized error
def session_required(fn):
    @wraps(fn)
    def decorator(*args, **kwargs):
        user_id = session.get("user_id")
        try:
            user = User.query.get(user_id)
        except SQLAlchemyError as e:
            logging.error(f"Error fetching user: {str(e)}")
            return ErrorResponse.handle_error("User was not able to be fetched.", 503)

        if not user:
            return ErrorResponse.handle_error("Unauthorized access.", 401)
        request.user = user
        return fn(*args, **kwargs)

    return decorator


# !👇 Depends on session_required decorator being called before
def check_user_in_game(fn):
    @wraps(fn)
    def decorator(*args, **kwargs):
        user = request.user
        game_id = kwargs.get("game_id")
        try:
            game = Game.query.get(game_id)
        except SQLAlchemyError as e:
            logging.error(f"Error fetching game: {str(e)}")
            return ErrorResponse.handle_error("Game was not able to be fetched.", 503)

        if not game:
            return ErrorResponse.handle_error("Game id is not valid.", 400)
        if user not in game.players:
            return ErrorResponse.handle_error("User is not a player in the game.", 401)
        request.game = game
        return fn(*args, **kwargs)

    return decorator


# !👇 Depends on session_required decorator being called before
def check_user_is_codebreaker(fn):
    @wraps(fn)
    def decorator(*args, **kwargs):
        user = request.user
        round_id = kwargs.get("round_id")
        try:
            round = Round.query.get(round_id)
        except SQLAlchemyError as e:
            logging.error(f"Error fetching Round: {str(e)}")
            return ErrorResponse.handle_error("Round was not able to be fetched.", 503)
        if not round:
            return ErrorResponse.handle_error("Round id is not valid.", 404)
        if not user.id == round.code_breaker_id:
            return ErrorResponse.handle_error("User is not the codebreaker.", 401)
        request.round = round
        return fn(*args, **kwargs)

    return decorator


# !👇 Depends on session_required decorator being called before
def check_user_in_round(fn):
    @wraps(fn)
    def decorator(*args, **kwargs):
        user = request.user
        round_id = kwargs.get("round_id")
        try:
            round = Round.query.get(round_id)
        except SQLAlchemyError as e:
            logging.error(f"Error fetching Round: {str(e)}")
            return ErrorResponse.handle_error("Round was not able to be fetched.", 503)

        if not round:
            return ErrorResponse.handle_error("Round id is not valid.", 404)
        player_ids_in_game = [player.id for player in round.game.players]
        if not user.id in player_ids_in_game:
            return ErrorResponse.handle_error("User is not a player in the game.", 401)
        request.round = round
        return fn(*args, **kwargs)

    return decorator


# !👇 Depends on session_required decorator being called before
def check_round_is_valid(fn):
    @wraps(fn)
    def decorator(*args, **kwargs):
        round_id = kwargs.get("round_id")
        try:
            round = Round.query.get(round_id)
        except SQLAlchemyError as e:
            logging.error(f"Error fetching Round: {str(e)}")
            return ErrorResponse.handle_error("Round was not able to be fetched.", 503)
        if not round:
            return ErrorResponse.handle_error("Round id is not valid.", 404)
        request.round = round
        return fn(*args, **kwargs)

    return decorator


def check_user_in_waiting_room(fn):
    @wraps(fn)
    def decorator(*args, **kwargs):
        user = request.user
        room_id = kwargs.get("room_id")
        try:
            waiting_room = WaitingRoom.query.get(room_id)
        except SQLAlchemyError as e:
            logging.error(f"Error fetching Round: {str(e)}")
            return ErrorResponse.handle_error("Round was not able to be fetched.", 503)
        if not waiting_room:
            return ErrorResponse.handle_error("Waiting room does not exist", 404)

        player_ids = [player.id for player in waiting_room.players]
        if user.id not in player_ids:
            return ErrorResponse.handle_error("User is not a part of waiting room", 401)
        request.waiting_room = waiting_room
        return fn(*args, **kwargs)

    return decorator
