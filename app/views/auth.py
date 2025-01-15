from flask import request, render_template, url_for, redirect, session, flash, jsonify
from app.utils.database import get_users_collection
from werkzeug.security import generate_password_hash, check_password_hash
from app.services.subscription import is_subscription_active
from flask_mail import Message
import time
import smtplib
from random import randint
from main import mail

users = get_users_collection()

# Temporary storage for OTPs (use a database or Redis in production)
otp_storage = {}

def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # Find user by email
        user = users.find_one({"email": email})
        if user and check_password_hash(user["password"], password):
            session["logged_in"] = True
            session["user_id"] = str(
                user["_id"]
            )  # Store user ID as string for JSON serialization
            session["email"] = email
            session["first_name"] = user["name"].split()[0]  # Extract the first name

            # Check if the user has an active subscription
            is_active, message = is_subscription_active(user["_id"])
            if not is_active:
                flash(message, "warning")
                return redirect(
                    url_for("app.subscription")
                )  # Redirect to subscription page

            # Redirect to the original page or materials page
            next_page = request.args.get("next", url_for("app.materials"))
            return redirect(next_page)
        else:
            return render_template("auth/login.html", error="Invalid email or password")
    return render_template("auth/login.html")


def logout():
    session.pop("logged_in", None)
    session.pop("email", None)
    session.pop("first_name", None)
    session.clear()
    return redirect(url_for("app.login"))


def register():
    if request.method == "POST":
        first_name = request.form["firstName"]
        last_name = request.form["lastName"]
        name = first_name + " " + last_name
        email = request.form["signUpEmail"].strip().lower()
        password = request.form["signUpPassword"]
        confirm_password = request.form["confirmPassword"]

        # Check if passwords match
        if password != confirm_password:
            return render_template("auth/register.html", error="Passwords do not match")

        # Check if the email already exists
        users_collection = get_users_collection()
        existing_user = users_collection.find_one({"email": email})
        if existing_user:
            return render_template("auth/register.html", error="Email already in use")

        # Hash the password and create the user
        hashed_password = generate_password_hash(password)
        new_user = {
            "name": name,
            "email": email,
            "password": hashed_password,
            "subscription_id": None,  # Subscription will be assigned after registration
        }

        # Insert the new user into the database
        user_id = users_collection.insert_one(new_user).inserted_id

        # Set session variables
        session["logged_in"] = True
        session["user_id"] = str(user_id)  # Storing user ID in session
        session["email"] = email
        session["first_name"] = first_name
        # Redirect to the subscription page if no active subscription is found
        return redirect(url_for("app.subscription"))

    return render_template("auth/register.html")


def send_otp():
    data = request.json
    email = data.get("email")
    if not email:
        return jsonify({"error": "Email is required"}), 400

    # Check if an OTP was already sent recently
    if email in otp_storage and time.time() < otp_storage[email]["expires"] - 300 + 60:
        return (
            jsonify({"error": "Please wait a minute before requesting another OTP."}),
            429,
        )

    otp = randint(100000, 999999)  # Generate a 6-digit OTP
    otp_storage[email] = {
        "otp": otp,
        "expires": time.time() + 300,
    }  # Store OTP for 5 minutes

    print(f"Sending OTP to email {email}")  # Avoid printing sensitive data

    try:
        msg = Message(
            "Your OTP Code", sender="your_email@example.com", recipients=[email]
        )
        msg.body = f"Your OTP code is {otp}. It is valid for 5 minutes."
        mail.send(msg)
        return jsonify({"message": "OTP sent successfully"}), 200
    except smtplib.SMTPException as smtp_error:
        print(f"SMTP error occurred: {smtp_error}")
        return jsonify({"error": "SMTP error occurred"}), 500
    except Exception as e:
        print(f"General error sending OTP: {str(e)}")
        return jsonify({"error": str(e)}), 500


def verify_otp():
    data = request.json
    email = data.get("email")
    otp = data.get("otp")

    if not email or not otp:
        return jsonify({"error": "Email and OTP are required"}), 400

    if email not in otp_storage:
        return jsonify({"error": "Invalid or expired OTP"}), 400

    stored_otp = otp_storage[email]
    if time.time() > stored_otp["expires"]:
        del otp_storage[email]  # Clean up expired OTP
        return jsonify({"error": "OTP has expired"}), 400

    try:
        if int(otp) == stored_otp["otp"]:
            del otp_storage[email]  # Remove OTP after successful verification
            return jsonify({"message": "OTP verified successfully"}), 200
        else:
            return jsonify({"error": "Invalid OTP"}), 400
    except ValueError:
        return jsonify({"error": "OTP must be a numeric value."}), 400


def reset_password():
    email = (
        request.form["email"].strip().lower()
    )  # Normalize to lowercase and strip spaces
    new_password = request.form["new_password"]
    confirm_password = request.form["confirm_password"]

    if new_password != confirm_password:
        return jsonify({"error": "Passwords do not match"}), 400

    hashed_password = generate_password_hash(new_password)

    # Debugging: Log the input email
    print(f"Input email (trimmed and lowercase): '{email}'")

    # Debugging: Print all emails in the database
    print("Database emails:")
    for user in users.find({}):
        print(f"Stored email: '{user['email']}'")

    # Perform the update query
    result = users.update_one(
        {"email": email}, {"$set": {"password": hashed_password}}  # Exact match
    )

    if result.matched_count > 0:
        print("Password updated successfully for:", email)
        return jsonify({"message": "Password updated successfully"}), 200
    else:
        print("Email not found in query:", email)
        return jsonify({"error": "Email not found"}), 404

