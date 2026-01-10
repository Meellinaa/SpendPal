import certifi
from pymongo import MongoClient

URI = "mongodb+srv://melinafathi3825_db_user:TLUujP6ELG1NtXE1@snapcart.avy60sg.mongodb.net/?appName=SnapCart"
client = MongoClient(URI, tlsCAFile=certifi.where())
# Use 'spendpal' to match your screenshot
db = client["spendpal"] 
food_col = db["FoodItems"] 

def predict_category(item_name):
    name_clean = item_name.lower().strip()
    try:
        # 1. Search the Cloud FoodItems collection
        result = food_col.find_one({"name": {"$regex": name_clean, "$options": "i"}})
        
        if result:
            return "Groceries", result["category"]
            
        # 2. Hardcoded fallback if not in Cloud yet
        if any(x in name_clean for x in ["apple", "banana", "corn"]):
            return "Groceries", "Produce"
        if any(x in name_clean for x in ["milk", "yogurt"]):
            return "Groceries", "Dairy"
            
    except Exception as e:
        print(f"Cloud lookup error: {e}")

    return "Other", "General"