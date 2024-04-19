from functools import wraps
from models.models import User, Game, Round
from flask import session, jsonify, request


# Checks if session is valid and passes the user down as a request
# If invalid, returns 401 unauthorized error
def session_required(fn):
    @wraps(fn)
    def decorator(*args, **kwargs):
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"message": "Unauthorized access."}), 401
        user = User.query.get(user_id)
        if not user:
            return jsonify({"message": "Unauthorized access."}), 401
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
            return jsonify({"message": "Game id is not valid."}), 400
        if user not in game.players:
            return jsonify({"message": "User is not a player in the game."}), 401
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
            return jsonify({"message": "Round id is not valid."}), 400
        if not user.id == round.code_breaker_id:
            return jsonify({"message": "User is not the codebreaker."}), 401
        request.round = round
        return fn(*args, **kwargs)

    return decorator


# Given specific round, checks whether or not the user is the codebreaker game
def check_user_in_game(fn):
    @wraps(fn)
    def decorator(*args, **kwargs):
        user = request.user
        round_id = kwargs.get("round_id")
        round = Round.query.get(round_id)
        if not round:
            return jsonify({"message": "Round id is not valid."}), 400
        player_ids_in_game = [player.id for player in round.game.players]
        if not user.id == player_ids_in_game:
            return jsonify({"message": "User is not a part of the game."}), 401
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
            return jsonify({"message": "Round id is not valid."}), 400
        request.round = round
        return fn(*args, **kwargs)

    return decorator
