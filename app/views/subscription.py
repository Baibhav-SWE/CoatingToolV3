from flask import (
    request,
    render_template,
    url_for,
    redirect,
    session,
    current_app as app,
)
from app.decorators import login_required
from app.services.subscription import (
    has_subscription_active,
    is_trial_taken,
    start_trial,
)


def create_checkout_url(product_variant_id, email=""):
    return f"https://intelladapt.myshopify.com/cart/{product_variant_id}:1?channel=buy_button&checkout[email]={email}"


def get_checkout_urls(email=""):
    return {
        "basic": {
            "monthly": create_checkout_url(
                app.config.get("BASIC_PRODUCT_MONTHLY_BUY_ID"), email
            ),
            "yearly": create_checkout_url(
                app.config.get("BASIC_PRODUCT_YEARLY_BUY_ID"), email
            ),
        },
        "premium": {
            "monthly": create_checkout_url(
                app.config.get("PREMIUM_PRODUCT_MONTHLY_BUY_ID"), email
            ),
            "yearly": create_checkout_url(
                app.config.get("PREMIUM_PRODUCT_YEARLY_BUY_ID"), email
            ),
        },
    }


@login_required
def subscription():
    # Retrieve user_id from session
    user_id = session.get("user_id")

    # Check subscription status
    status, message = has_subscription_active(user_id)

    # If subscription is inactive, redirect to subscription page
    if not status:
        return render_template("private/subscription.html", message=message, first_name=session.get("first_name"))

    # If subscription is active, redirect to materials page
    return redirect(url_for("app.index"))


@login_required
def activate_trial():
    user_id = session.get("user_id")
    is_taken, message = is_trial_taken(user_id)
    if is_taken:
        return redirect(url_for("app.subscription", error=message))

    is_start, message = start_trial(user_id)
    if not is_start:
        return redirect(url_for("app.subscription", error=message))
    return redirect(url_for("app.materials"))


@login_required
def checkout():
    data = request.form
    checkout_urls = get_checkout_urls(session.get("email"))
    if not data["type"] or not data["plan"]:
        return redirect(url_for("app.subscription", error="Invalid subscription plan."))
    return redirect(checkout_urls[data["type"]][data["plan"]])
