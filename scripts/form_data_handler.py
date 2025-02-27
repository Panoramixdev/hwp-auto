# form_data_handler.py: Leest het Excel-bestand uit en genereert config.json

import pandas as pd
import json
import os

def process_excel(file_path: str, output_file: str = 'config/config.json'):
    """
    Verwerkt het Excel-bestand en genereert config.json voor de WordPress installatie.

    Parameters:
    - file_path (str): Pad naar het geüploade Excel-bestand.
    - output_file (str): Pad naar het te genereren JSON-configuratiebestand.
    """

    # Controleer of het bestand bestaat
    if not os.path.exists(file_path):
        print(f"⚠️ Bestand niet gevonden: {file_path}")
        return

    # Lees de Excel sheet in een DataFrame
    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        print(f"⚠️ Fout bij het lezen van het Excel-bestand: {e}")
        return

    # Zet Excel-gegevens om naar een JSON-configuratie
    try:
        config_data = {
            "site_title": df.loc[df['Instelling'] == 'Website Titel', 'Waarde'].values[0],
            "admin_user": df.loc[df['Instelling'] == 'Admin Gebruiker', 'Waarde'].values[0],
            "admin_password": df.loc[df['Instelling'] == 'Admin Wachtwoord', 'Waarde'].values[0],
            "admin_email": df.loc[df['Instelling'] == 'Admin E-mail', 'Waarde'].values[0],
            "external_plugins": df.loc[df['Instelling'] == 'Externe Plugins', 'Waarde'].values[0].split(','),
            "enable_redis": df.loc[df['Instelling'] == 'Redis Caching', 'Waarde'].values[0].lower() == 'true',
            "enable_seo": df.loc[df['Instelling'] == 'Rank Math SEO', 'Waarde'].values[0].lower() == 'true'
        }
        
        # Schrijf de configuratie naar config.json
        with open(output_file, 'w') as config_file:
            json.dump(config_data, config_file, indent=4)
        
        print(f"✅ Configuratie succesvol opgeslagen in {output_file}")

    except Exception as e:
        print(f"⚠️ Fout bij het verwerken van de Excel-data: {e}")
