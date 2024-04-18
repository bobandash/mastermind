from flask import Blueprint, jsonify, request, session
from models.models import User, db
from flask_bcrypt import Bcrypt

auth_bp = Blueprint("auth_bp", __name__)
bcrypt = Bcrypt()


# Basic flow is user has anonymous access
# Can update their account with user information if they want to save/login later
@auth_bp.route("/register", methods=["POST"])
def register_anonymous_user():
    if session.get("user_id"):
        return (
            jsonify(
                {"message": "If already signed in, user cannot create a new account."}
            ),
            403,
        )

    new_user = User()
    db.session.add(new_user)
    db.session.commit()
    session["user_id"] = new_user.id
    return jsonify({"message": "User was successfully created."}), 200


@auth_bp.route("/me", methods=["GET", "PUT"])
def user_info():
    user_id = session.get("user_id")
    user = User.query.filter_by(id=user_id).first()
    if request.method == "GET":
        if not user:
            return jsonify({"message": "Unauthorized access."}), 401
        return jsonify({"id": user.id}), 200
    # creates user with persistent access regardless of cookies
    elif request.method == "PUT":
        if user.password or user.email:
            return jsonify({"message": "User already has persistent login."}), 403
        new_username, new_password, new_email = (
            request.form.get("username"),
            request.form.get("password"),
            request.form.get("email"),
        )

        if not all([new_username, new_password, new_email]):
            return jsonify({"message": "Necessary field data is missing."}), 400

        if len(new_password) < 8 or len(new_password) > 20:
            return (
                jsonify({"message": "Password has to be between 8 to 20 characters."}),
                400,
            )

        email_taken = User.query.filter_by(email=new_email).first()
        if email_taken:
            return jsonify({"message": "Email is already taken."}), 400

        try:
            hashed_password = bcrypt.generate_password_hash(new_password).decode(
                "utf-8"
            )
            user.username = new_username
            user.email = new_email
            user.password = hashed_password
            db.session.commit()
            return (
                jsonify({"message": "User information was updated successfully"}),
                200,
            )
        # Case: one of the schemas errors is raised
        except ValueError as e:
            return jsonify({"error": str(e)}), 400


@auth_bp.route("/login", methods=["POST"])
def login_user():
    email, password = request.form.get("email"), request.form.get("password")
    if not all([email, password]):
        return jsonify({"message": "Necessary field data is missing"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or (user and not user.password):
        return jsonify({"message": "Invalid credentials"}), 401

    password_matches = bcrypt.check_password_hash(user.password, password)
    if not password_matches:
        return jsonify({"message": "Invalid credentials"}), 401

    session["user_id"] = user.id
    return jsonify({"message": "Successfully logged in"}), 200


@auth_bp.route("/logout", methods=["POST"])
def logout_user():
    session.pop("user_id")
    return jsonify({"message": "Successfully logged out user"}), 200
