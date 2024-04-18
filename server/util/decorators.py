from functools import wraps
from models.models import User
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
