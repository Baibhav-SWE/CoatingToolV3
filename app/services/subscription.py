from flask import current_app as app
from datetime import datetime, timezone, timedelta
from dateutil.relativedelta import relativedelta
from app.utils.database import get_subscriptions_collection, get_payments_collection
from app.services.payment import get_pending_payment, update_payment


def has_subscription_active(user_id):
    subscriptions_collection = get_subscriptions_collection()
    current_date = datetime.now(timezone.utc)  # Timezone-aware UTC datetime

    # Fetch the subscription
    subscription = subscriptions_collection.find_one({"user_id": user_id})

    if not subscription:
        payment = get_pending_payment(user_id)
        if not payment:
            return False, "Subscription has expired."
        create_subscription(user_id, payment)
        return False, "No active subscription found or the subscription has expired."

    # Ensure `end_date` is timezone-aware
    end_date = subscription.get("end_date")
    if not end_date:
        return False, "Subscription has no end date."

    if end_date.tzinfo is None:  # If naive, make it UTC-aware
        end_date = end_date.replace(tzinfo=timezone.utc)

    # Check if the subscription has expired
    if end_date < current_date:
        payment = get_pending_payment(user_id)
        if not payment:
            return False, "Subscription has expired."
        activate_subscription(user_id, payment)
        return True, "Subscription is active."

    # Check if the subscription is active
    if subscription.get("status") != "active":
        return False, "Subscription is not active."

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
        }
    )
    if subscription:
        return True, "Trial not available."

    return False, "Trial is not activated."


def start_trial(user_id):
    """
    Activate a trial subscription for the user.
    :param user_id: ID of the user making the request.
    :return: A tuple (bool, str) indicating the subscription status and a message.
    """
    try:
        subscriptions_collection = get_subscriptions_collection()
        end_date = datetime.now(timezone.utc) + timedelta(
            days=app.config.get("TRIAL_DAYS", 7)
        )
        subscription = subscriptions_collection.insert_one(
            {
                "user_id": user_id,
                "subscription_type": "trial",
                "status": "active",
                "end_date": end_date,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            }
        )

        return subscription.inserted_id, "Trial activated successfully."
    except Exception as e:
        return None, "An error occurred while activating the trial subscription."


def check_valid_product(product_id):
    return product_id in [
        app.config.get("BASIC_PRODUCT_ID"),
        app.config.get("PREMIUM_PRODUCT_ID"),
    ]


def create_subscription(user_id, payment_data):
    try:
        subscriptions_collection = get_subscriptions_collection()

        # Check if a subscription already exists for the user
        existing_subscription = subscriptions_collection.find_one({"user_id": user_id})
        if existing_subscription:
            return None, "User already has a subscription."

        # Calculate end_date based on subscription duration
        if payment_data["duration"].lower() == "monthly":
            end_date = datetime.now(timezone.utc) + relativedelta(months=1)
        elif payment_data["duration"].lower() == "yearly":
            end_date = datetime.now(timezone.utc) + relativedelta(months=12)
        else:
            return None, "Invalid subscription duration."

        # Insert the new subscription
        subscription = subscriptions_collection.insert_one(
            {
                "user_id": user_id,
                "payment_id": payment_data["_id"],
                "subscription_type": payment_data["plan_type"],
                "status": "active",
                "end_date": end_date,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            }
        )
        update_payment(
            payment_data["_id"],
            {
                "status": "used",
                "updated_at": datetime.now(timezone.utc),
            },
        )

        return subscription.inserted_id, "Subscription created successfully."
    except Exception as e:
        return None, f"An error occurred while creating the subscription: {str(e)}"


def update_subscription(user_id, payment_data):
    try:
        subscriptions_collection = get_subscriptions_collection()

        # Fetch the current subscription
        subscription = subscriptions_collection.find_one({"user_id": user_id})

        if not subscription:
            return create_subscription(user_id, payment_data)

        # Determine the starting date for the new end_date calculation
        current_end_date = subscription.get("end_date", datetime.now(timezone.utc))
        current_end_date = (
            current_end_date
            if current_end_date > datetime.now(timezone.utc)
            else datetime.now(timezone.utc)
        )

        # Calculate new end_date based on the plan's duration
        if payment_data["duration"].lower() == "monthly":
            new_end_date = current_end_date + relativedelta(months=1)
        elif payment_data["duration"].lower() == "yearly":
            new_end_date = current_end_date + relativedelta(months=12)
        else:
            return None, "Invalid subscription duration."

        # Update the subscription in the database
        updated_subscription = subscriptions_collection.find_one_and_update(
            {"user_id": user_id},
            {
                "$set": {
                    "payment_id": payment_data["_id"],
                    "end_date": new_end_date,
                    "subscription_type": payment_data["plan_type"],
                    "updated_at": datetime.now(timezone.utc),
                }
            },
            return_document=True,
        )
        update_payment(
            payment_data["_id"],
            {
                "status": "used",
                "updated_at": datetime.now(timezone.utc),
            },
        )

        return updated_subscription, "Subscription updated successfully."
    except Exception as e:
        return None, f"An error occurred while updating the subscription: {str(e)}"


def activate_subscription(user_id, payment_data):
    return update_subscription(user_id, payment_data)


def deactivate_subscription(user_id):
    try:
        subscriptions_collection = get_subscriptions_collection()

        # Fetch the current subscription
        subscription = subscriptions_collection.find_one({"user_id": user_id})

        if not subscription:
            return None, "User does not have a subscription."

        # Update the subscription in the database
        updated_subscription = subscriptions_collection.find_one_and_update(
            {"user_id": user_id},
            {
                "$set": {
                    "status": "expired",
                    "updated_at": datetime.now(timezone.utc),
                }
            },
            return_document=True,
        )

        return updated_subscription, "Subscription updated successfully."
    except Exception as e:
        return None, f"An error occurred while updating the subscription: {str(e)}"
