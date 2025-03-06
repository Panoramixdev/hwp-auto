import pandas as pd
import json

def generate_excel_report(config_path, output_path):
    """ Generates an Excel report summarizing the WordPress installation. """
    with open(config_path, 'r') as file:
        config = json.load(file)

    data = {
        "Instelling": [
            "Website Titel",
            "Admin Gebruiker",
            "Admin Wachtwoord",
            "Admin E-mail",
            "Geïnstalleerde Plugins",
            "Premium Plugins"
        ],
        "Waarde": [
            config["site_title"],
            config["admin_user"],
            config["admin_password"],
            config["admin_email"],
            ", ".join(config["external_plugins"]),
            ", ".join(config["premium_plugins"])
        ]
    }

    df = pd.DataFrame(data)
    df.to_excel(output_path, index=False)
    print(f"✅ Installation report saved: {output_path}")

# Example usage:
# generate_excel_report("config/config.json", "config/installation_report.xlsx")
