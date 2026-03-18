from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Literal, Optional
from uuid import uuid4
from motor.motor_asyncio import AsyncIOMotorClient
from models import ClothingItemBase, ClothingItem, ClothingItemFilter, ClothingItemUpdate
from bson import ObjectId
#from database_interface import get_items_collection
from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title="Clothing Items API",
    description="A simple API to manage clothing items",
    version="1.0.0",
)

app.mount("/images", StaticFiles(directory="images"), name="images")
app.mount("/static", StaticFiles(directory="frontend"), name="static")

client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.wardrobe
collection = db.items #get_items_collection()


def mongo_to_dict(item):
    item["id"] = str(item["_id"])
    del item["_id"]
    return item

@app.get("/", tags=["Root"])
async def read_root():#(collection: AsyncIOMotorCollection = Depends(get_items_collection)):
    """Welcome endpoint"""
    items_count = await collection.count_documents({})    
    return {
        "message": "Welcome to the Clothing Items API!",
        "docs": "/docs",
        "items_count": items_count,
    }

@app.get("/items", response_model=List[ClothingItem], tags=["Items"])
async def get_all_clothing_items():#(collection=Depends(get_items_collection)):
    """Get all clothing items"""
    items = await collection.find({}).to_list(1000)
    items = [mongo_to_dict(item) for item in items]
    return items

# Always define specific routes before path-parameter routes to avoid conflicts
# TO-DO: add filters or allow different direction or length
@app.get("/items/time_ordered", response_model=List[ClothingItem], tags=["Items"])
async def get_clothing_items_time_ordered():#(collection=Depends(get_items_collection)):
    """Get clothing items ordered by time of creation in the database"""
    filter = {} # maybe useful later
    direction = -1 # descending
    sorted_cursor = collection.find(filter).sort("_id", direction)
    items = await sorted_cursor.to_list(length=3)
    items = [mongo_to_dict(item) for item in items]
    return items

# this probably doesn't work
@app.get("/items/{item_id}", response_model=ClothingItem, tags=["Items"])
async def get_clothing_item(item_id: str):#, collection=Depends(get_items_collection)):
    """Get a specific clothing item by ID"""
    item = await collection.find_one({"id": item_id})
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.post(
    "/create_clothing_item",
    response_model=ClothingItem,
    status_code=201,
    tags=["Items"],
)
async def create_clothing_item(item: ClothingItemBase):
    """Create a new clothing item"""
    item_dict = item.model_dump()
    inserted = await collection.insert_one(item_dict)
    item_dict["id"] = str(inserted.inserted_id)
    return item_dict

@app.post(
    "/get_items_filtered",
    response_model=List[ClothingItem],
    status_code=200,
    tags=["Items"],
)
async def get_items_filtered(filter: ClothingItemFilter):
    """Get clothing items based on filters"""

    query = {}

    filter_map = {
        "category": "category",
        "season": "season",
        "color": "colors",
        "brand": "brand",
        "second_hand": "second_hand"
    }

    for field, db_field in filter_map.items():
        value = getattr(filter, field)

        if value:
            query[db_field] = {"$in": value}

    items = await collection.find(query).to_list(1000)
    items = [mongo_to_dict(item) for item in items]

    return items

@app.patch("/modify_item/{item_id}", response_model=ClothingItem, tags=["Items"])
async def modify_clothing_item(item_id: str, item: ClothingItemUpdate):
    """Modify an existing clothing item by ID"""
    item_dict = item.model_dump(exclude_unset=True)
    if not item_dict:
        raise HTTPException(status_code=400, detail="No fields provided")
    result = await collection.update_one({"_id": ObjectId(item_id)}, 
                                         {"$set": item_dict})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    updated_item = await collection.find_one({"_id": ObjectId(item_id)})
    return mongo_to_dict(updated_item)
