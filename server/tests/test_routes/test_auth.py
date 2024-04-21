from flask import session
from functools import wraps
from models.models import User
from util.decorators import session_required


# TODO: Figure out how to pass request and test decorators
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
            assert response.status_code == 201
            assert User.query.count() == 1

    def test_register_not_signed_in(self, create_app, create_db):
        mock_app = create_app
        mock_db = create_db
        client_mock = mock_app.test_client(use_cookies=True)

        with mock_app.app_context():
            response = client_mock.post("/auth/register")
            assert response.status_code == 201
            assert User.query.count() == 1


# @session_required
# @auth_bp.route("/me", methods=["GET"])
# def user_info():
#     user = request.user
#     return jsonify({"id": user.id}), 200
