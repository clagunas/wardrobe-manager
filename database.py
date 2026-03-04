import csv
import os
from pymongo import MongoClient
from datetime import datetime

client = MongoClient("mongodb://localhost:27017/")
db = client["wardrobe"]
collection = db["items"]
#collection.create_index("name", unique=True) # for later

# Clear existing data (DEV)
collection.delete_many({})
print("Existing data cleared.")

data_folder = "data"

for filename in os.listdir(data_folder):
    if filename.endswith(".csv"):
        file_path = os.path.join(data_folder, filename)
        print(f"Importing {filename}...")
        
        with open(file_path, newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                item = {
                    "name": row["Item"],
                    "category": row["Type"],
                    "image_filename": row["Image"],
                    "style": row["Style"],
                    "brand": row["Brand"],
                    #"second_hand": row["2nd hand"].lower() == "yes",
                    "colors": [c.strip() for c in row["Color"].split(",")],
                    "season": [s.strip() for s in row["Season"].split(",")],
                    "price": float(row["Price"].replace(",", ".")) if row["Price"] else None,
                    #"date_added": datetime.strptime(row["Date"], "%Y-%m-%d") if row["Date"] else None,
                    "place": row["Place"],
                    "comment": row["Comment"]
                }
                collection.insert_one(item)

print("Import complete.")