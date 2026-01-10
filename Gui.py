# At the top of Gui.py
from Receipt import Receipt         # <--- Must match file name 'Receipt.py'
from CloudManager import CloudManager # <--- Must match file name 'CloudManager.py'
import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import re
from datetime import datetime, timedelta
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# --- IMPORT YOUR BACKEND ---
from OCRProcessor import OCRProcessor
from CloudManager import CloudManager
from Receipt import Receipt
from types import SimpleNamespace
from SmartCategorizer import categorize_item

class SnapCartApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("SnapCart - All-in-One")
        self.geometry("1100x800")
        ctk.set_appearance_mode("dark")
        
        # Initialize Engines
        self.ocr_engine = OCRProcessor()
        self.cloud_manager = CloudManager()
        self.all_scanned_items = [] # To hold data for the report (list of item dicts)
        self.receipts = [] # List of `Receipt` objects for each scanned receipt
        
        # --- SIDEBAR ---
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        
        ctk.CTkLabel(self.sidebar, text="SNAPCART", font=("Arial", 20, "bold")).pack(pady=20)
        
        self.btn_editor = ctk.CTkButton(self.sidebar, text="📝 Receipt Editor", command=self.show_editor)
        self.btn_editor.pack(pady=10, padx=10)
        
        self.btn_report = ctk.CTkButton(self.sidebar, text="📊 Spending Report", command=self.show_report)
        self.btn_report.pack(pady=10, padx=10)

        # --- MAIN CONTENT AREA ---
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(side="right", fill="both", expand=True, padx=20, pady=20)
        
        # Initialize Frames
        self.editor_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.report_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        
        self.setup_editor_ui()
        self.setup_report_ui()
        
        # Start at Editor
        self.show_editor()

    # ---------------- TAB NAVIGATION ----------------
    def show_editor(self):
        self.report_frame.pack_forget()
        self.editor_frame.pack(fill="both", expand=True)
        self.btn_editor.configure(fg_color="#2563EB")
        self.btn_report.configure(fg_color="transparent")

    def show_report(self):
        self.editor_frame.pack_forget()
        self.report_frame.pack(fill="both", expand=True)
        self.btn_report.configure(fg_color="#2563EB")
        self.btn_editor.configure(fg_color="transparent")
        self.refresh_report()

    # ---------------- EDITOR LOGIC ----------------
    def setup_editor_ui(self):
        self.item_rows = []
        top = ctk.CTkFrame(self.editor_frame, fg_color="transparent")
        top.pack(fill="x", pady=10)
        
        ctk.CTkLabel(top, text="RECEIPT EDITOR", font=("Arial", 22, "bold")).pack(side="left")
        self.btn_scan = ctk.CTkButton(top, text="📸 Scan Receipt", command=self.start_scan)
        self.btn_scan.pack(side="right")

        self.lbl_total = ctk.CTkLabel(self.editor_frame, text="TOTAL: $0.00", font=("Arial", 35, "bold"), text_color="#10B981")
        self.lbl_total.pack(pady=10)

        self.scroll_frame = ctk.CTkScrollableFrame(self.editor_frame, label_text="Scanned Items")
        self.scroll_frame.pack(fill="both", expand=True, pady=10)

    def start_scan(self):
        file_path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.png *.jpeg")])
        if not file_path: return
        self.btn_scan.configure(state="disabled", text="Scanning...")
        threading.Thread(target=self.run_ocr_thread, args=(file_path,)).start()

    def run_ocr_thread(self, file_path):
        try:
            raw_text = self.ocr_engine.extract_text(file_path)
            data = self.ocr_engine.parse_receipt(raw_text)

            # Categorize items using the grocery item categorizer
            categorized_items = []
            for name, price in data['items']:
                category, subcategory = categorize_item(name)
                categorized_items.append({
                    'name': name,
                    'price': price,
                    'category': category,
                    'subcategory': subcategory
                })

            # Save to cloud
            self.categorized_items = self.cloud_manager.process_and_save(
                [(item['name'], item['price']) for item in categorized_items], data['total']
            )

            # Build a Receipt object for this scan and store it
            receipt_obj = Receipt(store_name="Unknown", date=datetime.now())
            for it in categorized_items:
                item_obj = SimpleNamespace(name=it.get('name'), price=it.get('price'), category=it.get('category'), subcategory=it.get('subcategory'))
                receipt_obj.add_item(item_obj)
            self.receipts.append(receipt_obj)

            # Store for the report tab (preserve existing structure)
            self.all_scanned_items.extend(categorized_items)

            self.after(0, lambda: self.display_editor_items(data['items']))
            self.after(0, lambda: self.lbl_total.configure(text=f"TOTAL: ${data['total']:.2f}"))
        finally:
            self.after(0, lambda: self.btn_scan.configure(state="normal", text="📸 Scan Receipt"))

    def display_editor_items(self, items):
        for w in self.scroll_frame.winfo_children(): w.destroy()
        self.item_rows.clear()
        for name, price in items:
            row = ctk.CTkFrame(self.scroll_frame)
            row.pack(fill="x", pady=2)
            ent_name = ctk.CTkEntry(row, height=30); ent_name.insert(0, name); ent_name.pack(side="left", padx=10, fill="x", expand=True)
            ent_price = ctk.CTkEntry(row, width=80); ent_price.insert(0, f"{price:.2f}"); ent_price.pack(side="right", padx=10)
            self.item_rows.append({"name": ent_name, "price": ent_price})

    # ---------------- REPORT LOGIC ----------------
    def setup_report_ui(self):
        ctk.CTkLabel(self.report_frame, text="SPENDING ANALYTICS", font=("Arial", 22, "bold")).pack(pady=10)
        
        self.report_total = ctk.CTkLabel(self.report_frame, text="All-Time Spent: $0.00", font=("Arial", 18))
        self.report_total.pack()

        self.fig_frame = ctk.CTkFrame(self.report_frame)
        self.fig_frame.pack(fill="both", expand=True, pady=20)

    def refresh_report(self):
        # Clear old chart
        for w in self.fig_frame.winfo_children(): w.destroy()
        
        if not self.all_scanned_items:
            ctk.CTkLabel(self.fig_frame, text="No data. Scan a receipt in the Editor tab first!").pack(pady=50)
            return

        # Simple Aggregation
        totals = {}
        for item in self.all_scanned_items:
            cat = item.get('category', 'Other')
            totals[cat] = totals.get(cat, 0) + item['price']

        self.report_total.configure(text=f"All-Time Spent: ${sum(totals.values()):.2f}")

        # Draw Chart
        fig = Figure(figsize=(5, 4), facecolor="#2b2b2b")
        ax = fig.add_subplot(111)
        ax.pie(totals.values(), labels=totals.keys(), autopct='%1.1f%%', colors=['#2563EB', '#10B981', '#F59E0B', '#EF4444'])
        ax.set_title("Spending by Category", color="white")
        
        canvas = FigureCanvasTkAgg(fig, self.fig_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

if __name__ == "__main__":
    app = SnapCartApp()
    app.mainloop()