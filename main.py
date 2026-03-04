from fastapi import FastAPI, Request, Query
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List

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
    item_type: List[str] = Query(None)
):
    query = {}

    if color:
        query["colors"] = {"$in": color}

    if season:
        query["season"] = {"$in": season}

    if item_type:
        query["category"] = {"$in": item_type}

    items = await collection.find(query).to_list(1000)

    # Fetch distinct values for filters
    all_colors = await collection.distinct("colors")
    all_seasons = await collection.distinct("season")
    all_types = await collection.distinct("category")

    return templates.TemplateResponse("items.html", {
        "request": request,
        "items": items,
        "all_colors": sorted(all_colors),
        "all_seasons": sorted(all_seasons),
        "all_types": sorted(all_types),
        "selected_colors": color or [],
        "selected_seasons": season or [],
        "selected_types": item_type or []
    })