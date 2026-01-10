from pymongo import MongoClient
import certifi
from datetime import datetime

# Your Connection String
URI = "mongodb+srv://melinafathi3825_db_user:TLUujP6ELG1NtXE1@snapcart.avy60sg.mongodb.net/?appName=SnapCart"

def save_test_receipt():
    try:
        # Connect
        client = MongoClient(URI, tlsCAFile=certifi.where())
        db = client["SnapCartDB"]
        
        # We use a NEW collection called 'Receipts'
        receipts_col = db["Receipts"] 

        # --- THE DATA STRUCTURE ---
        # This is how we store Date + Items together
        receipt_data = {
            "date": datetime.now(),            # 1. The Date (Today)
            "store_name": "Walmart",           # 2. Store Name
            "items": [                         # 3. List of Items
                {"name": "Apple", "price": 1.20, "category": "Produce"},
                {"name": "Milk", "price": 4.50, "category": "Dairy"},
                {"name": "Bread", "price": 3.00, "category": "Bakery"}
            ],
            "total": 8.70                      # 4. Total
        }

        # Save it!
        result = receipts_col.insert_one(receipt_data)
        print(f"✅ Receipt Saved! ID: {result.inserted_id}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    save_test_receipt()