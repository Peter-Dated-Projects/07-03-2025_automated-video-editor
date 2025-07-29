from flask import request
from flask_restful import Api, Resource
from pymongo import MongoClient
import os

# env variables
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB = os.environ.get("MONGO_DB", "mydatabase")
MONGO_COLLECTION = os.environ.get("MONGO_COLLECTION", "mycollection")

# -------------------------------------------------------------------- #
# MongoDB setup

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client[os.environ.get("MONGO_DB", "mydatabase")]
collection = db[os.environ.get("MONGO_COLLECTION", "mycollection")]

# -------------------------------------------------------------------- #
# Database API

class DatabaseAPI(Resource):
    def get(self):
        """Get all documents or a single document by id (use ?id=xxx)"""
        doc_id = request.args.get("id")
        if doc_id:
            doc = collection.find_one({"_id": doc_id})
            if doc:
                doc["_id"] = str(doc["_id"])
                return doc, 200
            return {"error": "Not found"}, 404
        docs = list(collection.find())
        for d in docs:
            d["_id"] = str(d["_id"])
        return docs, 200

    def post(self):
        """Insert a new document. Expects JSON body."""
        data = request.get_json()
        if not data:
            return {"error": "No data provided"}, 400
        result = collection.insert_one(data)
        return {"inserted_id": str(result.inserted_id)}, 201

    def put(self):
        """Update a document by id. Expects JSON body with 'id' and update fields."""
        data = request.get_json()
        doc_id = data.get("id")
        if not doc_id:
            return {"error": "No id provided"}, 400
        update = {k: v for k, v in data.items() if k != "id"}
        result = collection.update_one({"_id": doc_id}, {"$set": update})
        if result.matched_count:
            return {"updated": True}, 200
        return {"error": "Not found"}, 404

    def delete(self):
        """Delete a document by id (expects ?id=xxx)"""
        doc_id = request.args.get("id")
        if not doc_id:
            return {"error": "No id provided"}, 400
        result = collection.delete_one({"_id": doc_id})
        if result.deleted_count:
            return {"deleted": True}, 200
        return {"error": "Not found"}, 404
