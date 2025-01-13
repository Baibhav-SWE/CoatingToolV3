from flask import Blueprint
from app.views import subscription, activate_trial, frontpage, feedback_form, send_feedback, login, logout, register, send_otp, verify_otp, reset_password, index, welcome, help, materials, get_materials, preview_material, delete_material, upload_material, optimize, save_targets, calculate, public_designs, get_public_designs, save_design, get_user_designs, load_design, delete_design, get_layers, get_color_chart

app_bp = Blueprint("app", __name__)

app_bp.route("/login", endpoint="login", methods=["GET", "POST"])(login)
app_bp.route("/logout", endpoint="logout", methods=["GET"])(logout)
app_bp.route("/register", endpoint="register", methods=["GET", "POST"])(register)
app_bp.route("/send-otp", endpoint="send-otp", methods=["POST"])(send_otp)
app_bp.route("/verify-otp", endpoint="verify-otp", methods=["POST"])(verify_otp)
app_bp.route("/reset_password", endpoint="reset_password", methods=["POST"])(reset_password)

app_bp.route("/frontpage", endpoint="frontpage", methods=["GET"])(frontpage)
app_bp.route("/feedback.html", endpoint="feedback", methods=["GET"])(feedback_form)
app_bp.route("/feedback.html", endpoint="send_feedback", methods=["POST"])(send_feedback)

app_bp.route("/", endpoint="index", methods=["GET"])(index)
app_bp.route("/welcome", endpoint="welcome", methods=["GET", "POST"])(welcome)
app_bp.route("/help", endpoint="help", methods=["GET", "POST"])(help)
app_bp.route("/materials", endpoint="materials", methods=["GET", "POST"])(materials)
app_bp.route("/get_materials", endpoint="get_materials", methods=["GET"])(get_materials)
app_bp.route("/preview_material", endpoint="preview_material", methods=["GET"])(preview_material)
app_bp.route("/delete_material", endpoint="delete_material", methods=["DELETE"])(delete_material)
app_bp.route("/upload_material", endpoint="upload_material", methods=["POST"])(upload_material)
app_bp.route("/optimize", endpoint="optimize", methods=["POST"])(optimize)
app_bp.route("/save_targets", endpoint="save_targets", methods=["POST"])(save_targets)
app_bp.route("/calculate", endpoint="calculate", methods=["POST"])(calculate)
app_bp.route("/public_designs", endpoint="public_designs", methods=["GET"])(public_designs)
app_bp.route("/get_public_designs", endpoint="get_public_designs", methods=["GET"])(get_public_designs)
app_bp.route("/save_design", endpoint="save_design", methods=["POST"])(save_design)
app_bp.route("/get_user_designs", endpoint="get_user_designs", methods=["GET"])(get_user_designs)
app_bp.route("/load_design", endpoint="load_design", methods=["GET"])(load_design)
app_bp.route("/delete_design", endpoint="delete_design", methods=["DELETE"])(delete_design)
app_bp.route("/get_layers", endpoint="get_layers", methods=["GET"])(get_layers)
app_bp.route("/get_color_chart", endpoint="get_color_chart", methods=["POST"])(get_color_chart)

app_bp.route("/subscription", endpoint="subscription", methods=["GET"])(subscription)
app_bp.route("/subscription/activate-trial", endpoint="activate_trial", methods=["GET"])(activate_trial)
