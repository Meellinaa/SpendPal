import certifi
from pymongo import MongoClient

uri = "mongodb+srv://melinafathi3825_db_user:TLUujP6ELG1NtXE1@snapcart.avy60sg.mongodb.net/?appName=SnapCart"
client = MongoClient(uri, tlsCAFile=certifi.where())
db = client["spendpal"]
col = db["receipts"]

# Delete everything
x = col.delete_many({})
print(f"✅ Deleted {x.deleted_count} old receipts. Database is clean!")