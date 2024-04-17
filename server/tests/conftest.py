import pytest
from flask import Flask
from models.models import db
from flask_jwt_extended import JWTManager


@pytest.fixture(scope="function")
def create_app():
    app_mock = Flask(__name__)
    app_mock.config["TESTING"] = True
    #  TODO: sqlite is not allowed to use Postgresql's model
    app_mock.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
    jwt = JWTManager(app_mock)
    db.init_app(app_mock)

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
