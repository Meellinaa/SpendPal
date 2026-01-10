# Description: Represents an entire shopping trip. It acts as a container for multiple Item objects and transaction details.

# Attributes:

# store_name (string): Where the purchase happened.

# date (datetime): When the purchase happened.

# items (List[Item]): A list containing all the Item objects for this trip.


# total_amount (float): The final sum of the receipt.
# +1

# Key Methods:

# add_item(item): Appends a new item to the list and updates the total.
# CloudManager.py
class CloudManager:
    # ... your __init__ stays the same ...

    def save_receipt_object(self, receipt_obj):
        """
        Takes the Receipt class object and converts it to 
        a dictionary that MongoDB understands.
        """
        # Convert the object to a dictionary (JSON format)
        receipt_data = {
            "store_name": receipt_obj.store_name,
            "date": receipt_obj.date,
            "total": receipt_obj.total_amount,
            "items": [
                {
                    "name": item.name, 
                    "price": item.price, 
                    "category": item.subcategory
                } for item in receipt_obj.items
            ]
        }

        try:
            self.receipts_col.insert_one(receipt_data)
            print(f"✅ Saved Receipt from {receipt_obj.store_name}")
        except Exception as e:
            print(f"❌ Cloud Error: {e}")