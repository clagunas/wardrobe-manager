from fileinput import filename
import os

from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field
from typing import List, Literal, Optional
from uuid import uuid4
from motor.motor_asyncio import AsyncIOMotorClient
from models import (
    ClothingItemBase,
    ClothingItem,
    ClothingItemFilter,
    ClothingItemUpdate,
    OutfitBase,
    Outfit,
    ALLOWED_CATEGORIES,
    ALLOWED_SEASONS
)
from bson import ObjectId
from fastapi import UploadFile, File
import shutil
import uuid
from image_utils import combine_images_square

# from database_interface import get_items_collection
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
collection = db.items  # get_items_collection()
outfit_collection = db.outfits
lookbook_collection = db.lookbooks # future use
calendar_collection = db.calendar # future use


def mongo_to_dict(item):
    item["id"] = str(item["_id"])
    del item["_id"]
    return item


@app.get("/", tags=["Root"])
async def read_root():  # (collection: AsyncIOMotorCollection = Depends(get_items_collection)):
    """Welcome endpoint"""
    
    # items_count = await collection.count_documents({})
    # return {
    #     "message": "Welcome to the Clothing Items API!",
    #     "docs": "/docs",
    #     "show_all": "/static/items.html",
    #     "items_count": items_count,
    # }
    return RedirectResponse("/static/index.html")

# HELPER FUNTIONS

@app.get("/allowed_values", tags=["Helper"])
async def allowed_values():
    return {
        "categories": ALLOWED_CATEGORIES,
        "seasons": ALLOWED_SEASONS
    }

@app.get("/item_appearances/{item_id}", response_model=dict, tags=["Helper"])
async def find_item_appearances(item_id: str):
    """Find outfits, lookbooks, and calendar entries that include a specific clothing item"""
    outfits = []
    async for outfit in outfit_collection.find({"items": item_id}):
        outfit["_id"] = str(outfit["_id"])
        outfits.append(outfit)
    lookbooks = []
    async for lookbook in db.lookbooks.find({"items": item_id}):
        lookbook["_id"] = str(lookbook["_id"])
        lookbooks.append(lookbook)
    days_count = await db.calendar.count_documents({"items": item_id})
    # days = []
    # async for day in db.calendar.find({"items": item_id}):
    #     day["_id"] = str(day["_id"])
    #     days.append(day)
        # I don't want the days but just a count 
    return {"outfits": outfits, "lookbooks": lookbooks, "days": days_count}

@app.get("/outfit_appearances/{outfit_id}", response_model=dict, tags=["Helper"])
async def find_outfit_appearances(outfit_id: str):
    """Find lookbooks, and calendar entries that include a specific outfit"""
    ## I don't know yet if all outfits and items will be listed under items
    lookbooks = []
    async for lookbook in db.lookbooks.find({"items": outfit_id}):
        lookbook["_id"] = str(lookbook["_id"])
        lookbooks.append(lookbook)
    days_count = await db.calendar.count_documents({"items": outfit_id})
    # days = []
    # async for day in db.calendar.find({"items": outfit_id}):
    #     day["_id"] = str(day["_id"])
    #     days.append(day)
        # I don't want the days but just a count 
    return {"lookbooks": lookbooks, "days": days_count}

# to be changed maybe
@app.post("/upload_image", tags=["Helper"])
async def upload_image(file: UploadFile = File(...)):
    ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}" # don't want that? 
    filepath = f"images/{filename}"
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"filename": filename}


# CLOTHING ITEM ROUTES

@app.get("/items", response_model=List[ClothingItem], tags=["Items"])
async def get_all_clothing_items():  # (collection=Depends(get_items_collection)):
    """Get all clothing items"""
    items = await collection.find({}).to_list(1000)
    items = [mongo_to_dict(item) for item in items]
    return items


# Always define specific routes before path-parameter routes to avoid conflicts
# TO-DO: add filters or allow different direction or length
@app.get("/items/time_ordered", response_model=List[ClothingItem], tags=["Items"])
async def get_clothing_items_time_ordered():  # (collection=Depends(get_items_collection)):
    """Get clothing items ordered by time of creation in the database"""
    filter = {}  # maybe useful later
    direction = -1  # descending
    sorted_cursor = collection.find(filter).sort("_id", direction)
    items = await sorted_cursor.to_list(length=3)
    items = [mongo_to_dict(item) for item in items]
    return items


