import pytest
from flask import Flask, abort
from models.models import db
from routes.auth_bp import auth_bp


@pytest.fixture(scope="function")
def create_app():
    app_mock = Flask(__name__)
    app_mock.config["TESTING"] = True
    app_mock.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app_mock.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app_mock.config["SECRET_KEY"] = "secret_key"
    app_mock.config["SESSION_PERMANENT"] = False
    app_mock.config["SESSION_USE_SIGNER"] = True
    db.init_app(app_mock)

    # register routes for app
    app_mock.register_blueprint(auth_bp, url_prefix="/auth")
    return app_mock


@pytest.fixture(scope="function")
def create_db(create_app):
    app_mock = create_app

    with app_mock.app_context():
        db.create_all()
        db.session.commit()

    yield db

    with app_mock.app_context():
        db.session.remove()
        db.drop_all()
