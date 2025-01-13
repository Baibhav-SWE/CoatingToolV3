from functools import wraps
from flask import request, redirect, url_for, session, flash
from app.services.subscription import is_subscription_active
from app.utils.database import get_subscriptions_collection


def subscription_required(subscription_type):
    """
    A decorator to check if the user has the required subscription type.
    :param subscription_type: The required subscription type ('basic' or 'premium').
    :return: A redirect if the subscription is not valid, or allows access to the view.
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if the user is logged in
            if not session.get("logged_in"):
                return redirect(url_for("app.login", next=request.url))

            # Get the user ID from the session
            user_id = session.get("user_id")
            if not user_id:
                return redirect(url_for("app.login"))

            # Check the user's subscription status and type
            is_active, message = is_subscription_active(user_id)
            if not is_active:
                flash(message, "warning")
                return redirect(
                    url_for("app.subscription")
                )  # Redirect to subscription page

            # Get the user's subscription type
            subscriptions_collection = get_subscriptions_collection()
            user_subscription = subscriptions_collection.find_one({"user_id": user_id})

            if not user_subscription:
                flash("No subscription found.", "warning")
                return redirect(url_for("app.subscription"))

            # Check if the user has the required subscription type
            if user_subscription.get("subscription_type") != subscription_type:
                flash(
                    f"{subscription_type.capitalize()} subscription required.",
                    "warning",
                )
                return redirect(url_for("app.subscription"))

            return f(*args, **kwargs)  # Access allowed if the subscription is valid

        return decorated_function

    return decorator
