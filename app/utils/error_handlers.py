from flask import jsonify, request


def register_error_handlers(app):
    @app.errorhandler(404)
    def handle_404(error):
        # Check if the route starts with '/api'
        if request.path.startswith("/api/"):
            return (
                jsonify(
                    {
                        "error": "Not Found",
                        "message": f"The endpoint {request.path} does not exist.",
                    }
                ),
                404,
            )
        # Default behavior for non-API routes
        return error

    @app.errorhandler(500)
    def handle_500(error):
        return (
            jsonify(
                {
                    "error": "Internal Server Error",
                    "message": "An unexpected error occurred. Please try again later.",
                }
            ),
            500,
        )
