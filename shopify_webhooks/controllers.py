from flask import request, jsonify
from app.services.subscription import create_subscription, check_valid_product
from app.utils.database import get_users_collection
from .services import get_required_data_from_webhook_order_fulfillment


def handle_product_create():
    product_data = request.json
    print("Product Data:", product_data)
    return jsonify({"message": "Product Created"}), 200


def handle_product_delete():
    product_data = request.json
    print("Product Data:", product_data)
    return jsonify({"message": "Product Deleted"}), 200


def handle_order_fulfillment():
    print("Order Data:", request.json)
    order_data = get_required_data_from_webhook_order_fulfillment(request.json)
    if order_data is None:
        return jsonify({"message": "Order data is missing"}), 400
    is_valid_product = check_valid_product(str(order_data["product_id"]))
    print("is_valid_product:", is_valid_product)
    if not is_valid_product:
        return jsonify({"message": "Successful"}), 200

    user_collection = get_users_collection()
    user = user_collection.find_one({"email": order_data["email"]})
    if user is None:
        return jsonify({"message": "User not found"}), 404
    created, message = create_subscription(user["_id"], order_data)
    print("Subscription Data:", message)
    if not created:
        return jsonify({"message": message}), 400
    return jsonify({"message": "Order Fulfilled"}), 200
