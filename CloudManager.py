# Save this as CloudManager.py
import certifi
from pymongo import MongoClient
from datetime import datetime

class CloudManager:
    def __init__(self):
        # 1. Connect to MongoDB
        self.uri = "mongodb+srv://melinafathi3825_db_user:TLUujP6ELG1NtXE1@snapcart.avy60sg.mongodb.net/?appName=SnapCart"
        try:
            self.client = MongoClient(self.uri, tlsCAFile=certifi.where())
            self.db = self.client["spendpal"] 
            self.receipts_col = self.db["receipts"]
            print("✅ Cloud Connected.")
        except:
            print("❌ Cloud Connection Failed")

        # 2. LOAD THE FILE (The Fix for 'Other')
        self.grocery_set = set()
        try:
            with open('grocery_items_cleaned.txt', 'r') as f:
                # Clean and lowercase everything
                self.grocery_set = {line.strip().lower() for line in f if line.strip()}
            print(f"✅ Loaded {len(self.grocery_set)} items from text file.")
        except FileNotFoundError:
            print("⚠️ ERROR: Could not find grocery_items_cleaned.txt")

    def categorize(self, item_name):
        """Strict check: If in file -> Groceries."""
        clean_name = item_name.lower().strip()
        
        # DEBUG: Print what we are checking
        # print(f"Checking '{clean_name}'...") 

        if clean_name in self.grocery_set:
            print(f"   -> MATCH! '{clean_name}' is Groceries.")
            return "Groceries", "General"
        
        # Partial match check (e.g. 'gala apple' contains 'apple')
        for known_item in self.grocery_set:
            if known_item in clean_name and len(known_item) > 3:
                print(f"   -> PARTIAL MATCH! '{clean_name}' contains '{known_item}'")
                return "Groceries", "General"

        print(f"   -> No match for '{clean_name}'. Defaults to Other.")
        return "Other", "General"

    def process_and_save(self, items, total):
        categorized_items = []
        
        for name, price in items:
            # Use the logic above
            main_cat, sub_cat = self.categorize(name)
            
            categorized_items.append({
                "name": name,
                "price": price,
                "category": main_cat,
                "subcategory": sub_cat
            })

        # Save to Cloud
        doc = {
            "date": datetime.now(),
            "store": "Scanned Receipt",
            "items": categorized_items,
            "total": total
        }
        self.receipts_col.insert_one(doc)
        return categorized_items