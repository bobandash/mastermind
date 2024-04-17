from flask import Flask
from dotenv import load_dotenv
from models.models import db
from flask_migrate import Migrate
import os

# TODO: for the mvp, will implement with JWT Token to save time
# however, for the game routes from my understanding, there's not a lot of performance benefit.
# the statelessness of jwt token for the majority of the routes is not needed, you would have the make db calls with the user_id
# If I use session based auth with redis as cache layer, I can at least logout the users if they get hacked


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
