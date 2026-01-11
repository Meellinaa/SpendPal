import certifi
import re
import os
from pymongo import MongoClient
from datetime import datetime

class CloudManager:
    def __init__(self):
        # 1. CONNECT TO MONGODB
        self.uri = "mongodb+srv://melinafathi3825_db_user:TLUujP6ELG1NtXE1@snapcart.avy60sg.mongodb.net/?appName=SnapCart"
        try:
            self.client = MongoClient(self.uri, tlsCAFile=certifi.where())
            self.db = self.client["spendpal"] 
            self.receipts_col = self.db["receipts"]
            print("✅ Cloud Connected.")
        except Exception as e:
            print(f"❌ Cloud Connection Failed: {e}")

        # 2. LOAD GROCERY LISTS
        self.grocery_word_sets = []
        base_path = os.path.dirname(os.path.abspath(__file__))
        file_names = ["grocery_items_cleaned.txt", "grocery_items.txt"]
        
        for fname in file_names:
            full_path = os.path.join(base_path, fname)
            if os.path.exists(full_path):
                with open(full_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        clean_line = line.strip().lower()
                        if clean_line:
                            self.grocery_word_sets.append(set(clean_line.split()))
                print(f"✅ Loaded items from {fname}")

    def clean_receipt_text(self, text):
        """ Fixes typos and abbreviations found in your specific logs. """
        text = text.lower()
        
        # 1. Fix Leetspeak
        trans_table = str.maketrans({'0': 'o', '1': 'i', '3': 'e', '4': 'a', '@': 'a'})
        text = text.translate(trans_table)

        # 2. TARGETED REPLACEMENTS (Added your failures here!)
        replacements = {
            "bgt": "baguette",
            "strawbry": "strawberry",
            "creamil": "cream",       # Fixes "Whip Creamil"
            "prsdnt": "president",    # Fixes "Prsdnt Brie"
            "bs": "boneless skinless", # Fixes "Bs Thighs"
            "org": "organic",
            "tmto": "tomato",
            "pota": "potato"
        }
        
        for bad, good in replacements.items():
            text = re.sub(r'\b' + bad + r'\b', good, text)
            
        # 3. Clean characters
        text = re.sub(r'[^a-z\s]', ' ', text)
        return text.strip()

    def categorize(self, item_name):
        clean_line = self.clean_receipt_text(item_name)
        line_words = set(clean_line.split())
        
        print(f"🔎 Scanning: '{item_name}' -> Cleaned: '{clean_line}'")

        # Step A: Check against text file
        for grocery_set in self.grocery_word_sets:
            if grocery_set.issubset(line_words):
                print(f"   ✅ MATCH! Found list item {grocery_set}")
                return "Groceries", "General"

        # Step B: EXPANDED KEYWORDS (Catches Plurals & Missing Items)
        # Added: cucumber, pepper, avocado, potato, cheese, feta, brie, cream, thigh
        keywords = [
            "shrimp", "straw", "berry", "bread", "artisan", "baguette", 
            "fruit", "vegetable", "cucumber", "pepper", "avocado", 
            "potato", "tomato", "cheese", "feta", "brie", "cream", 
            "milk", "thigh", "meat", "chicken", "beef"
        ]
        
        for kw in keywords:
            # Check if keyword is in the line (handles 'cucumbers' matching 'cucumber')
            if kw in clean_line:
                print(f"   ✅ KEYWORD MATCH! Found '{kw}'")
                return "Groceries", "General"

        print(f"   ❌ No match. Defaults to Other.")
        return "Other", "General"

    def process_and_save(self, items, total):
        categorized_items = []
        for name, price in items:
            main_cat, sub_cat = self.categorize(name)
            categorized_items.append({
                "name": name,
                "price": price,
                "category": main_cat,
                "subcategory": sub_cat
            })

        doc = {
            "date": datetime.now(),
            "store": "Scanned Receipt",
            "items": categorized_items,
            "total": total
        }
        try:
            self.receipts_col.insert_one(doc)
            print(f"✅ SAVED RECEIPT: {len(categorized_items)} items - ${total}")
        except:
            print("❌ Save Failed")
        return categorized_items