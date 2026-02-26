import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

# ================= DATABASE =================
conn = sqlite3.connect("gymstore.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS products(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    category TEXT,
    price REAL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS cart(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    price REAL
)
""")

conn.commit()

def insert_default_products():
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        products = [

            # Supplements
            ("Whey Protein","Supplements",2500),
            ("Mass Gainer","Supplements",3000),
            ("Creatine","Supplements",1200),
            ("BCAA","Supplements",1500),
            ("Pre Workout","Supplements",1800),
            ("Multivitamin","Supplements",800),

            # Equipment
            ("Dumbbells","Equipment",2000),
            ("Barbell","Equipment",3500),
            ("Treadmill","Equipment",45000),
            ("Bench Press","Equipment",8000),
            ("Kettlebell","Equipment",1500),
            ("Resistance Band","Equipment",500),

            # Gym Clothes
            ("Gym T-Shirt","Gym Clothes",700),
            ("Track Pants","Gym Clothes",900),
            ("Gym Shorts","Gym Clothes",600),
            ("Gym Hoodie","Gym Clothes",1200),
            ("Training Jacket","Gym Clothes",1500),
            ("Gym Cap","Gym Clothes",400),

            # Accessories
            ("Shaker Bottle","Accessories",300),
            ("Gym Gloves","Accessories",500),
            ("Lifting Belt","Accessories",1200),
            ("Skipping Rope","Accessories",250),
            ("Gym Bag","Accessories",1500),
            ("Wrist Wraps","Accessories",350),
        ]
        cursor.executemany("INSERT INTO products (name, category, price) VALUES (?, ?, ?)", products)
        conn.commit()

insert_default_products()

# ================= MAIN WINDOW =================
root = tk.Tk()
root.title("Gym Store Management System")
root.geometry("1000x650")
root.configure(bg="#1e1e2f")

# ================= STYLE (CSS LIKE) =================
style = ttk.Style()
style.theme_use("clam")

style.configure("TButton",
                font=("Segoe UI", 10, "bold"),
                padding=6,
                background="#4CAF50",
                foreground="white")

style.map("TButton",
          background=[("active", "#45a049")])

style.configure("TCombobox",
                padding=5)

# ================= FRAMES =================
left_frame = tk.Frame(root, bg="#2b2b3c", padx=20, pady=20)
left_frame.pack(side="left", fill="both", expand=True)

right_frame = tk.Frame(root, bg="#2b2b3c", padx=20, pady=20)
right_frame.pack(side="right", fill="both", expand=True)

# ================= PRODUCT SECTION =================
tk.Label(left_frame, text="Products",
         font=("Segoe UI", 16, "bold"),
         bg="#2b2b3c",
         fg="white").pack()

product_list = tk.Listbox(left_frame,
                          width=45,
                          height=18,
                          bg="#1e1e2f",
                          fg="white",
                          font=("Segoe UI", 10))
product_list.pack(pady=10)

# ================= CART SECTION =================
tk.Label(right_frame, text="Cart",
         font=("Segoe UI", 16, "bold"),
         bg="#2b2b3c",
         fg="white").pack()

cart_list = tk.Listbox(right_frame,
                       width=45,
                       height=18,
                       bg="#1e1e2f",
                       fg="white",
                       font=("Segoe UI", 10))
cart_list.pack(pady=10)

# ================= FUNCTIONS =================
def show_products(category):
    product_list.delete(0, tk.END)
    cursor.execute("SELECT id,name,price FROM products WHERE category=?", (category,))
    for row in cursor.fetchall():
        product_list.insert(tk.END, f"{row[0]} | {row[1]} | ₹{row[2]}")

def add_to_cart():
    selected = product_list.get(tk.ACTIVE)
    if selected:
        pid = selected.split("|")[0].strip()
        cursor.execute("SELECT name,price FROM products WHERE id=?", (pid,))
        product = cursor.fetchone()
        cursor.execute("INSERT INTO cart (name,price) VALUES (?,?)", product)
        conn.commit()
        view_cart()

def view_cart():
    cart_list.delete(0, tk.END)
    cursor.execute("SELECT id,name,price FROM cart")
    total = 0
    for row in cursor.fetchall():
        cart_list.insert(tk.END, f"{row[0]} | {row[1]} | ₹{row[2]}")
        total += row[2]
    total_label.config(text=f"Total: ₹{total}")

def remove_from_cart():
    selected = cart_list.get(tk.ACTIVE)
    if selected:
        cid = selected.split("|")[0].strip()
        cursor.execute("DELETE FROM cart WHERE id=?", (cid,))
        conn.commit()
        view_cart()

def apply_discount():
    cursor.execute("SELECT SUM(price) FROM cart")
    total = cursor.fetchone()[0]
    if total:
        discount = float(discount_entry.get())
        final = total - (total * discount / 100)
        messagebox.showinfo("Final Amount", f"After {discount}% Discount:\n₹{final}")

def add_product():
    name = name_entry.get()
    category = category_dropdown.get()
    price = price_entry.get()

    if name == "" or category == "" or price == "":
        messagebox.showerror("Error", "Fill all fields")
        return

    cursor.execute("INSERT INTO products (name,category,price) VALUES (?,?,?)",
                   (name,category,float(price)))
    conn.commit()
    messagebox.showinfo("Success","Product Added")
    name_entry.delete(0, tk.END)
    price_entry.delete(0, tk.END)

# ================= CATEGORY BUTTONS =================
button_frame = tk.Frame(root, bg="#1e1e2f")
button_frame.pack(pady=10)

ttk.Button(button_frame, text="Supplements",
           command=lambda: show_products("Supplements")).grid(row=0,column=0,padx=5)

ttk.Button(button_frame, text="Equipment",
           command=lambda: show_products("Equipment")).grid(row=0,column=1,padx=5)

ttk.Button(button_frame, text="Gym Clothes",
           command=lambda: show_products("Gym Clothes")).grid(row=0,column=2,padx=5)

ttk.Button(button_frame, text="Accessories",
           command=lambda: show_products("Accessories")).grid(row=0,column=3,padx=5)

ttk.Button(button_frame, text="Add to Cart",
           command=add_to_cart).grid(row=1,column=0,pady=10)

ttk.Button(button_frame, text="Remove from Cart",
           command=remove_from_cart).grid(row=1,column=1)

# ================= DISCOUNT =================
discount_entry = tk.Entry(button_frame)
discount_entry.grid(row=2,column=0,pady=5)

ttk.Button(button_frame, text="Apply Discount %",
           command=apply_discount).grid(row=2,column=1)

total_label = tk.Label(button_frame,
                       text="Total: ₹0",
                       font=("Segoe UI", 12, "bold"),
                       bg="#1e1e2f",
                       fg="white")
total_label.grid(row=2,column=2)

# ================= ADD PRODUCT SECTION =================
add_frame = tk.Frame(root, bg="#2b2b3c", pady=15)
add_frame.pack(fill="x")

tk.Label(add_frame, text="Add New Product",
         font=("Segoe UI", 14, "bold"),
         bg="#2b2b3c",
         fg="white").pack()

form_frame = tk.Frame(add_frame, bg="#2b2b3c")
form_frame.pack(pady=10)

name_entry = tk.Entry(form_frame, width=20)
name_entry.grid(row=0,column=0,padx=5)
name_entry.insert(0,"Product Name")

category_dropdown = ttk.Combobox(form_frame,
                                 values=["Supplements","Equipment","Gym Clothes","Accessories"],
                                 width=18)
category_dropdown.grid(row=0,column=1,padx=5)

price_entry = tk.Entry(form_frame, width=15)
price_entry.grid(row=0,column=2,padx=5)
price_entry.insert(0,"Price")

ttk.Button(form_frame, text="Add Product",
           command=add_product).grid(row=0,column=3,padx=5)

# ================= EXIT =================
ttk.Button(root, text="Exit", command=root.quit).pack(pady=10)

root.mainloop()
