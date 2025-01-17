from pymongo import MongoClient
import os

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["contests_bot"]
users_col = db["users"]
contests_col = db["contests"]