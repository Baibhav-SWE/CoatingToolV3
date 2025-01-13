from flask import request, render_template, url_for, redirect, session, jsonify
from email.mime.text import MIMEText
import smtplib

def frontpage():
    return render_template("pages/frontpage.html")

def feedback_form():
    return render_template("pages/feedback.html")

# Route to handle feedback submission and send email
def send_feedback():
    feedback = request.form["feedback"]

    # Email configuration
    sender_email = "your_email@example.com"  # Replace with your email
    sender_password = "your_email_password"  # Replace with your email's password
    recipient_email = "ashelke@adaptivewaves.com"

    subject = "New Feedback Received"
    message_body = f"Feedback:\n{feedback}"

    # Sending email
    msg = MIMEText(message_body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = recipient_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
        return jsonify(
            {"status": "success", "message": "Feedback received. Thank you!"}
        )
    except Exception as e:
        print(f"Error sending email: {e}")
        return jsonify(
            {"status": "error", "message": "Failed to send feedback. Please try again."}
        )