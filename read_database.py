import csv
import os
from pymongo import MongoClient
from datetime import datetime
from models import ClothingItemBase

client = MongoClient("mongodb://localhost:27017/")
db = client["wardrobe"]
collection = db["items"]
#collection.create_index("name", unique=True) # for later

# Clear existing data (DEV)
collection.delete_many({})
print("Existing data of items cleared.")

data_folder = "data"

def to_bool(value):
    return str(value).strip().lower() in {"true", "1", "yes"}

for filename in os.listdir(data_folder):
    if filename.endswith(".csv"):
        file_path = os.path.join(data_folder, filename)
        print(f"Importing {filename}...")
        
        with open(file_path, newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                item = ClothingItemBase(
                    name=row["Item"],
                    category=row["Type"],
                    image_filename=row["Image"],
                    style=[s.strip() for s in row["Style"].split(",") if s],
                    brand=row["Brand"] or None,
                    second_hand=to_bool(row["2nd hand"]) if row["2nd hand"] else None,
                    colors=[c.strip() for c in row["Color"].split(",") if c],
                    season=row["Season"] or None,
                    price=float(row["Price"].replace(",", ".")) if row["Price"] else None,
                    date_added=datetime.strptime(row["Date"], "%d/%m/%Y") if row["Date"] else None,
                    place=row["Place"],
                    comment=row["Comment"],
                )
                collection.insert_one(item.model_dump())

print("Import of items complete.")

# there should be a better way
if "outfits" not in db.list_collection_names():
    db.create_collection("outfits")
    print("Outfits collection created.")

if "lookbook" not in db.list_collection_names():
    db.create_collection("lookbook")
    print("Lookbook collection created.")

if "calendar" not in db.list_collection_names():
    db.create_collection("calendar")
    print("Calendar collection created.")
