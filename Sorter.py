from datetime import datetime

class TransactionSorter:
    def __init__(self, raw_data_string):
        self.transactions = []
        # Automatically parse the data when the class is created
        self._parse_data(raw_data_string)

    def _parse_data(self, raw_data):
        """Internal method to convert string text into usable objects."""
        lines = raw_data.strip().split('\n')
        
        for line in lines:
            parts = line.split(',')
            if len(parts) == 3:
                # Clean up whitespace
                member_id = parts[0].strip()
                date_str = parts[1].strip()
                item_name = parts[2].strip()

                try:
                    # Convert '14-08-2014' into a real Date Object so we can sort correctly
                    date_obj = datetime.strptime(date_str, "%d-%m-%Y")
                    
                    self.transactions.append({
                        "id": member_id,
                        "date_obj": date_obj, # Kept for sorting
                        "date_str": date_str, # Kept for display
                        "item": item_name
                    })
                except ValueError:
                    print(f"⚠️ Skipped invalid date format: {date_str}")

    def sort_by_date(self, newest_first=False):
        """Sorts the list by Date (Chronological)."""
        self.transactions.sort(key=lambda x: x['date_obj'], reverse=newest_first)
        return self.transactions

    def sort_by_item(self):
        """Sorts the list Alphabetically by Item Name."""
        self.transactions.sort(key=lambda x: x['item'])
        return self.transactions

    def sort_by_id(self):
        """Sorts by Member ID."""
        self.transactions.sort(key=lambda x: int(x['id']))
        return self.transactions

    def print_results(self):
        """Helper to print the data nicely."""
        print(f"{'DATE':<15} {'ITEM':<20} {'ID':<10}")
        print("-" * 45)
        for t in self.transactions:
            print(f"{t['date_str']:<15} {t['item']:<20} {t['id']:<10}")

# ==========================================
# HOW TO USE IT
# ==========================================
if __name__ == "__main__":
    # 1. Your raw data string
    my_data = """3563,14-08-2014,candy
3989,26-04-2014,baking powder
1393,26-08-2014,red/blush wine
1706,02-04-2014,soda
2111,12-11-2014,domestic eggs
3593,06-04-2014,bottled water
4255,29-09-2014,brown bread
4089,18-03-2014,bottled water"""

    # 2. Create the sorter
    sorter = TransactionSorter(my_data)

    # 3. Sort by Date (Chronological)
    print("\n--- 📅 SORTED BY DATE ---")
    sorter.sort_by_date(newest_first=False) # Change to True for Newest -> Oldest
    sorter.print_results()

    # 4. Sort by Item (Alphabetical)
    print("\n--- 🍎 SORTED BY ITEM ---")
    sorter.sort_by_item()
    sorter.print_results()