from functools import wraps
from models.models import User, Game, Round
from flask import session, jsonify, request
from util.json_errors import ErrorResponse


# Checks if session is valid and passes the user down as a request
# If invalid, returns 401 unauthorized error
def session_required(fn):
    @wraps(fn)
    def decorator(*args, **kwargs):
        user_id = session.get("user_id")
        if not user_id:
            return ErrorResponse.not_authorized("Unauthorized access.")
        user = User.query.get(user_id)
        if not user:
            return ErrorResponse.not_authorized("Unauthorized access.")
        request.user = user
        return fn(*args, **kwargs)

    return decorator


# !👇 All decorators underneath depend on session_required being called before
def check_user_in_game(fn):
    @wraps(fn)
    def decorator(*args, **kwargs):
        user = request.user
        game_id = kwargs.get("game_id")
        game = Game.query.get(game_id)
        if not game:
            return ErrorResponse.bad_request("Game id is not valid.")
        if user not in game.players:
            return ErrorResponse.not_authorized("User is not a player in the game.")
        request.game = game
        return fn(*args, **kwargs)

    return decorator


# depends on session_required to run before
# Checks whether or not the user is the codebreaker in the specific round
def check_user_is_codebreaker(fn):
    @wraps(fn)
    def decorator(*args, **kwargs):
        user = request.user
        round_id = kwargs.get("round_id")
        round = Round.query.get(round_id)
        if not round:
            return ErrorResponse.bad_request("Round id is not valid.")
        if not user.id == round.code_breaker_id:
            return ErrorResponse.not_authorized("User is not the codebreaker.")
        request.round = round
        return fn(*args, **kwargs)

    return decorator


def check_user_in_round(fn):
    @wraps(fn)
    def decorator(*args, **kwargs):
        user = request.user
        round_id = kwargs.get("round_id")
        round = Round.query.get(round_id)
        if not round:
            return ErrorResponse.bad_request("Round id is not valid.")
        player_ids_in_game = [player.id for player in round.game.players]
        if not user.id == player_ids_in_game:
            return ErrorResponse.not_authorized("User is not a player in the game.")
        request.round = round
        return fn(*args, **kwargs)

    return decorator


def check_round_is_valid(fn):
    @wraps(fn)
    def decorator(*args, **kwargs):
        user = request.user
        round_id = kwargs.get("round_id")
        round = Round.query.get(round_id)
        if not round:
            return ErrorResponse.bad_request("Round id is not valid.")
        request.round = round
        return fn(*args, **kwargs)

    return decorator
