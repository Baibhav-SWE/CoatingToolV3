from flask import Blueprint
from shopify_webhooks.controllers import (
    handle_order_fulfillment,
)
from shopify_webhooks.middlewares import validate_shopify_webhook

shopify_bp = Blueprint("shopify", __name__)

shopify_bp.route("/order/fulfillment", methods=["POST"])(
    validate_shopify_webhook(handle_order_fulfillment)
)
