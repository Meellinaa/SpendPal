import pytesseract
from PIL import Image
import re
import os
import shutil
import certifi
from pymongo import MongoClient
from datetime import datetime  # <--- Added this to track time

class OCRProcessor:
    def __init__(self):
        # 1. Setup Tesseract
        tesseract_path = shutil.which("tesseract")
        if not tesseract_path:
            possible_paths = ['/opt/homebrew/bin/tesseract', '/usr/local/bin/tesseract']
            for path in possible_paths:
                if os.path.exists(path):
                    tesseract_path = path
                    break
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        self.config = '--psm 6'

        # 2. CONNECT TO CLOUD DATABASE
        uri = "mongodb+srv://melinafathi3825_db_user:TLUujP6ELG1NtXE1@snapcart.avy60sg.mongodb.net/?appName=SnapCart"
        
        try:
            self.client = MongoClient(uri, tlsCAFile=certifi.where())
            self.db = self.client["SnapCartDB"]
            self.food_collection = self.db["FoodItems"]
            self.receipts_collection = self.db["Receipts"] # <--- New Collection for History
            print("✅ OCR Connected to Cloud (Read & Write)!")
        except Exception as e:
            print(f"⚠️ Cloud Connection Error: {e}")
            self.food_collection = None
            self.receipts_collection = None

    def extract_text(self, image_path):
        """Standard Text Extraction"""
        try:
            img = Image.open(image_path).convert('L')
            text = pytesseract.image_to_string(img, config=self.config)
            
            corrections = {
                "RESULER": "REGULAR", "RESULAR": "REGULAR", 
                "SEVINSS": "SAVINGS", "TAK": "TAX", "O": "0"
            }
            for error, fix in corrections.items():
                text = text.replace(error, fix)
            return text
        except: return "Error"

    def parse_receipt(self, raw_text):
        """Identify Foods, Calculate Total, and SAVE TO CLOUD"""
        data = { 
            "store_name": "Unknown", 
            "items": [], 
            "total": 0.0,
            "date": datetime.now() # <--- Stamp the current time
        }
        
        lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
        
        for line in lines:
            # Check for Store Name (Simple guess: First line that isn't a number)
            if data["store_name"] == "Unknown" and len(line) > 4 and not any(char.isdigit() for char in line):
                data["store_name"] = line

            # Check for Total
            if any(w in line.upper() for w in ["TOTAL", "SUBTOTAL", "TAX", "SAVINGS"]):
                matches = re.findall(r'(\d+[.,]\d{2})', line)
                if matches and "TOTAL" in line.upper():
                    try: data["total"] = float(matches[-1].replace(',', '.'))
                    except: pass
                continue
            
            # Find Items
            matches = re.findall(r'(\d+\.\d{2})', line)
            if matches:
                try:
                    price = float(matches[-1])
                    raw_name = line.split(matches[-1])[0].strip()
                    clean_name = re.sub(r'[^\w\s]', '', raw_name).strip()
                    
                    if len(clean_name) > 2:
                        # Fix Name using Cloud Database
                        corrected_name, category = self.identify_food_cloud(clean_name)
                        
                        # Add to list
                        data["items"].append({
                            "name": corrected_name,
                            "category": category,
                            "price": price
                        })
                except: continue

        # Calculate total if OCR missed it
        if data["total"] == 0.0 and data["items"]:
            data["total"] = sum(item["price"] for item in data["items"])

        # --- AUTOMATIC SAVE STEP ---
        self.save_receipt_to_cloud(data)
        
        # Return format for GUI (List of tuples)
        gui_return_data = {
            "store_name": data["store_name"],
            "total": data["total"],
            "items": [(f"{item['name']} ({item['category']})", item['price']) for item in data["items"]]
        }
        return gui_return_data

    def identify_food_cloud(self, raw_name):
        """Read from FoodItems collection"""
        if self.food_collection is None:
            return raw_name.title(), "Other"

        clean_name = raw_name.lower()
        try:
            result = self.food_collection.find_one({"name": {"$regex": clean_name}})
            if result:
                return result['name'].split(',')[0].title(), result['category']
        except: pass
        
        return raw_name.title(), "Other"

    def save_receipt_to_cloud(self, receipt_data):
        """Write to Receipts collection"""
        if self.receipts_collection is None:
            return

        try:
            # Only save if we found items (don't save empty junk scans)
            if len(receipt_data["items"]) > 0:
                self.receipts_collection.insert_one(receipt_data)
                print(f"✅ SAVED RECEIPT: {receipt_data['store_name']} - ${receipt_data['total']:.2f}")
            else:
                print("⚠️ Scan empty, skipping save.")
        except Exception as e:
            print(f"❌ Save Failed: {e}")