from flask import request, jsonify, current_app
from functools import wraps
from shopify_webhooks.utils import validate_shopify_hmac


def validate_shopify_webhook(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Get the Shopify shared secret from the configuration
        shared_secret = current_app.config["SHOPIFY_SHARED_SECRET"]

        # Validate the webhook
        if not validate_shopify_hmac(request, shared_secret):
            return jsonify({"error": "Unauthorized request"}), 401

        return func(*args, **kwargs)

    return wrapper
