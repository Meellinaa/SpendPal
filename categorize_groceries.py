from SmartCategorizer import categorize_item

with open('grocery_items_cleaned.txt') as f:
    items = [line.strip() for line in f if line.strip()]

print(f"{'Item':<15} | {'Main Category':<12} | {'Subcategory':<12}")
print('-'*45)
for item in items:
    main_cat, sub_cat = categorize_item(item)
    print(f"{item:<15} | {main_cat:<12} | {sub_cat:<12}")
