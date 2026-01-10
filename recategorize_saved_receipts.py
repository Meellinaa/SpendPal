from pymongo import MongoClient
from SmartCategorizer import categorize_item
import certifi

# MongoDB connection
uri = "mongodb+srv://melinafathi3825_db_user:TLUujP6ELG1NtXE1@snapcart.avy60sg.mongodb.net/?appName=SnapCart"
client = MongoClient(uri, tlsCAFile=certifi.where())
db = client["spendpal"]
receipts_col = db["receipts"]

# Process all receipts
for receipt in receipts_col.find():
    updated = False
    for item in receipt.get("items", []):
        old_cat = item.get("category", "")
        old_sub = item.get("subcategory", "")
        new_cat, new_sub = categorize_item(item.get("name", ""))
        if (old_cat, old_sub) != (new_cat, new_sub):
            item["category"] = new_cat
            item["subcategory"] = new_sub
            updated = True
    if updated:
        receipts_col.update_one({"_id": receipt["_id"]}, {"$set": {"items": receipt["items"]}})
        print(f"Updated receipt {receipt['_id']}")
print("Done re-categorizing all saved receipts.")
