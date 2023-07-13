from pymongo import MongoClient
import os

url = os.getenv("DATABASE_URL")
client = MongoClient(url)
db = client["melomint-dev"]
