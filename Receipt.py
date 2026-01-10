# Save this as Receipt.py
class Receipt:
    def __init__(self, store_name, date):
        self.store_name = store_name
        self.date = date
        self.items = []
        self.total_amount = 0.0

    def add_item(self, item):
        self.items.append(item)
        # Handle cases where item is a dictionary or an object
        if isinstance(item, dict):
            self.total_amount += item['price']
        else:
            self.total_amount += item.price