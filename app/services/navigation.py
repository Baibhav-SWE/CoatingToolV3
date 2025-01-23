from flask import request, session, url_for
from app.utils.database import get_subscriptions_collection


def add_if_allowed(plan, allowed_plans, items):
    """Add items to the navigation if the plan is in the allowed plans."""
    return items if plan in allowed_plans else []


def get_nav_links():
    subscription_collections = get_subscriptions_collection()
    subscription = subscription_collections.find_one({"user_id": session["user_id"]})
    plan = subscription["subscription_type"] if subscription else None

    """Return navigation links based on the current request path."""
    nav_links = {
        "/welcome": [
            {"type": "link", "name": "Home", "url": url_for("app.welcome"), "submenu": None},
            *add_if_allowed(plan, ["basic","premium"], [
                {"type": "dropdown", "name": "Load", "url": "#", "submenu": [
                    {"name": "Open Design", "action": "redirectToIndex('openDesign')", "type": "button"},
                    {"name": "Load Material", "action": "document.getElementById('materialFileInput').click();", "type": "button"},
                ]},
            ]),
            {"type": "link", "name": "All Designs", "url": url_for("app.public_designs"), "submenu": None},
            {"type": "link", "name": "Help", "url": url_for("app.help"), "submenu": None},
        ],
        "/": [
            {"type": "link", "name": "Home", "url": url_for("app.welcome"), "submenu": None},
            *add_if_allowed(plan, ["basic","premium"], [
                {"type": "dropdown", "name": "Load", "url": "#", "submenu": [
                    {"name": "Open Design", "action": "openDesign()", "type": "button"},
                    {"name": "Load Material", "action": "document.getElementById('materialFileInput').click();", "type": "button"},
                ]},
            ]),
            {"type": "button", "name": "Save", "action": "saveDesign()"},
            *add_if_allowed(plan, ["basic","premium"], [
                {"type": "dropdown", "name": "Downloads", "url": "#", "submenu": [
                    {"name": "Graph (JPEG)", "action": "downloadGraph()", "type": "button"},
                    {"name": "Data (CSV)", "action": "downloadCSV()", "type": "button"},
                    {"name": "Data (PDF)", "action": "downloadPDF()", "type": "button"},
                    {"name": "Design (JSON)", "action": "downloadDesignJSON()", "type": "button"},
                ]},
                {"type": "dropdown", "name": "Results", "url": "#", "submenu": [
                    {"name": "Show Transmittance", "action": "showTransmittance()", "type": "button"},
                    {"name": "Show Reflectance", "action": "showReflectance()", "type": "button"},
                ]},
            ]),
            {"type": "link", "name": "All Designs", "url": url_for("app.public_designs"), "submenu": None},
            {"type": "link", "name": "Help", "url": url_for("app.help"), "submenu": None},
        ],
        "/help": [
            {"type": "link", "name": "Home", "url": url_for("app.welcome"), "submenu": None},
            *add_if_allowed(plan, ["basic","premium"], [
                {"type": "link", "name": "Load Design", "url": url_for("app.load_design"), "submenu": None},
            ]),
            {"type": "link", "name": "Help", "url": url_for("app.help"), "submenu": None},
        ],
        "/materials": [
            {"type": "link", "name": "Home", "url": url_for("app.welcome"), "submenu": None},
            *add_if_allowed(plan, ["basic","premium"], [
                {"type": "button", "name": "Upload Material", "action": "document.getElementById('materialFileInput').click();"},
                {"type": "link", "name": "Set Up Environment", "url": url_for("app.welcome"), "submenu": None},
            ]),
            {"type": "link", "name": "Help", "url": url_for("app.help"), "submenu": None},
            {"type": "link", "name": "Documentation", "url": "/static/files/Documentation.pdf", "download": "Documentation.pdf", "submenu": None},
        ],
        "/public_designs": [
            {"type": "link", "name": "Home", "url": url_for("app.welcome"), "submenu": None},
            {"type": "link", "name": "New Design", "url": url_for("app.index"), "submenu": None},
        ],
    }
    return nav_links.get(request.path, [])
