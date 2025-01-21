from functools import wraps
from flask import request, redirect, url_for, session, flash
from app.services.subscription import has_subscription_active
from app.utils.database import get_subscriptions_collection


def subscription_required(subscription_type):
    """
    A decorator to check if the user has the required subscription type.
    :param subscription_type: The required subscription type (string or list of types).
    :return: A redirect if the subscription is not valid, or allows access to the view.
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Ensure subscription_type is a list for easier validation
            required_types = (
                [subscription_type]
                if isinstance(subscription_type, str)
                else subscription_type
            )

            # Check if the user is logged in
            if not session.get("logged_in"):
                return redirect(url_for("app.login", next=request.url))

            # Get the user ID from the session
            user_id = session.get("user_id")
            if not user_id:
                return redirect(url_for("app.login"))

            # Check the user's subscription status and type
            is_active, message = has_subscription_active(user_id)
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

            user_subscription_type = user_subscription.get("subscription_type")

            # Allow access if user has a premium subscription
            if user_subscription_type == "premium":
                return f(*args, **kwargs)

            # Check if the user's subscription type is in the required types
            if user_subscription_type not in required_types:
                flash(
                    f"{', '.join(map(str.capitalize, required_types))} subscription required.",
                    "warning",
                )
                return redirect(request.referrer or url_for("app.subscription"))

            return f(*args, **kwargs)  # Access allowed if the subscription is valid

        return decorated_function

    return decorator
