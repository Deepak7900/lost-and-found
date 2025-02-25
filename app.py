

from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Database setup
DATABASE = "lost_found.db"

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
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

# Home page
@app.route("/")
def home():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items")
    items = cursor.fetchall()
    conn.close()
    return render_template("index.html", items=items)

# Add item
@app.route("/add", methods=["GET", "POST"])
def add_item():
    if request.method == "POST":
        name = request.form["name"]
        category = request.form["category"]
        location = request.form["location"]
        status = request.form["status"]
        phone = request.form["phone"]
        image = request.files["image"]

        if name and category and location and status:
            # Save the image
            image_path = ""
            if image:
                image_path = os.path.join("static/uploads", image.filename)
                image.save(image_path)

            # Save to database
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO items (name, category, location, status, phone, image_path) VALUES (?, ?, ?, ?, ?, ?)",
                           (name, category, location, status, phone, image_path))
            conn.commit()
            conn.close()
            flash("Item added successfully!", "success")
            return redirect(url_for("home"))
        else:
            flash("Please fill in all fields.", "error")
    return render_template("add_item.html")

# Delete item
@app.route("/delete/<int:item_id>")
def delete_item(item_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM items WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    flash("Item deleted successfully!", "success")
    return redirect(url_for("home"))

# Initialize database
init_db()

# Run the app
if __name__ == "__main__":
    # Create uploads folder if it doesn't exist
    if not os.path.exists("static/uploads"):
        os.makedirs("static/uploads")
    app.run(debug=True)