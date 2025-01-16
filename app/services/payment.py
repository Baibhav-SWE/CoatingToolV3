from flask import current_app as app
from datetime import datetime, timezone
from app.utils.database import get_payments_collection


def get_plan_type(product_id):
    return "premium" if product_id == app.config.get("PREMIUM_PRODUCT_ID") else "basic"


def create_payment(user_id, order_data):
    try:
        payments_collection = get_payments_collection()

        payments_collection.insert_one(
            {
                "user_id": user_id,  # Ensure user_id is stored as ObjectId
                "plan_type": get_plan_type(order_data["product_id"]),
                "product_id": order_data["product_id"],
                "price": order_data["total_price"],
                "product_title": order_data["product_title"],
                "status": "pending",
                "duration": order_data["plan_duration"],
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            }
        )
        return True, "Subscription created successfully."
    except Exception as e:
        return False, f"An error occurred while creating the subscription: {str(e)}"


def get_pending_payment(user_id):
    payments_collection = get_payments_collection()
    return payments_collection.find_one(
        {
            "user_id": user_id,
            "status": "pending",
        }
    )


def update_payment(payment_id, data):
    payments_collection = get_payments_collection()
    return payments_collection.find_one_and_update(
        {"_id": payment_id},
        {"$set": data},
    )
