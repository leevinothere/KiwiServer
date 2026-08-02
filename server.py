from flask import Flask, request, abort, jsonify
from flask_cors import CORS
from supabase import create_client
import os

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

app = Flask(__name__)
CORS(app)

WEBSITE_FOLDER = "websites"

@app.route("/")
def index():
    return "🥝 Kiwi Server is running!"


@app.route("/site/<name>")
def get_site(name):
    name = name.lower().strip()

    response = (
        supabase.table("websites")
        .select("html")
        .eq("name", name)
        .execute()
    )

    if response.data:
        return response.data[0]["html"]

    # Then check GitHub websites folder
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

    supabase.table("websites").upsert({
        "name": name,
        "html": html
    }).execute()

    print("Saved website:", name)

    return jsonify(success=True)

@app.route("/websites")
def list_websites():

    response = (
        supabase.table("websites")
        .select("name")
        .execute()
    )

    database_sites = [row["name"] for row in response.data]

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

@app.route("/search")
def search():
    query = request.args.get("q", "").lower().strip()

    response = (
        supabase.table("websites")
        .select("name")
        .execute()
    )

    html = f"""
    <h1>🥝 Kiwi Search</h1>
    <h2>Results for "{query}"</h2>
    """

    found = False

    all_sites = []

    # Supabase websites
    for row in response.data:
        all_sites.append(row["name"])

    # Built-in websites
    if os.path.exists(WEBSITE_FOLDER):
        for file in os.listdir(WEBSITE_FOLDER):
            if file.endswith(".html"):
                all_sites.append(file[:-5])

    # Remove duplicates
    all_sites = sorted(set(all_sites))

    # Search everything
    for name in all_sites:
        if query in name.lower():
            found = True
            html += f"""
            <p>
                <a href="/site/{name}">
                    🥝 {name}
                </a>
            </p>
            """

    if not found:
        html += "<p>No Kiwi websites found.</p>"

    return html
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=3000
    )
