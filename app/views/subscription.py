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
    is_subscription_active,
    is_trial_taken,
    start_trial,
)


def create_checkout_url(product_variant_id):
    return f"https://intelladapt.myshopify.com/cart/{product_variant_id}:1?channel=buy_button"


def get_checkout_urls():
    return {
        "basic": {
            "monthly": create_checkout_url(
                app.config.get("BASIC_PRODUCT_MONTHLY_BUY_ID")
            ),
            "yearly": create_checkout_url(
                app.config.get("BASIC_PRODUCT_YEARLY_BUY_ID")
            ),
        },
        "premium": {
            "monthly": create_checkout_url(
                app.config.get("PREMIUM_PRODUCT_MONTHLY_BUY_ID")
            ),
            "yearly": create_checkout_url(
                app.config.get("PREMIUM_PRODUCT_YEARLY_BUY_ID")
            ),
        },
    }


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
    if is_taken:
        return redirect(url_for("app.subscription", error=message))

    is_start, message = start_trial(user_id)
    if not is_start:
        return redirect(url_for("app.subscription", error=message))
    return redirect(url_for("app.materials"))


@login_required
def checkout():
    data = request.form
    checkout_urls = get_checkout_urls()
    if not data["type"] or not data["plan"]:
        return redirect(url_for("app.subscription", error="Invalid subscription plan."))
    return redirect(checkout_urls[data["type"]][data["plan"]])
