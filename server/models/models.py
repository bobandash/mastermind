from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from uuid import uuid4
from datetime import datetime
from util.enum import DifficultyEnum, StatusEnum

import json

db = SQLAlchemy()


# Junction table between players and games
user_games = db.Table(
    "user_games",
    db.Column("user_id", db.String, db.ForeignKey("user.id")),
    db.Column("game_id", db.Integer, db.ForeignKey("game.id")),
)


# do not have to be logged in to play
# unless you want to save your game stats
class User(db.Model):
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid4()))
    username = db.Column(db.String(20), nullable=True)
    password = db.Column(db.String(20), nullable=True)
    games = db.relationship("Game", secondary=user_games, backref="players")
    rounds = db.relationship(
        "Round", backref="rounds"
    )  # stores rounds that the user is the code-breaker

    @validates("password")
    def validate_password(self, key, value):
        if value and len(value) < 8:
            raise ValueError("Password has to be at least 8 characters when provided.")
        return value


class Difficulty(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mode = db.Column(db.Enum(DifficultyEnum), nullable=False)
    max_turns = db.Column(db.Integer, nullable=False)
    num_holes = db.Column(db.Integer, nullable=False)
    num_colors = db.Column(db.Integer, nullable=False)
    games = db.relationship("Game", backref="difficulty_ref")

    @validates("max_turns", "num_holes", "num_colors")
    def validate_turns(self, key, value):
        if value <= 0:
            raise ValueError(f"{key} cannot be less than or equal to 0.")
        return value


# Games have round(s), single player mode is one round
class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now())
    is_multiplayer = db.Column(db.Boolean, nullable=False)
    difficulty = db.Column(db.Integer, db.ForeignKey("difficulty.id"), nullable=False)
    status = db.Column(db.Enum(StatusEnum), nullable=False)
    num_rounds = db.Column(db.Integer, default=1, nullable=False)
    winner = db.Column(db.String, db.ForeignKey("user.id"))
    rounds = db.relationship("Round", backref="game_ref")

    @validates("num_rounds")
    def validate_num_rounds(self, key, value):
        if value <= 0:
            raise ValueError(f"Number of rounds cannot be less than or equal to 0.")
        return value


class Round(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game = db.Column(db.Integer, db.ForeignKey("game.id"), nullable=False)
    status = db.Column(db.Enum(StatusEnum), nullable=False)
    code_breaker = db.Column(db.String, db.ForeignKey("user.id"), nullable=False)
    round_num = db.Column(db.Integer, nullable=False)
    secret_code = db.Column(db.String, nullable=False)
    points = db.Column(db.Integer, default=None)
    turns = db.relationship("Turn", backref="round_ref")

    @validates("game", "secret_code")
    def validate_secret_code(self, key, value):
        if key == "secret_code" and self.game:
            num_holes = self.game.difficulty.num_holes
            num_colors = self.game.difficulty.num_colors
            try:
                secret_code = json.loads(value)
            except:
                raise ValueError(
                    "Secret code is in incorrect format (should be json encoded list of integers)."
                )
            if not isinstance(secret_code, list) or not all(
                isinstance(k, int) for k in secret_code
            ):
                raise ValueError(
                    "Secret code is in incorrect format (should be json encoded list of integers)."
                )
            elif len(secret_code) != num_holes:
                raise ValueError(
                    "Secret code is invalid (does not match the number of holes)."
                )
            elif max(secret_code) >= num_colors or min(secret_code) < 0:
                raise ValueError(
                    "Secret code is invalid (one or more numbers is not possible)."
                )
        return value


# Rounds have multiple turns
class Turn(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    round = db.Column(db.Integer, db.ForeignKey("round.id"), nullable=False)
    turn_num = db.Column(db.Integer, nullable=False)
    guess = db.Column(db.String, nullable=False)
    result = db.Column(db.String(255), nullable=False)  # stored as a serialized json

    @validates("guess")
    def validate_guess(self, key, value):
        try:
            guess = json.loads(value)
        except:
            raise ValueError(
                "Guess is in invalid format (should be json encoded list of integers)"
            )
        if not isinstance(guess, list) or not all(isinstance(k, int) for k in guess):
            raise ValueError(
                "Guess is in invalid format (should be json encoded list of integers)"
            )
        num_holes = self.round.game.difficulty.num_holes
        num_colors = self.round.game.difficulty.num_colors
        if not len(guess) == num_holes:
            raise ValueError("Guess is invalid (does not match number of holes).")
        elif max(guess) >= num_colors or min(guess) < 0:
            raise ValueError("Guess is invalid (one or more numbers is not possible).")
        return value

    @validates("result")
    def validate_result(self, key, value):
        try:
            res_map = json.loads(value)
        except:
            raise ValueError(
                "Result is in invalid format (should be json encoded list of black_pegs and white_pegs)."
            )

        if not (
            set(res_map.keys()) == {"black_pegs", "white_pegs"}
            and all(isinstance(res_map[k], int) for k in res_map)
        ):
            raise ValueError("Turn's result is not in the proper format.")

        num_black_pegs, num_white_pegs = res_map["black_pegs"], res_map["white_pegs"]
        if num_black_pegs < 0 or num_white_pegs < 0:
            raise ValueError("Number of pegs is invalid.")

        num_pegs = num_black_pegs + num_white_pegs
        num_holes = self.round.game.difficulty.num_holes
        if num_pegs > num_holes:
            raise ValueError("White and black pegs exceed number of holes.")
        return value