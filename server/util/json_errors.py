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
    def not_found(message):
        return (
            jsonify(
                {
                    "error": {
                        "code": "notFound",
                        "message": message,
                    }
                }
            ),
            404,
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
                        "code": "serverError",
                        "message": message,
                    }
                }
            ),
            500,
        )

    @staticmethod
    def unexpected_error(message, status_code):
        return (
            jsonify(
                {
                    "error": {
                        "code": "notHandled",
                        "message": message,
                    }
                }
            ),
            status_code,
        )
