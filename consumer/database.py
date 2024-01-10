from pymongo import MongoClient
from dotenv import load_dotenv
import os

class Database:
    def __init__(self):
        load_dotenv()
        print("Connecting to database: " + os.getenv("MONGODB_URL"))
        self.client = MongoClient(os.getenv("MONGODB_URL"))
        print("Connected to database")
        self.db = self.client[os.getenv("MONGODB_DB_NAME")]
        self.collection = self.db[os.getenv("MONGODB_COLLECTION")]

    def insert(self, data):
        self.collection.insert_one(data)

    def find(self, query):
        return self.collection.find(query)

    def find_one(self, query):
        return self.collection.find_one(query)

    def delete(self, query):
        self.collection.delete_one(query)

    def count(self):
        return self.collection.count_documents({})

    def close(self):
        self.client.close()