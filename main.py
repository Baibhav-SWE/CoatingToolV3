from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
    session,
    send_file,
    flash,
)
import numpy as np
import json
from io import BytesIO
import os
import pandas as pd
from set_stack import set_stack
from ATR1D import ATR1D
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from get_electric import get_electric
from flask import Flask, jsonify, request
from random import randint
from flask_mail import Mail, Message
import time
import smtplib
from scipy.optimize import differential_evolution
from color_chart import plot_color_chart
from email.mime.text import MIMEText
from shopify_webhooks.routes import shopify_bp
from app.routes import app_bp
from app.utils.database import init_db, get_db, get_users_collection
from app.services.subscription import is_subscription_active


app = Flask(__name__, static_url_path="/static")
app.secret_key = "your_secure_secret_key"  # Secret key for session management

app.config.from_object("config.Config")

# MongoDB setup
init_db(app)

app.register_blueprint(shopify_bp, url_prefix="/webhooks/shopify")
app.register_blueprint(app_bp, url_prefix="/")

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False, host="0.0.0.0", port=5500)
