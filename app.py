
from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = "findit-project-key"

DATABASE = "findit.db"


# Database connection
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# Create database and table
def initialize_database():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            status TEXT NOT NULL,
            description TEXT,
            location TEXT NOT NULL,
            contact TEXT NOT NULL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


# Homepage and search
@app.route("/", methods=["GET"])
def home():
    search = request.args.get("search", "").strip()

    conn = get_db()

    if search:
        items = conn.execute("""
            SELECT * FROM items
            WHERE name LIKE ?
            OR category LIKE ?
            OR location LIKE ?
            OR description LIKE ?
            ORDER BY id DESC
        """, tuple([f"%{search}%"] * 4)).fetchall()
    else:
        items = conn.execute("""
            SELECT * FROM items ORDER BY id DESC
        """).fetchall()

    conn.close()

    return render_template(
        "index.html",
        items=items,
        search=search
    )


# Report Lost or Found item
@app.route("/report", methods=["GET", "POST"])
def report():

    status = request.args.get("status", "Lost")

    if status not in ("Lost", "Found"):
        status = "Lost"

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        category = request.form.get("category", "").strip()
        description = request.form.get("description", "").strip()
        location = request.form.get("location", "").strip()
        contact = request.form.get("contact", "").strip()
        status = request.form.get("status", status).strip()

        if not all([name, category, location, contact]):
            return "Please fill all required fields.", 400

        if status not in ("Lost", "Found"):
            return "Invalid status.", 400

        conn = get_db()

        conn.execute("""
            INSERT INTO items
            (name, category, status, description, location, contact)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, category, status, description, location, contact))

        conn.commit()
        conn.close()

        return redirect(url_for("home"))

    return render_template("report.html", status=status)


# Test page
@app.route("/test")
def test():
    return """
    <html>
    <body style="background:#eaf2ff;text-align:center;padding:100px;">
        <h1 style="color:blue;">FindIt is Working!</h1>
        <h2>Welcome to Lost and Found</h2>
        <p>Your Flask application is running successfully.</p>
    </body>
    </html>
    """


if __name__ == "__main__":
    initialize_database()
    app.run(host="0.0.0.0", port=5000, debug=True)
