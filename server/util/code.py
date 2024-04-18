import json
import requests


def get_random_secret_code(num_holes, num_colors):
    params = {
        "num": num_holes,
        "min": 0,
        "max": num_colors - 1,
        "col": 1,
        "base": 10,
        "format": "plain",
    }
    random_code = requests.get(
        "https://www.random.org/integers", params=params
    ).text.split("\n")[:-1]
    random_code = json.dumps(list(map(int, random_code)))
    return random_code
