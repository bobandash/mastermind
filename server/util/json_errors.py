from flask import jsonify


class ErrorResponse:
    @staticmethod
    def bad_request(message):
        return (
            jsonify(
                {
                    "error": {
                        "code": "badRequest",
                        "message": message,
                    }
                }
            ),
            400,
        )

    @staticmethod
    def not_authorized(message):
        return (
            jsonify(
                {
                    "error": {
                        "code": "unauthorized",
                        "message": message,
                    }
                }
            ),
            401,
        )

    @staticmethod
    def server_error(message):
        return (
            jsonify(
                {
                    "error": {
                        "code": "server_error",
                        "message": message,
                    }
                }
            ),
            500,
        )
