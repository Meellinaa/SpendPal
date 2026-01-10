from pymongo import MongoClient
import certifi

# Connection
URI = "mongodb+srv://melinafathi3825_db_user:TLUujP6ELG1NtXE1@snapcart.avy60sg.mongodb.net/?appName=SnapCart"
client = MongoClient(URI, tlsCAFile=certifi.where())
db = client["SnapCartDB"]
receipts_col = db["Receipts"]

def show_history():
    print("\n--- 🛒 YOUR SHOPPING HISTORY ---")
    
    # This pulls every receipt saved in the cloud
    all_receipts = receipts_col.find().sort("date", -1) 

    total_all_time = 0
    
    for r in all_receipts:
        date_str = r['date'].strftime("%Y-%m-%d")
        print(f"📅 {date_str} | 🏪 {r['store_name']} | 💰 ${r['total']:.2f}")
        total_all_time += r['total']
        
        # Optional: Print items inside that receipt
        # for item in r['items']:
        #     print(f"   - {item['name']}")

    print("--------------------------------")
    print(f"💵 GRAND TOTAL SPENT: ${total_all_time:.2f}")

if __name__ == "__main__":
    show_history()