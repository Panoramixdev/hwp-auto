# app.py: Backend voor het verwerken van het installatieformulier, uitlezen van Excel-data 
# en dynamisch genereren van docker-compose.yml

from flask import Flask, request, jsonify, render_template, redirect, url_for
import pandas as pd
import json
import os
import traceback

# Importeer externe modules voor dataverwerking en Docker Compose generatie
from form_data_handler import process_excel
from generate_docker_compose import generate_docker_compose

app = Flask(__name__)

# Map voor het opslaan van geüploade bestanden en gegenereerde configuraties
UPLOAD_FOLDER = 'config'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Laadt de indexpagina van het installatieformulier
@app.route('/')
def index():
    return render_template('index.html')

# Verwerkt het geüploade Excel-bestand en slaat de configuratie op
@app.route('/upload-config', methods=['POST'])
def upload_config():
    file = request.files['config_file']
    
    if not file:
        return "⚠️ Geen bestand geüpload.", 400
    
    # Sla het Excel-bestand op in de config map
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)
    
    # Verwerk het Excel-bestand en genereer config.json en docker-compose.yml
    try:
        # Stap 1: Verwerk Excel-data naar config.json
        process_excel(file_path, 'config/config.json')
        
        # Stap 2: Genereer dynamisch het docker-compose.yml bestand
        generate_docker_compose('config/config.json', 'docker/docker-compose.yml')
        
        print("✅ Configuratie en Docker Compose succesvol aangemaakt!")
        return redirect(url_for('index'))
    
    except Exception as e:
        print(f"⚠️ Fout bij het verwerken van het Excel-bestand: {e}")
        traceback.print_exc()
        return jsonify({"status": "⚠️ Fout bij het verwerken van het Excel-bestand."}), 500

# API endpoint voor het ophalen van config.json voor de frontend
@app.route('/config/config.json', methods=['GET'])
def get_config():
    try:
        config_path = 'config/config.json'
        if not os.path.exists(config_path):
            return jsonify({"status": "⚠️ config.json niet gevonden."}), 404
        
        with open(config_path, 'r') as config_file:
            config_data = json.load(config_file)
            return jsonify(config_data)
    
    except Exception as e:
        print(f"⚠️ Fout bij het ophalen van config.json: {e}")
        traceback.print_exc()
        return jsonify({"status": "⚠️ Fout bij het ophalen van config.json."}), 500

# API endpoint voor de huidige WordPress versie
@app.route('/config/wp-version', methods=['GET'])
def get_wp_version():
    try:
        # Haal de WordPress versie op via WP-CLI
        wp_version = os.popen("docker exec wordpress wp core version --allow-root").read().strip()
        return jsonify({"version": wp_version})
    except Exception as e:
        print(f"⚠️ Fout bij het ophalen van de WordPress versie: {e}")
        return jsonify({"status": "⚠️ Fout bij het ophalen van de WordPress versie."}), 500

# API endpoint voor beschikbare plugins uit Excel-bestand
@app.route('/config/available-plugins.json', methods=['GET'])
def get_available_plugins():
    try:
        file_path = 'config/available-plugins.xlsx'
        df = pd.read_excel(file_path)

        plugins = {}
        for _, row in df.iterrows():
            category = row['Categorie']
            plugin = {
                "name": row['Plugin Naam'],
                "url": row['Plugin URL'],
                "compatibility": row['Compatibele WP Versie']
            }
            if category not in plugins:
                plugins[category] = []
            plugins[category].append(plugin)

        return jsonify(plugins)

    except Exception as e:
        print(f"⚠️ Fout bij het ophalen van beschikbare plugins: {e}")
        traceback.print_exc()
        return jsonify({"status": "⚠️ Fout bij het ophalen van beschikbare plugins."}), 500

# API endpoint om de status van de Docker Compose generatie te controleren
@app.route('/status', methods=['GET'])
def get_status():
    try:
        compose_path = 'docker/docker-compose.yml'
        if os.path.exists(compose_path):
            return jsonify({"status": "✅ docker-compose.yml succesvol aangemaakt!"})
        else:
            return jsonify({"status": "⚠️ docker-compose.yml niet g
