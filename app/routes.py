from flask import Blueprint
from app.controller import handle_subscription

app_bp = Blueprint("app", __name__)

app_bp.route("/subscription", methods=["GET"])(handle_subscription)
