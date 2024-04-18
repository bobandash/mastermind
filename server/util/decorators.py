from functools import wraps
from models.models import User, Game
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


# depends on session_required to run before
def game_valid_for_user_given_game_id(fn):
    @wraps(fn)
    def decorator(*args, **kwargs):
        user = request.user
        game_id = kwargs.get("game_id")
        game = Game.query.get(game_id)
        if not game:
            return jsonify({"message": "Game id is not valid."}), 400
        if user not in game.players:
            return jsonify({"message": "User is not a player in the game"}), 401
        request.game = game
        return fn(*args, **kwargs)

    return decorator
