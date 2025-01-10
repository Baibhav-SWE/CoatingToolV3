from flask import current_app as app
from datetime import datetime, timezone, timedelta
from app.utils.database import get_subscriptions_collection


def is_subscription_active(user_id):
    """
    Check if the user has a single active subscription that has not expired.
    :param user_id: ID of the user making the request.
    :return: A tuple (bool, str) indicating the subscription status and a message.
    """
    subscriptions_collection = get_subscriptions_collection()

    # Fetch the active subscription for the user
    current_date = datetime.now(timezone.utc)  # Timezone-aware UTC datetime
    subscription = subscriptions_collection.find_one(
        {
            "user_id": user_id,
            "status": "active",
            "end_date": {
                "$gte": current_date.isoformat()
            },  # Ensure end_date is not expired
        }
    )

    if not subscription:
        return False, "No active subscription found or the subscription has expired."

    return True, "Subscription is active."


def is_trial_taken(user_id):
    """
    Check if the user has already activated a trial subscription.
    :param user_id: ID of the user making the request.
    :return: A tuple (bool, str) indicating the subscription status and a message.
    """
    subscriptions_collection = get_subscriptions_collection()

    # Fetch the active subscription for the user
    subscription = subscriptions_collection.find_one(
        {
            "user_id": user_id,
            "subscription_type": "trial",
        }
    )
    if subscription:
        return True, "Trial already activated."

    return False, "Trial is not activated."


def start_trial(user_id):
    """
    Activate a trial subscription for the user.
    :param user_id: ID of the user making the request.
    :return: A tuple (bool, str) indicating the subscription status and a message.
    """
    try:
        subscriptions_collection = get_subscriptions_collection()
        subscriptions_collection.insert_one(
            {
                "user_id": user_id,
                "subscription_type": "trial",
                "status": "active",
                "start_date": datetime.now(timezone.utc).isoformat(),
                "end_date": (
                    datetime.now(timezone.utc) + timedelta(days=7)
                ).isoformat(),
            }
        )

        return True, "Trial activated successfully."
    except Exception as e:
        return False, "An error occurred while activating the trial subscription."


def check_valid_product(product_id):
    return product_id in [
        app.config.get("BASIC_PRODUCT_ID"),
        app.config.get("PREMIUM_PRODUCT_ID"),
    ]


def get_subscription_type(product_id):
    return "basic" if product_id == app.config.get("BASIC_PRODUCT_ID") else "premium"


def create_subscription(user_id, order_data):
    try:
        subscriptions_collection = get_subscriptions_collection()

        # Check if an active subscription exists
        existing_subscription = subscriptions_collection.find_one(
            {"user_id": user_id, "status": "active"}
        )

        if existing_subscription:
            # Set the existing active subscription to "expired"
            subscriptions_collection.find_one_and_update(
                {"_id": existing_subscription["_id"]}, {"$set": {"status": "expired"}}
            )

        # Proceed to create the new subscription
        subscription_type = get_subscription_type(order_data["product_id"])

        subscriptions_collection.insert_one(
            {
                "user_id": user_id,
                "subscription_type": subscription_type,
                "product_id": order_data["product_id"],
                "price": order_data["total_price"],
                "product_title": order_data["product_title"],
                "status": "active",
                "start_date": datetime.now(timezone.utc).isoformat(),
                "end_date": (
                    datetime.now(timezone.utc)
                    + timedelta(
                        days=(
                            365
                            if order_data["subscription_duration"] == "Yearly"
                            else 30
                        )
                    )
                ).isoformat(),
            }
        )
        return True, "Subscription created successfully."
    except Exception as e:
        return False, f"An error occurred while creating the subscription: {str(e)}"
