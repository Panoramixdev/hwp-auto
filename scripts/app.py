import os
import json
import traceback
import pandas as pd
from flask import Flask, request, jsonify, render_template

from form_data_handler import process_excel
from generate_docker_compose import generate_docker_compose

app = Flask(
    __name__,
    template_folder="../web",
    static_folder="../web",
    static_url_path="/static"
)

UPLOAD_FOLDER = "config"
PLUGIN_JSON_PATH = "config/available-plugins.json"
CONFIG_JSON_PATH = "config/config.json"
EXCEL_FILENAME = "available-plugins.xlsx"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def generate_plugin_list():
    """(Her)genereer de pluginlijst op basis van config/available-plugins.xlsx + premium map."""
    file_path = os.path.join(UPLOAD_FOLDER, EXCEL_FILENAME)
    plugins = {}
    if os.path.exists(file_path):
        try:
            df = pd.read_excel(file_path)
            for _, row in df.iterrows():
                cat = row["Categorie"]
                plugin = {
                    "name": row["Plugin Naam"],
                    "url": row["Plugin URL"],
                }
                plugins.setdefault(cat, []).append(plugin)
        except Exception as e:
            print(f"Fout in {EXCEL_FILENAME}: {e}")
            traceback.print_exc()

    # Premium plugins
    premium_folder = "config/premium-plugins"
    if os.path.exists(premium_folder):
        plugins["Premium Plugins"] = []
        for f in os.listdir(premium_folder):
            if f.endswith(".zip"):
                plugins["Premium Plugins"].append({
                    "name": f.replace(".zip", ""),
                    "url": f"/config/premium-plugins/{f}",
                    "compatibility": "N/A"
                })

    with open(PLUGIN_JSON_PATH, "w", encoding="utf-8") as pf:
        json.dump(plugins, pf, indent=2)
    print("✅ available-plugins.json hernieuwd!")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/config/config.json", methods=["GET"])
def get_current_config():
    """Maak config.json toegankelijk, zodat de frontend deze kan ophalen."""
    if not os.path.exists(CONFIG_JSON_PATH):
        return jsonify({"status": "⚠️ config.json niet gevonden"}), 404
    try:
        with open(CONFIG_JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        print(f"Fout bij openen config.json: {e}")
        return jsonify({"status": "⚠️ Error"}), 500

@app.route("/config/available-plugins.json", methods=["GET"])
def get_available_plugins():
    """Geef de beschikbare pluginlijst terug."""
    if not os.path.exists(PLUGIN_JSON_PATH):
        return jsonify({"status": "⚠️ available-plugins.json niet gevonden"}), 404
    try:
        with open(PLUGIN_JSON_PATH, "r", encoding="utf-8") as pf:
            plugins = json.load(pf)
        return jsonify(plugins)
    except Exception as e:
        print(f"Fout bij ophalen plugins: {e}")
        traceback.print_exc()
        return jsonify({"status": "⚠️ Error"}), 500

@app.route("/config/update-graphql", methods=["POST"])
def update_graphql():
    """Mock-route om GraphQL-endpoint te 'ontvangen'."""
    try:
        data = request.get_json()
        endpoint = data.get("graphqlEndpoint", "")
        print(f"GraphQL endpoint ontvangen: {endpoint}")
        return jsonify({"status": "GraphQL endpoint updated", "endpoint": endpoint})
    except Exception as e:
        print(f"Fout bij update_graphql: {e}")
        return jsonify({"status": "Error"}), 500

@app.route("/upload-excel", methods=["POST"])
def upload_excel():
    try:
        excel_file = request.files.get("excel_file")
        if not excel_file:
            return jsonify({"status": "Geen excel_file ontvangen"}), 400

        # Sla als 'temp_plugins.xlsx' op
        temp_path = os.path.join(app.config["UPLOAD_FOLDER"], "temp_plugins.xlsx")
        excel_file.save(temp_path)

        # Lees Excel direct in
        plugins = {}
        df = pd.read_excel(temp_path)
        for _, row in df.iterrows():
            cat = row["Categorie"]
            plugin_data = {
                "name": row["Plugin Naam"],
                "url": row["Plugin URL"]
            }
            plugins.setdefault(cat, []).append(plugin_data)

        # Voeg Premium Plugins toe
        premium_folder = "config/premium-plugins"
        if os.path.exists(premium_folder):
            plugins["Premium Plugins"] = []
            for f in os.listdir(premium_folder):
                if f.endswith(".zip"):
                    plugins["Premium Plugins"].append({
                        "name": f.replace(".zip", ""),
                        "url": f"/config/premium-plugins/{f}",
                        "compatibility": "N/A"
                    })

        # Schrijf naar available-plugins.json
        with open(os.path.join(app.config["UPLOAD_FOLDER"], "available-plugins.json"), "w", encoding="utf-8") as pf:
            json.dump(plugins, pf, indent=2)

        return jsonify({"status": "OK"})
    except Exception as e:
        print("Fout bij upload_excel:", e)
        traceback.print_exc()
        return jsonify({"status": "ERROR"}), 500

@app.route("/upload-config", methods=["POST"])
def upload_config():
    """
    Verwerkt het geüploade Excel-bestand + genereert config.json en pluginlijst.
    Wordt normaliter aangeroepen bij de 'Installatie'-knop.
    """
    try:
        excel_file = request.files.get("config_file")
        hosting_type = request.form.get("hosting_type")

        form_data = {
            "site_title": request.form.get("site_title", "Default Site"),
            "admin_user": request.form.get("admin_user", "admin"),
            "admin_password": request.form.get("admin_password", "admin"),
            "admin_email": request.form.get("admin_email", "admin@example.com"),
        }

        if excel_file:
            # Sla geüploade Excel op
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], excel_file.filename)
            excel_file.save(file_path)
            # Genereer config.json (site_title, plugins, enz)
            process_excel(file_path, CONFIG_JSON_PATH, form_data)
            # (Her)genereer pluginlijst => available-plugins.json
            generate_plugin_list()
        else:
            print("⚠️ Geen nieuw Excel-bestand ontvangen, alleen form-data.")

        # Indien Docker
        if hosting_type == "docker":
            print("Docker geselecteerd, genereer docker-compose.yml...")
            generate_docker_compose(CONFIG_JSON_PATH, "docker/docker-compose.yml")

        return jsonify({"status": "✅ Installatieconfig geüpload!"})
    except Exception as e:
        print(f"⚠️ Fout: {e}")
        traceback.print_exc()
        return jsonify({"status": "⚠️ Mislukt"}), 500

# Optionele route om handmatig /config/available-plugins.xlsx in te lezen
@app.route("/config/load-plugins", methods=["POST"])
def load_plugins_manually():
    try:
        generate_plugin_list()
        return jsonify({"status": "✅ Plugins opnieuw geladen!"})
    except Exception as e:
        print(f"Fout bij load_plugins_manually: {e}")
        return jsonify({"status": "⚠️ Error"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
