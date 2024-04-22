from flask import Blueprint, jsonify, request, session
from models.models import User, db
from flask_bcrypt import Bcrypt
from util.json_errors import ErrorResponse
from sqlalchemy.exc import SQLAlchemyError
import logging
from util.decorators import session_required
import re

auth_bp = Blueprint("auth_bp", __name__)
bcrypt = Bcrypt()


# Basic flow is user has anonymous access
# Can update their account with user information if they want to save/login later
@auth_bp.route("/register", methods=["POST"])
def register_anonymous_user():
    user_id = session.get("user_id")
    if user_id:
        return ErrorResponse.handle_error(
            "User cannot create a new account if currently signed in.", 403
        )
    try:
        user = User()
        db.session.add(user)
        db.session.commit()
        session["user_id"] = user.id
    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"Error creating user: {str(e)}")
        return ErrorResponse.handle_error(
            "User creation failed.",
            500,
        )
    return jsonify({"id": user.id}), 201


@session_required
@auth_bp.route("/me", methods=["GET"])
def user_info():
    user = request.user
    return jsonify({"id": user.id}), 200


@session_required
@auth_bp.route("/me", methods=["PUT"])
def create_persistent_login():
    user = request.user
    if user.password or user.email:
        return ErrorResponse.handle_error("User already has persistent login.", 403)
    username, password, email = (
        request.form.get("username"),
        request.form.get("password"),
        request.form.get("email"),
    )

    if not all([username, password, email]):
        return ErrorResponse.handle_error("Necessary field data is missing.", 400)

    if len(password) < 8 or len(password) > 20:
        return ErrorResponse.handle_error(
            "Password has to be between 8 to 20 characters.", 400
        )

    regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"
    if not re.match(regex, email):
        return ErrorResponse.handle_error("Email is not valid.", 400)

    try:
        user_email_taken = User.query.filter_by(email=email).first()
    except SQLAlchemyError as e:
        logging.error(f"Error fetching user: {str(e)}")
        return ErrorResponse.handle_error("User was not able to be fetched.", 503)

    if user_email_taken:
        return ErrorResponse.handle_error("Account already exists.", 400)

    try:
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
        user.username = username
        user.email = email
        user.password = hashed_password
        db.session.commit()
        return (
            jsonify({"id": user.id, "username": user.username, "email": user.email}),
            204,
        )
    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"Error creating user: {str(e)}")
        return ErrorResponse.handle_error(
            "User information could not be edited.",
            500,
        )


@auth_bp.route("/login", methods=["POST"])
def login_user():
    email, password = request.form.get("email"), request.form.get("password")
    if not all([email, password]):
        return ErrorResponse.handle_error("Necessary field data is missing.", 400)

    try:
        user = User.query.filter_by(email=email).first()
    except SQLAlchemyError as e:
        logging.error(f"Error fetching user: {str(e)}")
        return ErrorResponse.handle_error("User was not able to be fetched.", 503)

    # CASE: Some users don't have not registered persistent login
    if not user or (user and not user.password):
        return ErrorResponse.handle_error("Invalid Credentials.", 401)

    password_matches = bcrypt.check_password_hash(user.password, password)
    if not password_matches:
        return ErrorResponse.handle_error("Invalid Credentials.", 401)

    session["user_id"] = user.id
    return jsonify({"id": user.id, "email": user.email, "username": user.username}), 200


@auth_bp.route("/logout", methods=["POST"])
def logout_user():
    session.pop("user_id")
    return jsonify({"message": "Successfully logged out user"}), 200
