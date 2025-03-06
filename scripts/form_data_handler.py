import pandas as pd
import json
import os

def process_excel(input_file, output_file, form_data=None):
    """
    Reads the Excel file and generates config.json with selected plugins.
    """
    try:
        df = pd.read_excel(input_file)

        # Extract plugin list from Excel
        plugin_list = df["Plugin URL"].dropna().tolist()

        # Check for premium plugins stored locally
        premium_plugin_dir = "config/premium-plugins"
        premium_plugins = [
            f"/{premium_plugin_dir}/{file}"
            for file in os.listdir(premium_plugin_dir) if file.endswith(".zip")
        ]

        # Create config data
        config_data = {
            "external_plugins": plugin_list,
            "premium_plugins": premium_plugins
        }

        # Save to config.json
        with open(output_file, 'w') as file:
            json.dump(config_data, file, indent=4)

        print(f"✅ Config.json created successfully: {output_file}")

    except Exception as e:
        print(f"⚠️ Error processing Excel file: {e}")
