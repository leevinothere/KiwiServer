from flask import Flask, request, abort, jsonify
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)

DATABASE = "kiwi.db"
WEBSITE_FOLDER = "websites"


def create_database():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS websites (
        name TEXT PRIMARY KEY,
        html TEXT
    )
    """)

    conn.commit()
    conn.close()


create_database()


@app.route("/")
def index():
    return "🥝 Kiwi Server is running!"


@app.route("/site/<name>")
def get_site(name):
    name = name.lower().strip()

    # First check database (user websites)
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT html FROM websites WHERE name = ?",
        (name,)
    )

    result = cursor.fetchone()

    conn.close()

    if result:
        return result[0]


    # Then check GitHub websites folder (built-in Kiwi pages)
    filename = os.path.join(
        WEBSITE_FOLDER,
        f"{name}.html"
    )

    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return f.read()


    abort(404)


@app.route("/publish", methods=["POST"])
def publish():

    data = request.get_json()

    if not data:
        return jsonify(success=False)


    name = data.get("name", "").lower().strip()
    html = data.get("html", "")


    if not name or not html:
        return jsonify(success=False)


    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR REPLACE INTO websites (name, html)
    VALUES (?, ?)
    """, (name, html))


    conn.commit()
    conn.close()


    print("Saved website:", name)

    return jsonify(success=True)


@app.route("/websites")
def list_websites():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT name FROM websites"
    )

    database_sites = [
        row[0]
        for row in cursor.fetchall()
    ]

    conn.close()


    # Add built-in pages too
    folder_sites = []

    if os.path.exists(WEBSITE_FOLDER):
        for file in os.listdir(WEBSITE_FOLDER):
            if file.endswith(".html"):
                folder_sites.append(
                    file[:-5]
                )


    all_sites = sorted(
        set(database_sites + folder_sites)
    )

    return jsonify(all_sites)


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=3000
    )
