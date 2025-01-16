def get_required_data_from_webhook_order_fulfillment(order_fulfillment):
    try:
        return {
            "order_id": order_fulfillment["id"],
            "fulfillment_status": order_fulfillment["fulfillment_status"],
            "email": order_fulfillment["customer"]["email"],
            "product_id": str(
                order_fulfillment["fulfillments"][0]["line_items"][0]["product_id"]
            ),
            "plan_duration": order_fulfillment["fulfillments"][0]["line_items"][0][
                "variant_title"
            ],
            "total_price": order_fulfillment["fulfillments"][0]["line_items"][0][
                "price"
            ],
            "product_title": order_fulfillment["fulfillments"][0]["line_items"][0][
                "title"
            ],
        }
    except KeyError:
        return None
