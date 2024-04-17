import pytest
from models.models import User, Difficulty, Game, Round, Turn
from util.enum import DifficultyEnum, StatusEnum
import json


class TestUserModel:
    def assert_password_raises_length_error(self, password):
        with pytest.raises(
            ValueError, match="Password has to be at least 8 characters when provided."
        ):
            new_user = User(password=password)

    def test_password_too_short(self):
        self.assert_password_raises_length_error("short")
        self.assert_password_raises_length_error("shortes")

    def test_password_valid_length(self):
        new_user = User(username="bruce", password="shortest")
        assert new_user.password == "shortest"

    def test_validate_email_invalidFormat(self):
        new_user = User()
        with pytest.raises(ValueError, match="Invalid email address format."):
            new_user.email = "johnsmith"
        with pytest.raises(ValueError, match="Invalid email address format."):
            new_user.email = "johnsmith@a"
        with pytest.raises(ValueError, match="Invalid email address format."):
            new_user.email = "johnsmith@a.c"

    def test_validate_email_validFormats(self):
        new_user = User()
        new_user.email = "johnsmith@aol.com"
        assert new_user
        new_user.email = "johnsmith@gmail.com"
        assert new_user
        assert new_user.email is "johnsmith@gmail.com"


class TestDifficultyMode:
    def test_max_turns_number_error(self):
        with pytest.raises(
            ValueError, match="max_turns cannot be less than or equal to 0."
        ):
            new_difficulty = Difficulty(
                mode=DifficultyEnum.NORMAL, max_turns=0, num_holes=1, num_colors=1
            )

    def test_num_holes_number_error(self):
        with pytest.raises(
            ValueError, match="num_holes cannot be less than or equal to 0."
        ):
            new_difficulty = Difficulty(
                mode=DifficultyEnum.NORMAL, max_turns=1, num_holes=0, num_colors=1
            )

    def test_num_colors_number_error(self):
        with pytest.raises(
            ValueError, match="num_colors cannot be less than or equal to 0."
        ):
            new_difficulty = Difficulty(
                mode=DifficultyEnum.NORMAL, max_turns=1, num_holes=1, num_colors=0
            )


class TestGameModel:
    def test_invalid_num_rounds_zero(self):
        with pytest.raises(
            ValueError, match="Number of rounds cannot be less than or equal to 0."
        ):
            new_difficulty = Difficulty(
                mode=DifficultyEnum.NORMAL, max_turns=1, num_holes=1, num_colors=1
            )
            new_game = Game(
                is_multiplayer=False,
                difficulty=new_difficulty,
                status=StatusEnum.IN_PROGRESS,
                num_rounds=0,
            )

    def test_invalid_num_rounds_negative(self):
        with pytest.raises(
            ValueError, match="Number of rounds cannot be less than or equal to 0."
        ):
            new_difficulty = Difficulty(
                mode=DifficultyEnum.NORMAL, max_turns=1, num_holes=1, num_colors=1
            )
            new_game = Game(
                is_multiplayer=False,
                difficulty=new_difficulty,
                status=StatusEnum.IN_PROGRESS,
                num_rounds=-1,
            )


class TestRoundModel:
    def test_secret_code_not_array(self):
        with pytest.raises(
            ValueError,
            match="Secret code is in incorrect format \\(should be json encoded list of integers\\).",
        ):
            new_difficulty = Difficulty(
                mode=DifficultyEnum.NORMAL, max_turns=10, num_holes=4, num_colors=8
            )
            new_game = Game(
                is_multiplayer=False,
                difficulty=new_difficulty,
                status=StatusEnum.IN_PROGRESS,
                num_rounds=4,
            )
            secret_code = json.dumps("a,b,c")
            new_round = Round(
                game=new_game,
                status=StatusEnum.IN_PROGRESS,
                round_num=1,
                secret_code=secret_code,
            )

    def test_secret_code_not_numbers(self):
        with pytest.raises(
            ValueError,
            match="Secret code is in incorrect format \\(should be json encoded list of integers\\).",
        ):
            new_difficulty = Difficulty(
                mode=DifficultyEnum.NORMAL, max_turns=10, num_holes=4, num_colors=8
            )
            new_game = Game(
                is_multiplayer=False,
                difficulty=new_difficulty,
                status=StatusEnum.IN_PROGRESS,
                num_rounds=4,
            )
            secret_code = json.dumps(["a", "b", "c", "d"])
            new_round = Round(
                game=new_game,
                status=StatusEnum.IN_PROGRESS,
                round_num=1,
                secret_code=secret_code,
            )

    def test_secret_code_invalid_inputs(self):
        with pytest.raises(
            ValueError,
            match="Secret code is invalid \\(one or more numbers is not possible\\).",
        ):
            new_difficulty = Difficulty(
                mode=DifficultyEnum.NORMAL, max_turns=10, num_holes=4, num_colors=8
            )
            new_game = Game(
                is_multiplayer=False,
                difficulty=new_difficulty,
                status=StatusEnum.IN_PROGRESS,
                num_rounds=4,
            )
            secret_code = json.dumps([8, 4, 4, 4])
            new_round = Round(
                game=new_game,
                status=StatusEnum.IN_PROGRESS,
                round_num=1,
                secret_code=secret_code,
            )

        with pytest.raises(
            ValueError,
            match="Secret code is invalid \\(one or more numbers is not possible\\).",
        ):
            new_difficulty = Difficulty(
                mode=DifficultyEnum.NORMAL, max_turns=10, num_holes=4, num_colors=8
            )
            new_game = Game(
                is_multiplayer=False,
                difficulty=new_difficulty,
                status=StatusEnum.IN_PROGRESS,
                num_rounds=4,
            )
            secret_code = json.dumps([-1, 4, 4, 4])
            new_round = Round(
                game=new_game,
                status=StatusEnum.IN_PROGRESS,
                round_num=1,
                secret_code=secret_code,
            )

    def test_valid_input(self):
        new_difficulty = Difficulty(
            mode=DifficultyEnum.NORMAL, max_turns=10, num_holes=4, num_colors=8
        )
        new_game = Game(
            is_multiplayer=False,
            difficulty=new_difficulty,
            status=StatusEnum.IN_PROGRESS,
            num_rounds=4,
        )
        secret_code = json.dumps([1, 1, 1, 1])
        new_round = Round(
            game=new_game,
            status=StatusEnum.IN_PROGRESS,
            round_num=1,
            secret_code=secret_code,
        )
        assert new_round


