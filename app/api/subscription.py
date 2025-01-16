from flask import jsonify, session
from app.decorators import login_required
from app.services.subscription import has_subscription_active
from . import api


@api.route("/has-active-subscription", methods=["GET"])
@login_required
def has_active_subscription():
    is_active, message = has_subscription_active(session.get("user_id"))
    return jsonify({"is_active": is_active, "message": message}), 200
