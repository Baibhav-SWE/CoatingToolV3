from flask import request, render_template


def handle_subscription():
    return render_template("/pages/subscription.html")
