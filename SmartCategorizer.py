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
