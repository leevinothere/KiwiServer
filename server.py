from flask import Flask, request, abort, jsonify
import sqlite3
import os

app = Flask(__name__)

DATABASE = "kiwi.db"


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

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT html FROM websites WHERE name = ?",
        (name,)
    )

    result = cursor.fetchone()

    conn.close()

    if not result:
        abort(404)

    return result[0]


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
def websites():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM websites")

    sites = cursor.fetchall()

    conn.close()

    return jsonify([site[0] for site in sites])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
