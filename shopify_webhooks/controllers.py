from flask import request, jsonify


def handle_product_create():
    product_data = request.json
    print("Product Data:", product_data)
    return jsonify({"message": "Product Created"}), 200


def handle_product_delete():
    product_data = request.json
    print("Product Data:", product_data)
    return jsonify({"message": "Product Deleted"}), 200


def handle_order_fulfillment():
    order_data = request.json
    print("Order Fulfilled:", order_data)
    return jsonify({"message": "Order Fulfilled"}), 200
