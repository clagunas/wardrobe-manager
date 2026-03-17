from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import Depends

MONGO_URL = "mongodb://localhost:27017"

client = AsyncIOMotorClient(MONGO_URL)
db = client.wardrobe
collection = db.items

def get_database():
    return db

def get_items_collection(db=Depends(get_database)):
    return db.items