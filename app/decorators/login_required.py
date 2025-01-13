from functools import wraps
from flask import request, redirect, url_for, session


def login_required(f):
    """
    A decorator to check if the user is authenticated.
    If not, redirect to the login page.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in"):  # Check if user is logged in
            return redirect(
                url_for("app.login", next=request.url)
            )  # Redirect to login page
        return f(*args, **kwargs)  # Call the original view function if authenticated

    return decorated_function
