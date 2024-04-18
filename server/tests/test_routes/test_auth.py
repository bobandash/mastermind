from flask import session
import pytest
from models.models import User


class TestAuthRoute:
    def test_register_already_signed_in(self, create_app, create_db):
        mock_app = create_app
        mock_db = create_db
        client_mock = mock_app.test_client(use_cookies=True)

        with mock_app.app_context():
            with client_mock.session_transaction() as sess:
                sess["user_id"] = 123
            response = client_mock.post("/auth/register")
            assert response.status_code == 403

    def test_register_not_signed_in(self, create_app, create_db):
        mock_app = create_app
        mock_db = create_db
        client_mock = mock_app.test_client(use_cookies=True)

        with mock_app.app_context():
            response = client_mock.post("/auth/register")
            assert response.status_code == 200
            assert response.json["message"] == "User was successfully created."
            assert User.query.count() == 1

    def test_me_gets_user_id(self, create_app, create_db):
        mock_app = create_app
        mock_db = create_db
        client_mock = mock_app.test_client(use_cookies=True)

        with mock_app.app_context():
            new_user = User()
            mock_db.session.add(new_user)
            mock_db.session.commit()
            with client_mock.session_transaction() as sess:
                sess["user_id"] = new_user.id
            response = client_mock.get("/auth/me")
            assert response.status_code == 200
            assert response.json["id"] == new_user.id


# TODO: After finish main game logic, add all tests
# @auth_bp.route("/me", methods=["GET", "PUT"])
# def user_info():
#     user_id = session.get("user_id")
#     user = User.query.filter_by(id=user_id).first()
#     if request.method == "GET":
#         if not user:
#             return jsonify({"message": "Unauthorized access."}), 401
#         return jsonify({"id": user.id}), 200
#     # creates user with persistent access regardless of cookies
#     elif request.method == "PUT":
#         if user.password or user.email:
#             return jsonify({"message": "User already has persistent login."}), 403
#         new_username, new_password, new_email = (
#             request.form.get("username"),
#             request.form.get("password"),
#             request.form.get("email"),
#         )

#         if not all([new_username, new_password, new_email]):
#             return jsonify({"message": "Necessary field data is missing."}), 400

#         if len(new_password) < 8 or len(new_password) > 20:
#             return (
#                 jsonify({"message": "Password has to be between 8 to 20 characters."}),
#                 400,
#             )

#         email_taken = User.query.filter_by(email=new_email).first()
#         if email_taken:
#             return jsonify({"message": "Email is already taken."}), 400

#         try:
#             hashed_password = bcrypt.generate_password_hash(new_password).decode(
#                 "utf-8"
#             )
#             user.username = new_username
#             user.email = new_email
#             user.password = hashed_password
#             db.session.commit()
#             return (
#                 jsonify({"message": "User information was updated successfully"}),
#                 200,
#             )
#         # Case: one of the schemas errors is raised
#         except ValueError as e:
#             return jsonify({"error": str(e)}), 400


# @auth_bp.route("/login", methods=["POST"])
# def login_user():
#     email, password = request.form.get("email"), request.form.get("password")
#     if not all([email, password]):
#         return jsonify({"message": "Necessary field data is missing"}), 400

#     user = User.query.filter_by(email=email).first()
#     if not user or (user and not user.password):
#         return jsonify({"message": "Invalid credentials"}), 401

#     password_matches = bcrypt.check_password_hash(user.password, password)
#     if not password_matches:
#         return jsonify({"message": "Invalid credentials"}), 401

#     session["user_id"] = user.id
#     return jsonify({"message": "Successfully logged in"}), 200


# @auth_bp.route("/logout", methods=["POST"])
# def logout_user():
#     session.pop("user_id")
#     return jsonify({"message": "Successfully logged out user"}), 200