class TestTurnModel:
    def setup_round(self, num_holes, num_colors):
        secret_code = json.dumps([1, 1, 1, 1])
        new_difficulty = Difficulty(
            mode=DifficultyEnum.NORMAL,
            max_turns=10,
            num_holes=num_holes,
            num_colors=num_colors,
        )
        new_game = Game(
            is_multiplayer=False,
            difficulty=new_difficulty,
            status=StatusEnum.IN_PROGRESS,
            num_rounds=4,
        )
        new_round = Round(
            game=new_game,
            status=StatusEnum.IN_PROGRESS,
            round_num=1,
            secret_code=secret_code,
        )
        return new_round

    def test_guess_not_correct_format(self):
        new_round = self.setup_round(4, 8)
        with pytest.raises(
            ValueError,
            match="Guess is in invalid format \\(should be json encoded list of integers\\)",
        ):
            new_guess = json.dumps("a, b, c")
            new_turn = Turn(round=new_round, turn_num=1, guess=new_guess)

        with pytest.raises(
            ValueError,
            match="Guess is in invalid format \\(should be json encoded list of integers\\)",
        ):
            new_guess = json.dumps(["a", "b", "c", "d"])
            new_turn = Turn(round=new_round, turn_num=1, guess=new_guess)

    def test_guess_not_match_num_holes(self):
        new_round = self.setup_round(4, 8)
        with pytest.raises(
            ValueError,
            match="Guess is invalid \\(does not match number of holes\\).",
        ):
            new_guess = json.dumps([1, 1, 1, 1, 1])
            new_turn = Turn(round=new_round, turn_num=1, guess=new_guess)

    def test_guess_not_match_valid_choices(self):
        new_round = self.setup_round(4, 8)
        with pytest.raises(
            ValueError,
            match="Guess is invalid \\(one or more numbers is not possible\\).",
        ):
            new_guess = json.dumps([1, 1, 1, 8])
            new_turn = Turn(round=new_round, turn_num=1, guess=new_guess)

        with pytest.raises(
            ValueError,
            match="Guess is invalid \\(one or more numbers is not possible\\).",
        ):
            new_guess = json.dumps([1, 1, -1, 7])
            new_turn = Turn(round=new_round, turn_num=1, guess=new_guess)

    def test_guess_valid_input(self):
        new_round = self.setup_round(4, 8)
        new_guess = json.dumps([1, 1, 1, 7])
        new_turn = Turn(round=new_round, turn_num=1, guess=new_guess)
        assert new_turn

    def test_result_not_match_format(self):
        new_round = self.setup_round(4, 8)
        new_guess = json.dumps([1, 1, 1, 7])
        with pytest.raises(
            ValueError,
            match="Result is in invalid format \\(should be json encoded list of black_pegs and white_pegs\\).",
        ):
            result = "black_pegs: 1, white_pegs: 2"
            new_turn = Turn(round=new_round, turn_num=1, guess=new_guess, result=result)

        with pytest.raises(
            ValueError,
            match="Result is in invalid format \\(should be json encoded list of black_pegs and white_pegs\\).",
        ):
            result = "black_pegs: 1, white_pegs: 2"
            new_turn = Turn(round=new_round, turn_num=1, guess=new_guess, result=result)

    def test_result_invalid_input(self):
        new_round = self.setup_round(4, 8)
        new_guess = json.dumps([1, 1, 1, 7])
        with pytest.raises(
            ValueError,
            match="Number of pegs is invalid.",
        ):
            result = json.dumps({"black_pegs": -1, "white_pegs": 2})
            new_turn = Turn(round=new_round, turn_num=1, guess=new_guess, result=result)

        with pytest.raises(
            ValueError,
            match="White and black pegs exceed number of holes.",
        ):
            result = json.dumps({"black_pegs": 3, "white_pegs": 2})
            new_turn = Turn(round=new_round, turn_num=1, guess=new_guess, result=result)

    def test_result_matches_format(self):
        new_round = self.setup_round(4, 8)
        result = json.dumps({"black_pegs": 1, "white_pegs": 2})
        new_guess = json.dumps([1, 1, 1, 1])
        new_turn = Turn(round=new_round, turn_num=1, guess=new_guess, result=result)
        assert new_turn
