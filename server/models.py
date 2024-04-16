from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ARRAY
from sqlalchemy.orm import validates
from uuid import uuid4
from datetime import datetime
import enum
import json

db = SQLAlchemy()


# Enums related to models
class DifficultyEnum(enum.Enum):
    NORMAL = 1
    HARD = 2
    CUSTOM = 3


class StatusEnum(enum.Enum):
    IN_PROGRESS = 1
    COMPLETED = 2
    TERMINATED = 3  # TODO: decide whether or not to terminate incomplete games after a certain time


# do not have to be logged in to play
# unless you want to save your game stats
class User(db.Model):
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid4()))
    username = db.Column(db.String(20), nullable=True)
    password = db.Column(db.String(20), nullable=True)
    games = db.relationship("Game", backref="user")
    rounds = db.relationship("Round", backref="user")

    @validates("password")
    def validate_password(self, key, password):
        if password and len(password) < 8:
            raise ValueError("Password has to be at least 8 characters")
        return password


class Difficulty(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mode = db.Column(db.Enum(DifficultyEnum), nullable=False)
    max_turns = db.Column(db.Integer, nullable=False)
    num_holes = db.Column(db.Integer, nullable=False)
    num_colors = db.Column(db.Integer, nullable=False)
    games = db.relationship("Game", backref="difficulty")

    @validates("mode")
    def validate_mode(self, key, mode):
        if (
            mode == DifficultyEnum.NORMAL
            and Difficulty.query.filter_by(mode=mode).first()
        ):
            raise ValueError("There cannot exist two Normal difficulties.")
        elif (
            mode == DifficultyEnum.HARD
            and Difficulty.query.filter_by(mode=mode).first()
        ):
            raise ValueError("There cannot exist two Hard difficulties.")
        return mode


# Games have round(s), single player mode is one round
class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    createdAt = db.Column(db.DateTime, default=lambda: datetime.now())
    is_multiplayer = db.Column(db.Boolean, nullable=False)
    difficulty = db.Column(db.Integer, db.ForeignKey("difficulty.id"), nullable=False)
    status = db.Column(db.Enum(StatusEnum), nullable=False)
    num_rounds = db.Column(db.Integer, default=1, nullable=False)
    winner = db.Column(db.String, db.ForeignKey("user.id"))
    rounds = db.relationship("Round", backref="game")


class Round(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game = db.Column(db.Integer, db.ForeignKey("game.id"), nullable=False)
    status = db.Column(db.Enum(StatusEnum), nullable=False)
    code_breaker = db.Column(db.String, db.ForeignKey("user.id"), nullable=False)
    round_num = db.Column(db.Integer, nullable=False)
    secret_code = db.Column(ARRAY(db.Integer), nullable=False)
    points = db.Column(db.Integer, default=None)
    turns = db.relationship("Turn", backref="round")

    @validates("game", "secret_code")
    def validate_secret_code(self, key, value):
        if key == "secret_code" and self.game:
            curr_game = Game.query.filter_by(id=self.game).first()
            if curr_game:
                num_holes = curr_game.difficulty.num_holes
                if len(value) != num_holes:
                    raise ValueError(
                        "Secret code is invalid (does not match the number of holes)"
                    )
        return value


# Rounds have multiple turns
class Turn(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    round = db.Column(db.Integer, db.ForeignKey("round.id"), nullable=False)
    turn_num = db.Column(db.Integer, nullable=False)
    guess = db.Column(ARRAY(db.Integer), nullable=False)
    result = db.Column(db.String(255), nullable=False)  # stored as a serialized json

    @validates("guess")
    def validate_guess(self, key, value):
        if self.round:
            curr_round = Round.query.filter_by(id=self.round).first()
            num_holes = curr_round.game.difficulty.num_holes
            if num_holes and not len(value) == num_holes:
                raise ValueError("Guess is invalid (does not match number of holes).")
        return value

    # TODO: decide whether or not to include more validation
    @validates("result")
    def validate_result(self, key, value):
        res_map = json.loads(value)
        if (
            len(res_map.keys()) > 2
            or "black_pegs" not in res_map
            or "white_pegs" not in res_map
        ):
            raise ValueError("Turn result is not in the proper format")
