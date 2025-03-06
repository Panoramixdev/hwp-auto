import json
import os

def configure_local_wp(config_path):
    """ Sets up WordPress locally (without Docker). """
    with open(config_path, 'r') as file:
        config = json.load(file)

    wp_url = config.get("wp_url", "http://localhost/wordpress")
    db_host = config.get("db_host", "localhost")
    db_name = config.get("db_name", "wp_auto")
    db_user = config.get("db_user", "root")
    db_password = config.get("db_password", "")

    print(f"🔧 Configuring Local WordPress: {wp_url}")
    os.system(f'wp core install --url={wp_url} --title="Local WP Site" '
              f'--admin_user=admin --admin_password=admin --admin_email=admin@example.com --allow-root')
    os.system(f'wp config create --dbname={db_name} --dbuser={db_user} --dbpass={db_password} --dbhost={db_host} --allow-root')

def configure_external_wp(config_path):
    """ Connects to an externally hosted WordPress site (e.g., Hostinger). """
    with open(config_path, 'r') as file:
        config = json.load(file)

    wp_url = config.get("wp_url", "https://example.com")
    api_key = config.get("hostinger_api_key", "")

    print(f"🌐 Connecting to external WordPress at {wp_url}")
    if not api_key:
        print("⚠️ Hostinger API key missing! Please add it to config.json.")
        return

    # Example: API call to set up plugins remotely
    print(f"🔧 Sending API request to configure plugins on {wp_url}")
