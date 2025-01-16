from flask import request, jsonify
from app.services.subscription import check_valid_product
from app.services.payment import create_payment
from app.utils.database import get_users_collection
from .services import get_required_data_from_webhook_order_fulfillment


def handle_order_fulfillment():
    order_data = get_required_data_from_webhook_order_fulfillment(request.json)
    if order_data is None:
        return jsonify({"message": "Order data is missing"}), 400
    is_valid_product = check_valid_product(str(order_data["product_id"]))
    if not is_valid_product:
        return jsonify({"message": "Successful"}), 200

    user_collection = get_users_collection()
    user = user_collection.find_one({"email": order_data["email"]})
    if user is None:
        return jsonify({"message": "User not found"}), 404
    created, message = create_payment(user["_id"], order_data)
    if not created:
        return jsonify({"message": message}), 400
    return jsonify({"message": "Order Fulfilled"}), 200
