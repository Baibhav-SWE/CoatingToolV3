import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()


class Config:
    MONGO_URI = os.getenv("MONGO_URI")
    DB_NAME = os.getenv("DB_NAME")
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))  # Default to 587 if not set
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS") == "True"
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL") == "True"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    SHOPIFY_SHARED_SECRET = os.getenv("SHOPIFY_SHARED_SECRET")
    PREMIUM_PRODUCT_ID = os.getenv("PREMIUM_PRODUCT_ID")
    BASIC_PRODUCT_ID = os.getenv("BASIC_PRODUCT_ID")
    BASIC_PRODUCT_MONTHLY_BUY_ID = os.getenv("BASIC_PRODUCT_MONTHLY_BUY_ID")
    BASIC_PRODUCT_YEARLY_BUY_ID = os.getenv("BASIC_PRODUCT_YEARLY_BUY_ID")
    PREMIUM_PRODUCT_MONTHLY_BUY_ID = os.getenv("PREMIUM_PRODUCT_MONTHLY_BUY_ID")
    PREMIUM_PRODUCT_YEARLY_BUY_ID = os.getenv("PREMIUM_PRODUCT_YEARLY_BUY_ID")
    TRIAL_DAYS = int(os.getenv("TRIAL_DAYS", 7))
