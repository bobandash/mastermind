# Script to populate database with preset fields
# !Drops all existing data, DO NOT RUN IN PRODUCTION
from models.models import db, Difficulty, User, Game, Round, Turn, user_games
from util.enum import DifficultyEnum
from flask import Flask
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.config.from_object("config.Config")
db.init_app(app)


def init_difficulties():
    with app.app_context():
        normal_difficulty = Difficulty(
            mode=DifficultyEnum.NORMAL, max_turns=10, num_holes=4, num_colors=8
        )
        hard_difficulty = Difficulty(
            mode=DifficultyEnum.HARD, max_turns=12, num_holes=5, num_colors=10
        )
        try:
            db.session.add(normal_difficulty)
            db.session.add(hard_difficulty)
            db.session.commit()
            print("Difficulties added successfully.")
        except Exception as e:
            db.session.rollback()
            print(f"Error initializing database: {str(e)}")
        finally:
            db.session.close()


if __name__ == "__main__":
    init_difficulties()
