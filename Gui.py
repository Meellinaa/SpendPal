import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
from datetime import datetime
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# --- YOUR CUSTOM MODULES ---
# Ensure these files are in the same folder!
from OCRProcessor import OCRProcessor
from CloudManager import CloudManager
from Receipt import Receipt

class SnapCartApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("SnapCart - All-in-One")
        self.geometry("1100x800")
        ctk.set_appearance_mode("dark")
        
        # Initialize Engines
        self.ocr_engine = OCRProcessor()
        self.cloud_manager = CloudManager()
        self.all_scanned_items = [] 
        
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
        
        # Setup UI
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
            
            # 1. Save to Cloud (Returns FIXED items with categories)
            categorized_items = self.cloud_manager.process_and_save(data['items'], data['total'])
            
            # 2. Update local memory
            self.all_scanned_items.extend(categorized_items)
            
            # 3. Update UI
            self.after(0, lambda: self.display_editor_items(categorized_items))
            self.after(0, lambda: self.lbl_total.configure(text=f"TOTAL: ${data['total']:.2f}"))
            
            # 4. Refresh Report
            self.after(0, self.refresh_report)
            self.after(0, lambda: self.btn_scan.configure(state="normal", text="📸 Scan Receipt"))
            
        except Exception as e:
            print(f"Error in OCR thread: {e}")
            self.after(0, lambda: self.btn_scan.configure(state="normal", text="📸 Scan Receipt"))

    def display_editor_items(self, items):
        # Clear old rows
        for w in self.scroll_frame.winfo_children(): w.destroy()
        self.item_rows.clear()
        
        # FIX: Handle the dictionary format from CloudManager
        for item in items:
            name = item['name']
            price = item['price']
            
            row = ctk.CTkFrame(self.scroll_frame)
            row.pack(fill="x", pady=2)
            
            ent_name = ctk.CTkEntry(row, height=30)
            ent_name.insert(0, name)
            ent_name.pack(side="left", padx=10, fill="x", expand=True)
            
            ent_price = ctk.CTkEntry(row, width=80)
            ent_price.insert(0, f"{price:.2f}")
            ent_price.pack(side="right", padx=10)
            
            self.item_rows.append({"name": ent_name, "price": ent_price})

    # ---------------- REPORT LOGIC ----------------
    def setup_report_ui(self):
        # Create initial structure (called once at startup)
        self.report_frame.grid_columnconfigure(0, weight=1)
        self.report_frame.grid_rowconfigure(0, weight=1)
        self.report_frame.grid_rowconfigure(1, weight=2)
        # Initial draw
        self.refresh_report()

    def refresh_report(self):
        # 1. Clear previous view
        for widget in self.report_frame.winfo_children():
            widget.destroy()

        # --- A. PIE CHART (Top) ---
        chart_frame = ctk.CTkFrame(self.report_frame, fg_color="transparent")
        chart_frame.grid(row=0, column=0, sticky="nsew", pady=10)
        
        totals = {}
        all_receipts = list(self.cloud_manager.receipts_col.find().sort("date", -1))
        
        for receipt in all_receipts:
            for item in receipt.get("items", []):
                cat = item.get("category", "Other")
                price = item.get("price", 0.0)
                totals[cat] = totals.get(cat, 0) + price

        if totals:
            fig = plt.Figure(figsize=(5, 4), dpi=100)
            fig.patch.set_facecolor('#2b2b2b')
            ax = fig.add_subplot(111)
            
            labels = list(totals.keys())
            sizes = list(totals.values())
            colors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6']
            
            wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%',
                                            startangle=90, colors=colors[:len(labels)])
            
            for text in texts + autotexts: text.set_color('white')
            ax.set_title(f"Total Spent: ${sum(sizes):.2f}", color="white")
            
            canvas = FigureCanvasTkAgg(fig, master=chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
        else:
            ctk.CTkLabel(chart_frame, text="No Data Yet").pack(pady=50)

        # --- B. ITEMIZED LIST (Bottom) ---
        list_label = ctk.CTkLabel(self.report_frame, text="Recent Transactions", font=("Arial", 16, "bold"))
        list_label.grid(row=1, column=0, sticky="w", padx=20, pady=(10,0))

        scroll_frame = ctk.CTkScrollableFrame(self.report_frame, label_text="Item History")
        scroll_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)

        for receipt in all_receipts:
            date_str = receipt['date'].strftime("%Y-%m-%d %H:%M")
            header_text = f"🛒 {receipt.get('store', 'Receipt')} ({date_str})"
            
            trip_frame = ctk.CTkFrame(scroll_frame)
            trip_frame.pack(fill="x", pady=5)
            
            ctk.CTkLabel(trip_frame, text=header_text, font=("Arial", 12, "bold"), text_color="#3B82F6").pack(anchor="w", padx=10, pady=2)

            for item in receipt.get("items", []):
                item_row = ctk.CTkFrame(trip_frame, fg_color="transparent")
                item_row.pack(fill="x", padx=10, pady=1)
                
                name = item.get('name', 'Unknown')
                cat = item.get('category', 'General')
                price = item.get('price', 0.0)

                ctk.CTkLabel(item_row, text=f"• {name}", width=200, anchor="w").pack(side="left")
                ctk.CTkLabel(item_row, text=cat, text_color="gray").pack(side="left", padx=10)
                ctk.CTkLabel(item_row, text=f"${price:.2f}").pack(side="right")

if __name__ == "__main__":
    app = SnapCartApp()
    app.mainloop()