#!/bin/bash

# manage_plugins.sh: Installeert en beheert WordPress plugins automatisch

echo "🚀 Start met het beheren van plugins..."

# Pad naar de configuratie en premium plugin map
CONFIG_FILE="/var/www/html/config.json"
PREMIUM_PLUGIN_DIR="/var/www/html/config/premium-plugins"

# Controleer of Composer is geïnstalleerd, zo niet, installeer het
if ! command -v composer &> /dev/null; then
    echo "📦 Composer niet gevonden, installeren..."
    apt-get update && apt-get install -y curl unzip php-cli php-zip
    curl -sS https://getcomposer.org/installer | php
    mv composer.phar /usr/local/bin/composer
fi

# Haal plugin gegevens op uit config.json
EXTERNAL_PLUGINS=$(jq -r '.external_plugins[]' $CONFIG_FILE)

# Loop door alle plugins en installeer ze
for plugin_url in $EXTERNAL_PLUGINS; do
    if [[ $plugin_url == "/config/premium-plugins/"* ]]; then
        # Premium plugin installeren vanaf lokale zip
        plugin_name=$(basename "$plugin_url" .zip)
        plugin_path="$PREMIUM_PLUGIN_DIR/$plugin_name.zip"
        
        if wp plugin is-installed $plugin_name --allow-root; then
            echo "🔄 Premium plugin bijwerken: $plugin_name"
            wp plugin update $plugin_name --allow-root
        else
            echo "🚀 Premium plugin installeren: $plugin_name"
            wp plugin install $plugin_path --activate --allow-root
        fi

    elif [[ $plugin_url == "composer require "* ]]; then
        # Plugin installeren via Composer
        echo "📦 Composer plugin installeren: $plugin_url"
        cd /var/www/html/wp-content/plugins/
        eval $plugin_url
        cd -

    else
        # Standaard plugin installeren vanaf WordPress repo
        plugin_slug=$(basename "$plugin_url" .zip)
        if wp plugin is-installed $plugin_slug --allow-root; then
            echo "🔄 Plugin bijwerken: $plugin_slug"
            wp plugin update $plugin_slug --allow-root
        else
            echo "🚀 Gratis plugin installeren: $plugin_slug"
            wp plugin install $plugin_url --activate --allow-root
        fi
    fi
done

echo "✅ Pluginbeheer voltooid!"
