import sqlite3
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import os

# Function to Update Database Schema
def update_db_schema():
    conn = sqlite3.connect("lost_found.db")
    cursor = conn.cursor()
    
    # Check if the table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='items'")
    table_exists = cursor.fetchone()
    
    if table_exists:
        # Add phone column if it does not exist
        cursor.execute("PRAGMA table_info(items)")
        columns = [column[1] for column in cursor.fetchall()]
        if "phone" not in columns:
            cursor.execute("ALTER TABLE items ADD COLUMN phone TEXT")
        
        # Add image_path column if it does not exist
        if "image_path" not in columns:
            cursor.execute("ALTER TABLE items ADD COLUMN image_path TEXT")
    
    conn.commit()
    conn.close()

# Initialize Database
def init_db():
    conn = sqlite3.connect("lost_found.db")
    cursor = conn.cursor()
    
    # Create table if it does not exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            location TEXT NOT NULL,
            status TEXT NOT NULL,
            phone TEXT,
            image_path TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

# Function to Add Item
def add_item():
    name = entry_name.get()
    category = entry_category.get()
    location = entry_location.get()
    status = entry_status.get()
    phone = entry_phone.get()
    image_path = label_image_path["text"]

    if name and category and location and status:
        conn = sqlite3.connect("lost_found.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO items (name, category, location, status, phone, image_path) VALUES (?, ?, ?, ?, ?, ?)", 
                       (name, category, location, status, phone, image_path))
        conn.commit()
        conn.close()
        update_table()
        clear_entries()
    else:
        messagebox.showerror("Error", "Please fill in all fields.")

# Function to Update Table
def update_table():
    for row in tree.get_children():
        tree.delete(row)

    conn = sqlite3.connect("lost_found.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items")
    rows = cursor.fetchall()
    conn.close()

    for row in rows:
        tree.insert("", END, values=row)

# Function to Clear Entry Fields
def clear_entries():
    entry_name.delete(0, END)
    entry_category.delete(0, END)
    entry_location.delete(0, END)
    entry_status.delete(0, END)
    entry_phone.delete(0, END)
    label_image_path.config(text="")
    image_label.config(image="")

# Function to Delete an Item
def delete_item():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "Please select an item to delete.")
        return

    item_id = tree.item(selected_item, 'values')[0]

    conn = sqlite3.connect("lost_found.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM items WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()

    update_table()

# Function to Upload Image
def upload_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
    if file_path:
        label_image_path.config(text=file_path)
        display_image(file_path)

# Function to Display Image
def display_image(file_path):
    image = Image.open(file_path)
    image.thumbnail((100, 100))
    photo = ImageTk.PhotoImage(image)
    image_label.config(image=photo)
    image_label.image = photo

# Function to Show Selected Item Details
def show_item_details(event):
    selected_item = tree.selection()
    if selected_item:
        item_id = tree.item(selected_item, 'values')[0]
        conn = sqlite3.connect("lost_found.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
        item = cursor.fetchone()
        conn.close()

        if item:
            entry_name.insert(0, item[1])
            entry_category.insert(0, item[2])
            entry_location.insert(0, item[3])
            entry_status.insert(0, item[4])
            entry_phone.insert(0, item[5])
            if item[6]:
                display_image(item[6])

# Initialize GUI
root = ttk.Window(themename="darkly")  # Dark mode
root.title("Lost & Found Management")
root.geometry("1000x600")

# Frame for Form
frame_form = ttk.Frame(root, padding=10)
frame_form.pack(side=TOP, fill=X)

ttk.Label(frame_form, text="Name:").grid(row=0, column=0, padx=5, pady=5)
entry_name = ttk.Entry(frame_form)
entry_name.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(frame_form, text="Category:").grid(row=0, column=2, padx=5, pady=5)
entry_category = ttk.Entry(frame_form)
entry_category.grid(row=0, column=3, padx=5, pady=5)

ttk.Label(frame_form, text="Location:").grid(row=1, column=0, padx=5, pady=5)
entry_location = ttk.Entry(frame_form)
entry_location.grid(row=1, column=1, padx=5, pady=5)

ttk.Label(frame_form, text="Status:").grid(row=1, column=2, padx=5, pady=5)
entry_status = ttk.Entry(frame_form)
entry_status.grid(row=1, column=3, padx=5, pady=5)

ttk.Label(frame_form, text="Phone:").grid(row=2, column=0, padx=5, pady=5)
entry_phone = ttk.Entry(frame_form)
entry_phone.grid(row=2, column=1, padx=5, pady=5)

ttk.Label(frame_form, text="Image:").grid(row=2, column=2, padx=5, pady=5)
label_image_path = ttk.Label(frame_form, text="", foreground="blue")
label_image_path.grid(row=2, column=3, padx=5, pady=5)
btn_upload = ttk.Button(frame_form, text="Upload Image", command=upload_image)
btn_upload.grid(row=2, column=4, padx=5, pady=5)

btn_add = ttk.Button(frame_form, text="Add Item", command=add_item)
btn_add.grid(row=3, column=0, columnspan=2, pady=10)

btn_delete = ttk.Button(frame_form, text="Delete Selected", command=delete_item)
btn_delete.grid(row=3, column=2, columnspan=2, pady=10)

# Image Display Label
image_label = ttk.Label(frame_form)
image_label.grid(row=0, column=5, rowspan=4, padx=10, pady=10)

# Table Frame
frame_table = ttk.Frame(root, padding=10)
frame_table.pack(side=BOTTOM, fill=BOTH, expand=True)

columns = ("ID", "Name", "Category", "Location", "Status", "Phone", "Image Path")
tree = ttk.Treeview(frame_table, columns=columns, show="headings")
tree.pack(fill=BOTH, expand=True)

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=100)

# Bind selection event to show item details
tree.bind("<<TreeviewSelect>>", show_item_details)

# Update Database Schema and Initialize Database
update_db_schema()
init_db()
update_table()

root.mainloop()