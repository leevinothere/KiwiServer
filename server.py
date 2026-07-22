from flask_cors import CORS
from flask import Flask, request, abort, jsonify
import os

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEBSITE_FOLDER = os.path.join(BASE_DIR, "websites")

os.makedirs(WEBSITE_FOLDER, exist_ok=True)

print("Website folder:", WEBSITE_FOLDER)


@app.route("/")
def index():
    return "🥝 Kiwi Server is running!"


@app.route("/site/<name>")
def get_site(name):
    name = name.lower().strip()
    filename = os.path.join(WEBSITE_FOLDER, f"{name}.html")

    print("Looking for:", filename)

    if not os.path.exists(filename):
        abort(404)

    with open(filename, "r", encoding="utf-8") as f:
        return f.read()


@app.route("/publish", methods=["POST"])
def publish():
    data = request.get_json()

    print("Received:", data)

    if not data:
        return jsonify(success=False, error="No JSON received")

    name = data.get("name", "").strip().lower()
    html = data.get("html", "")

    if not name:
        return jsonify(success=False, error="Website name is empty")

    if not html:
        return jsonify(success=False, error="Website HTML is empty")

    filename = os.path.join(WEBSITE_FOLDER, f"{name}.html")

    print("Saving to:", filename)

    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)

    return jsonify(success=True)


@app.route("/websites")
def websites():
    files = []

    for file in os.listdir(WEBSITE_FOLDER):
        if file.endswith(".html"):
            files.append(file[:-5])

    files.sort()

    return jsonify(files)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)