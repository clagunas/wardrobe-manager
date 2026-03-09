from fastapi import FastAPI, Request, Query, Form, File, UploadFile
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from typing import List, Optional
import os
import shutil
import re
import uuid

def make_filename(name):
    cleaned = name.lower()
    cleaned = re.sub(r"[^\w\s]", "", cleaned)
    cleaned = cleaned.replace(" ", "_")
    return f"{uuid.uuid4()}_{cleaned}.jpg"

ALLOWED_CATEGORIES = [
    "Top",
    "Pants",
    "Outerwear",
    "Shoes",
    "Accessories",
    "Dresses",
    "Bags"
]

app = FastAPI()

client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.wardrobe
collection = db.items

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def list_items(
    request: Request,
    color: List[str] = Query(None),
    season: List[str] = Query(None),
    item_category: List[str] = Query(None),
    brand: Optional[str] = Query(None),
):
    query = {}

    if color:
        query["colors"] = {"$in": color}

    if season:
        query["season"] = {"$in": season}

    if item_category:
        query["category"] = {"$in": item_category}

    if brand:
        query["brand"] = {"$regex": brand, "$options": "i"}

    items = await collection.find(query).to_list(1000)

    # Fetch distinct values for filters
    all_colors = await collection.distinct("colors")
    all_seasons = await collection.distinct("season")
    all_categories = ALLOWED_CATEGORIES

    return templates.TemplateResponse("items.html", {
        "request": request,
        "items": items,
        "all_colors": sorted(all_colors),
        "all_seasons": sorted(all_seasons),
        "all_categories": sorted(all_categories),
        "selected_colors": color or [],
        "selected_seasons": season or [],
        "selected_categories": item_category or [],
        "selected_brand": brand or "",
    })

@app.get("/add-item")
async def add_item_form(request: Request):
    # Get distinct values for filters to populate dropdowns if needed
    all_colors = await collection.distinct("colors")
    all_seasons = await collection.distinct("season")
    all_categories = ALLOWED_CATEGORIES
    all_styles = await collection.distinct("style")
    return templates.TemplateResponse("add_item.html", {
        "request": request,
        "all_colors": sorted(all_colors),
        "all_seasons": sorted(all_seasons),
        "all_categories": sorted(all_categories),
        "all_styles": sorted(all_styles)
    })

@app.post("/add-item")
async def add_item(
    name: str = Form(...),
    category: str = Form(...),
    colors: Optional[List[str]] = Form(None),   # list of checked colors
    seasons: Optional[List[str]] = Form(None),  # list of checked seasons
    style: Optional[List[str]] = Form(None),
    brand: Optional[str] = Form(None),
    price: Optional[float] = Form(None),
    image: Optional[UploadFile] = File(None)
):
    image_filename = None
    if image:
        # Save file to static/images/
        image_filename = make_filename(name)
        save_path = os.path.join("static", "images", image_filename)
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

    # do not allow arbitrary categories
    if category not in ALLOWED_CATEGORIES:
        return RedirectResponse(url="/add-item", status_code=303)
    
    item = {
        "name": name,
        "category": category,
        "colors": colors or [],
        "season": seasons or [],
        "style": style or [],
        "brand": brand or "",
        "price": price or "",
        "image_filename": image_filename,
        #"created_at": datetime.utcnow()
    }

    await collection.insert_one(item)

    return RedirectResponse(url="/", status_code=303)

@app.get("/edit-item/{item_id}")
async def edit_item_form(request: Request, item_id: str):

    item = await collection.find_one({"_id": ObjectId(item_id)})

    return templates.TemplateResponse("edit_item.html", {
        "request": request,
        "item": item,
        "all_colors": await collection.distinct("colors"),
        "all_seasons": await collection.distinct("season"),
        "all_styles": await collection.distinct("style"),
        "all_categories": ALLOWED_CATEGORIES
    })

@app.post("/edit-item/{item_id}")
async def update_item(
    item_id: str,
    name: str = Form(...),
    category: str = Form(...),
    colors: Optional[List[str]] = Form(None),
    seasons: Optional[List[str]] = Form(None),
    style: Optional[List[str]] = Form(None),
    brand: Optional[str] = Form(None),
    price: Optional[float] = Form(None),
    image: Optional[UploadFile] = File(None)
):

    update_data = {
        "name": name,
        "category": category,
        "colors": colors or [],
        "season": seasons or [],
        "style": style or [],
        "brand": brand or "",
        "price": price or ""
    }

    if image:
        image_filename = make_filename(name)

        save_path = os.path.join("static", "images", image_filename)

        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        update_data["image_filename"] = image_filename

    await collection.update_one(
        {"_id": ObjectId(item_id)},
        {"$set": update_data}
    )

    return RedirectResponse(url="/", status_code=303)