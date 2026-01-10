# Description: The "database" and calculator. It manages the storage of all receipt history and calculates statistics for the dashboard.

# Responsibilities:

# Saves new receipts to a list (or file/database).

# Aggregates data for specific timeframes (Weekly, Monthly, Yearly).
# +1

# Calculates category percentages for the donut chart.

# Key Methods:

# add_receipt(receipt): Saves a transaction.

# get_weekly_spending(): Returns the total dollar amount for the current week.

# get_category_breakdown(): Returns data formatted for the dashboard charts.