from pymongo import MongoClient
from dotenv import load_dotenv
import os

class Database:
    def __init__(self):
        load_dotenv()
        self.client = MongoClient(os.getenv("MONGO_IP"), int(os.getenv("MONGO_PORT")))
        print("Connected to database")
        self.db = self.client[os.getenv("MONGO_DB")]
        self.collection = self.db[os.getenv("MONGO_COLLECTION")]

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