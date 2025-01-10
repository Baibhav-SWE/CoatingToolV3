from pymongo import MongoClient

# Global MongoDB client and database
client = None
db = None


def init_db(app):
    """
    Initialize the MongoDB connection using app configuration.
    """
    global client, db
    mongo_uri = app.config.get("MONGO_URI")
    if not mongo_uri:
        raise ValueError("MONGO_URI is not set in the configuration.")

    client = MongoClient(mongo_uri)
    db = client["AWI_users"]


def get_db():
    """
    Retrieve the initialized database instance.
    """
    global db
    if db is None:
        raise Exception("Database not initialized. Call init_db() first.")
    return db


def get_users_collection():
    db = get_db()
    return db["AWI_users"]


def get_subscriptions_collection():
    db = get_db()
    return db["subscriptions"]
