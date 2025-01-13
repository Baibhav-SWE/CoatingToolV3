from flask import request, render_template, url_for, redirect, session
from app.decorators import login_required
from app.services.subscription import (
    is_subscription_active,
    is_trial_taken,
    start_trial,
)
from app.utils.database import get_users_collection, get_subscriptions_collection


@login_required
def subscription():
    # Retrieve user_id from session
    user_id = session.get("user_id")

    # Check if user_id exists in session
    if not user_id:
        return redirect(url_for("app.login"))

    # Check subscription status
    status, message = is_subscription_active(user_id)
    print(status, message)

    # If subscription is inactive, redirect to subscription page
    if not status:
        return render_template("pages/subscription.html", message=message)

    # If subscription is active, redirect to materials page
    return redirect(url_for("app.materials"))


@login_required
def activate_trial():
    user_id = session.get("user_id")
    is_taken, message = is_trial_taken(user_id)
    print(is_taken, message)
    if is_taken:
        return redirect(url_for("app.subscription", error=message))

    is_start, message = start_trial(user_id)
    if not is_start:
        return redirect(url_for("app.subscription", error=message))
    return redirect(url_for("app.materials"))
