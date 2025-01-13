from pymongo import MongoClient

# Global MongoDB client and database
client = None
db = None


def init_db(app):
    """
    Initialize the MongoDB connection using app configuration.
    If the database or collections do not exist, they will be created automatically.
    """
    global client, db
    mongo_uri = app.config.get("MONGO_URI")
    if not mongo_uri:
        raise ValueError("MONGO_URI is not set in the configuration.")

    client = MongoClient(mongo_uri)
    db = client.get_database(
        app.config.get("DB_NAME")
    )  # Will create the database if it doesn't exist

    # Create collections if they don't exist
    if "AWI_users" not in db.list_collection_names():
        db.create_collection("AWI_users")  # Create users collection if it doesn't exist
    if "subscriptions" not in db.list_collection_names():
        db.create_collection(
            "subscriptions"
        )  # Create subscriptions collection if it doesn't exist


def get_db():
    """
    Retrieve the initialized database instance.
    """
    global db
    if db is None:
        raise Exception("Database not initialized. Call init_db() first.")
    return db


def get_users_collection():
    """
    Retrieve the 'users' collection.
    """
    db = get_db()
    return db["AWI_users"]  # Access the 'users' collection


def get_subscriptions_collection():
    """
    Retrieve the 'subscriptions' collection.
    """
    db = get_db()
    return db["subscriptions"]  # Access the 'subscriptions' collection

