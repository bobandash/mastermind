from flask import jsonify


class ErrorResponse:
    # TODO: Handle other common error codes in the future
    @staticmethod
    def handle_error(message, status_code):
        error_codes = {
            400: "badRequest",
            401: "unauthorized",
            403: "forbidden",
            404: "notFound",
            415: "unsupportedMedia",
            500: "serverError",
            503: "serviceUnavailable",  # Generally for failed query operations
        }
        error_code = error_codes.get(status_code, "notHandled")
        return (
            jsonify(
                {
                    "error": {
                        "code": error_code,
                        "message": message,
                    }
                }
            ),
            status_code,
        )
