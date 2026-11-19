# 🛒 SpendPal

A desktop app that turns grocery receipts into a budget tracker. Snap or upload a receipt, and SpendPal reads it, sorts every item into a category and shows where your money goes.

## The problem

Tracking grocery spending by hand is tedious, so most people stop doing it and lose track of their budget. SpendPal makes logging a receipt take seconds.

## Features

- **🧾 Receipt OCR** – reads receipt images with Tesseract and pulls out item names, prices and the total.
- **🏷️ Smart categories** – auto-sorts items (produce, dairy, meat, snacks, …) using a keyword-based categorizer.
- **📊 Budget tracking** – totals by category and by time period (week / month) so you can see if you're on budget.
- **☁️ Cloud storage** – saves receipts to MongoDB Atlas so your history follows you.
- **🖥️ Desktop GUI** – built with CustomTkinter.

## Tech stack

Python · CustomTkinter · Tesseract OCR (pytesseract) · Pillow · MongoDB Atlas (pymongo)

## Run it locally

```bash
brew install tesseract          # or your OS's Tesseract package
pip install customtkinter pytesseract pillow pymongo certifi
python Gui.py
```

## Project structure

```
Gui.py               # Desktop interface
OCRProcessor.py      # Receipt image → text → items
SmartCategorizer.py  # Item → category, totals by category and period
CloudManager.py      # MongoDB storage
Receipt.py           # Receipt data model
```
