import re
import difflib
from datetime import datetime, timedelta

# ---------------- CATEGORY TARGETS ----------------
CATEGORY_TARGETS = {
    "Groceries": 50,
    "Dining Out": 40,
    "Shopping": 100,
    "Other": 60
}

# ---------------- CATEGORIZATION ----------------
def categorize_item(item_name):
    """
    Categorize an item name into (main_category, sub_category).
    Extend the KEYWORDS dict below to add more rules.
    """

    # Clean and normalize the item name
    name = item_name.lower()
    # Replace common number-to-letter substitutions
    substitutions = str.maketrans({
        '0': 'o',
        '1': 'i',
        '3': 'e',
        '4': 'a',
        '5': 's',
        '7': 't',
        '8': 'b',
        '9': 'g',
    })
    name = name.translate(substitutions)
    name = re.sub(r'[^a-z ]+', ' ', name)  # Remove punctuation/special chars (now only letters and spaces)
    name = re.sub(r'\s+', ' ', name).strip()  # Collapse whitespace


    # Load grocery lists from both files (cache after first load)
    if not hasattr(categorize_item, "_grocery_set"):
        grocery_set = set()
        for fname in ["grocery_items_cleaned.txt", "grocery_items.txt"]:
            try:
                with open(fname) as f:
                    grocery_set.update(line.strip().lower() for line in f if line.strip())
            except FileNotFoundError:
                pass
        categorize_item._grocery_set = grocery_set
    grocery_set = categorize_item._grocery_set


    # If any word in the cleaned name matches a grocery item, categorize as Groceries
    for word in name.split():
        if word in grocery_set:
            return "Groceries", "Matched Word"

    # Fuzzy match: for each word, find close matches in grocery_set
    for word in name.split():
        close = difflib.get_close_matches(word, grocery_set, n=1, cutoff=0.8)
        if close:
            return "Groceries", f"Fuzzy ({close[0]})"

    # If any grocery item is a substring of the name (for partial/fuzzy match)
    for grocery in grocery_set:
        if grocery in name:
            return "Groceries", "Fuzzy Match"

    # No more hardcoded keywords. If not a grocery, fallback to Other.
    return "Other", "General"

def categorize_grocery_file(filename="grocery_items_cleaned.txt"):
    """Categorize all items in the given file and print a table of results."""
    with open(filename) as f:
        items = [line.strip() for line in f if line.strip()]

    print(f"{'Item':<25} | {'Main Category':<12} | {'Subcategory':<12}")
    print('-'*55)
    for item in items:
        main_cat, sub_cat = categorize_item(item)
        print(f"{item:<25} | {main_cat:<12} | {sub_cat:<12}")

# Allow running as a script
if __name__ == "__main__":
    categorize_grocery_file()
# Description: The "brain" of the application. It automatically assigns categories to items based on their names.

# Responsibilities:

# Checks item names against a database of keywords (e.g., mapping "Avocado" to "Produce" ).
# +1

# Ensures every item has a label for the charts.

# Key Methods:
# spending_report.py

import re
from datetime import datetime, timedelta

# ---------------- CATEGORY TARGETS ----------------
CATEGORY_TARGETS = {
    "Groceries": 50,
    "Dining Out": 40,
    "Shopping": 100,
    "Other": 60
}

# ---------------- CATEGORIZATION ----------------
def categorize_item(item_name):
    name = item_name.lower()

    if any(x in name for x in ["apple", "banana", "lettuce", "corn"]):
        return "Groceries", "Produce"
    elif any(x in name for x in ["milk", "cheese", "yogurt"]):
        return "Groceries", "Dairy"
    elif any(x in name for x in ["steak", "chicken", "beef"]):
        return "Groceries", "Meat"
    elif any(x in name for x in ["chip", "cookie", "oreo"]):
        return "Groceries", "Snacks"
    elif any(x in name for x in ["uber", "restaurant", "coffee"]):
        return "Dining Out", "General"
    elif any(x in name for x in ["amazon", "walmart"]):
        return "Shopping", "General"
    else:
        return "Other", "General"

# ---------------- RECEIPT PARSING ----------------
def parse_receipt_txt(filepath):
    items = []
    current_date = datetime.now()

    with open(filepath, "r", encoding="utf-8") as file:
        lines = file.readlines()

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if any(x in line.lower() for x in ["total", "tax", "subtotal"]):
            continue

        match = re.search(r"(.+?)\s+(\d+\.\d{2})$", line)
        if match:
            name = match.group(1)
            price = float(match.group(2))
            category, subcategory = categorize_item(name)

            items.append({
                "name": name,
                "price": price,
                "category": category,
                "subcategory": subcategory,
                "date": current_date
            })

    return items

# ---------------- AGGREGATION ----------------
def filter_items(items, view_mode="Month"):
    now = datetime.now()
    if view_mode == "Week":
        return [i for i in items if i["date"] >= now - timedelta(days=7)]
    return items

def total_spent(items):
    return sum(i["price"] for i in items)

def totals_by_category(items):
    totals = {}
    for i in items:
        totals[i["category"]] = totals.get(i["category"], 0) + i["price"]
    return totals
