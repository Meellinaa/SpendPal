import customtkinter as ctk
from tkinter import filedialog

# --- INTERNAL FAKE CATEGORIZER ---
def get_mock_category(item_name):
    name = item_name.lower()
    if any(x in name for x in ["apple", "banana", "lettuce", "corn"]):
        return "Produce"
    elif any(x in name for x in ["milk", "cheese", "yogurt"]):
        return "Dairy"
    elif any(x in name for x in ["steak", "chicken", "beef", "meat"]):
        return "Meat"
    elif any(x in name for x in ["chip", "cookie", "oreo", "snack"]):
        return "Snacks"
    else:
        return "Other"

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Setup
        self.title("SnapCart (Lite Mode)")
        self.geometry("800x600")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # --- SIDEBAR ---
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        
        ctk.CTkLabel(self.sidebar, text="SNAPCART", font=("Arial", 20, "bold")).pack(pady=20)
        
        # Upload Button
        self.btn_upload = ctk.CTkButton(self.sidebar, text="Upload Receipt", command=self.run_demo_scan)
        self.btn_upload.pack(pady=10, padx=20)

        # --- MAIN AREA ---
        self.main_area = ctk.CTkFrame(self, fg_color="transparent")
        self.main_area.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        # Top: Total
        self.top_frame = ctk.CTkFrame(self.main_area, fg_color="transparent")
        self.top_frame.pack(fill="x", pady=10)

        self.lbl_total = ctk.CTkLabel(self.top_frame, text="Total: $0.00", font=("Arial", 40, "bold"))
        self.lbl_total.pack(side="left")

        # Bottom: Item List
        self.scroll_frame = ctk.CTkScrollableFrame(self.main_area, label_text="Receipt Items")
        self.scroll_frame.pack(fill="both", expand=True)

    def run_demo_scan(self):
        # 1. Ask user for file (Visual only)
        file_path = filedialog.askopenfilename()
        if not file_path: return

        print("Running demo scan...")

        # 2. CREATE FAKE DATA
        raw_items = [
            ("Gala Apples", 4.50),
            ("Organic Milk", 5.20),
            ("Ribeye Steak", 22.00),
            ("Doritos Nacho", 4.99),
            ("Oreo Cookies", 3.50),
            ("Cheddar Cheese", 6.00),
            ("Bananas", 1.50)
        ]

        # 3. USE INTERNAL CATEGORIZER
        processed_items = []
        total = 0.0
        
        for name, price in raw_items:
            category = get_mock_category(name) 
            processed_items.append({"name": name, "price": price, "category": category})
            total += price

        # 4. Update UI
        self.lbl_total.configure(text=f"Total: ${total:.2f}")
        self.display_items(processed_items)

    def display_items(self, items):
        # Clear old items
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        # Add Header
        header = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        header.pack(fill="x", pady=2)
        ctk.CTkLabel(header, text="ITEM NAME", font=("Arial", 12, "bold"), width=200, anchor="w").pack(side="left", padx=10)
        ctk.CTkLabel(header, text="CATEGORY", font=("Arial", 12, "bold"), width=100, anchor="w").pack(side="left", padx=10)
        ctk.CTkLabel(header, text="PRICE", font=("Arial", 12, "bold"), width=80, anchor="e").pack(side="right", padx=10)

        # Add Items
        for item in items:
            row = ctk.CTkFrame(self.scroll_frame)
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=item['name'], width=200, anchor="w").pack(side="left", padx=10)
            ctk.CTkLabel(row, text=item['category'], text_color="#3B82F6", width=100, anchor="w").pack(side="left", padx=10)
            ctk.CTkLabel(row, text=f"${item['price']:.2f}", font=("Arial", 12, "bold"), width=80, anchor="e").pack(side="right", padx=10)

if __name__ == "__main__":
    print("--- Starting App ---")
    app = App()
    app.mainloop()
