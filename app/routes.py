from flask import Blueprint
from app.views import subscription, activate_trial

app_bp = Blueprint("app", __name__)

app_bp.route("/subscription", endpoint="subscription", methods=["GET"])(subscription)
app_bp.route(
    "/subscription/activate-trial", endpoint="activate_trial", methods=["GET"]
)(activate_trial)
