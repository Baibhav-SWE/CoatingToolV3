import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

class Config:
    MONGO_URI = os.getenv("MONGO_URI")
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))  # Default to 587 if not set
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS") == "True"
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL") == "True"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    SHOPIFY_SHARED_SECRET = os.getenv("SHOPIFY_SHARED_SECRET")