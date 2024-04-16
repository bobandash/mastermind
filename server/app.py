from flask import Flask
from dotenv import load_dotenv
from models import db
from flask_migrate import Migrate
import os


def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config.from_object("config.Config")
    db.init_app(app)
    migrate = Migrate(app, db)
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=8000)
