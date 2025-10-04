from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import os


class MongoDBConnection:
    def __init__(self, uri=None, db_name=None):
        self.uri = uri or os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        self.db_name = db_name or os.getenv("MONGODB_DB", "balagh_bot")
        self.client = None
        self.db = None

    def connect(self):
        try:
            self.client = MongoClient(
                self.uri, serverSelectionTimeoutMS=5000, minPoolSize=1
            )
            # Trigger a server selection to verify connection
            self.client.admin.command("ping")
            self.db = self.client[self.db_name]
        except ConnectionFailure as e:
            raise RuntimeError(f"Failed to connect to MongoDB: {e}")

    def get_db(self):
        if self.db is None:
            self.connect()
        return self.db

    def close(self):
        if self.client:
            self.client.close()


# Usage example:
mongo_conn = MongoDBConnection()
