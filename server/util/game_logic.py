def is_guess_proper_format(guess, secret_code, num_colors):
    if len(secret_code) != len(guess):
        return False
    if not all([isinstance(g, int) for g in guess]):
        return False
    if max(guess) >= num_colors or min(guess) < 0:
        return False
    return True


def calculate_result(guess, secret_code):
    black_pegs = 0
    white_pegs = 0
    remaining_pegs_guess = {}
    remaining_pegs_secret_code = {}
    for i in range(len(guess)):
        if guess[i] == secret_code[i]:
            black_pegs += 1
        else:
            remaining_pegs_guess[guess[i]] = remaining_pegs_guess.get(guess[i], 0) + 1
            remaining_pegs_secret_code[secret_code[i]] = (
                remaining_pegs_secret_code.get(secret_code[i], 0) + 1
            )

    for key in remaining_pegs_guess.keys():
        if key in remaining_pegs_secret_code:
            white_pegs += min(
                remaining_pegs_guess[key], remaining_pegs_secret_code[key]
            )
    won_round = black_pegs == len(guess)
    correct_numbers = white_pegs + black_pegs
    is_plural = correct_numbers > 1
    if not white_pegs and not black_pegs:
        message = "All incorrect."
    else:
        message = f"{correct_numbers} correct number{'s' if is_plural else ''} and {black_pegs} correct location"
    return {
        "won_round": won_round,
        "black_pegs": black_pegs,
        "white_pegs": white_pegs,
        "message": message,
    }
