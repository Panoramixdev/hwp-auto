#!/bin/bash

# manage_plugins.sh: Installeert en beheert WordPress plugins automatisch

echo "🚀 Start met het beheren van plugins..."

# Pad naar de dynamisch gegenereerde configuratie
CONFIG_FILE="/var/www/html/config.json"

# Haal plugin gegevens op uit config.json
EXTERNAL_PLUGINS=$(jq -r '.external_plugins[]' $CONFIG_FILE)

# Loop door alle plugins en installeer of update ze
for plugin_url in $EXTERNAL_PLUGINS; do
    if wp plugin is-installed $plugin_url --allow-root; then
        echo "🔄 Plugin bijwerken: $plugin_url"
        wp plugin update $plugin_url --allow-root
    else
        echo "🚀 Plugin installeren: $plugin_url"
        wp plugin install $plugin_url --activate --allow-root
    fi
done

echo "✅ Pluginbeheer voltooid!"
