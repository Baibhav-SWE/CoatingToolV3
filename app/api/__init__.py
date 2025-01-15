from flask import Blueprint

# Create a blueprint for version 1 of the API
api = Blueprint("api", __name__)

# Import API routes to register them
from . import subscription