@app.get("/items/{item_id}", response_model=ClothingItem, tags=["Items"])
async def get_clothing_item(
    item_id: str,
):  # , collection=Depends(get_items_collection)):
    """Get a specific clothing item by ID"""
    item = await collection.find_one({"_id": ObjectId(item_id)})
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return mongo_to_dict(item)


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
    "/filter_items",
    response_model=List[ClothingItem],
    status_code=200,
    tags=["Items"],
)
async def filter_items(filter: ClothingItemFilter):
    """Get clothing items based on filters"""

    query = {}

    filter_map = {
        "category": "category",
        "season": "season",
        "color": "colors",
        "brand": "brand",
        "second_hand": "second_hand",
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
    result = await collection.update_one(
        {"_id": ObjectId(item_id)}, {"$set": item_dict}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    updated_item = await collection.find_one({"_id": ObjectId(item_id)})
    return mongo_to_dict(updated_item)

# delete an item by id
@app.delete("/delete_item/{item_id}", status_code=204, tags=["Items"])
async def delete_clothing_item(item_id: str):
    """Delete a clothing item by ID"""
    result = await collection.delete_one({"_id": ObjectId(item_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return None

# OUTFIT ROUTES

# check all outfit routes
@app.post("/create_outfit", response_model=Outfit, status_code=201, tags=["Outfits"])
async def create_outfit(outfit: OutfitBase):
    """Create a new outfit in the 'outfits' collection"""
    outfit_dict = outfit.model_dump()
    # check if an outfit with the same items already exists
    outfit_dict["items"] = sorted(outfit_dict["items"])
    exists = await outfit_collection.count_documents({"items": outfit_dict["items"]}) > 0
    if exists:
        raise HTTPException(status_code=400, detail="Outfit with the same items already exists")
    inserted = await outfit_collection.insert_one(outfit_dict)
    outfit_dict["id"] = str(inserted.inserted_id)

    # create outfit pic 
    # currently only works if all items have an image
    object_ids = [ObjectId(i) for i in outfit_dict["items"]]
    items = await collection.find({"_id": {"$in": object_ids}}).to_list(length=None)
    img_paths = [item["image_filename"] for item in items if "image_filename" in item]

    if len(items) != len(object_ids):
        raise HTTPException(status_code=400, detail="Some items not found")

    img_paths = []
    for item in items:
        if "image_filename" not in item:
            raise HTTPException(status_code=400, detail="Item missing image")
        img_paths.append(item["image_filename"])

    result = combine_images_square(img_paths)

    filename = f"{outfit_dict['id']}.png"
    filepath = os.path.join("images/outfits/", filename)
    result.save(filepath)

    await outfit_collection.update_one(
    {"_id": inserted.inserted_id},
    {"$set": {"image_filename": filename}}
    )
    outfit_dict["image_filename"] = filename # for items it's only the filename too

    return outfit_dict


@app.get("/outfits", response_model=List, tags=["Outfits"])
async def get_all_outfits():
    """Get all outfits"""
    # outfits = await outfit_collection.find({}).to_list(1000)
    # outfits = [mongo_to_dict(outfit) for outfit in outfits]
    # return outfits

    outfits = []

    async for outfit in outfit_collection.find():
        item_ids = [ObjectId(i) for i in outfit["items"]]

        items = []
        async for item in collection.find({"_id": {"$in": item_ids}}):
            item["_id"] = str(item["_id"])
            items.append(item)

        outfit["_id"] = str(outfit["_id"])
        outfit["items_data"] = items

        outfits.append(outfit)

    return outfits

@app.get("/outfits/{outfit_id}", response_model=Outfit, tags=["Outfits"])
async def get_outfit(outfit_id: str):
    """Get a specific outfit by ID"""
    outfit = await outfit_collection.find_one({"_id": ObjectId(outfit_id)})
    if not outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")
    return mongo_to_dict(outfit)

@app.get(
    "/outfits/get_items/{outfit_id}",
    response_model=List[ClothingItem],
    tags=["Outfits"],
)
async def get_outfit_items(outfit_id: str):
    """Get a specific outfit by ID"""
    outfit = await outfit_collection.find_one({"_id": ObjectId(outfit_id)})
    if not outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")
    items = []
    for item_id in outfit["items"]:
        item = await collection.find_one({"_id": ObjectId(item_id)})
        if item:
            items.append(mongo_to_dict(item))
    return items

@app.delete("/delete_outfit/{outfit_id}", status_code=204, tags=["Outfits"])
async def delete_outfit(outfit_id: str):
    """Delete an outfit by ID"""
    result = await outfit_collection.delete_one({"_id": ObjectId(outfit_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Outfit not found")
    return None