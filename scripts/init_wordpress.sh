#!/bin/bash

# init_wordpress.sh: Automatische installatie en configuratie van WordPress
echo "🚀 Start WordPress installatie..."

# Pad naar de dynamisch gegenereerde configuratie
CONFIG_FILE="/var/www/html/config.json"

# Haal configuratiegegevens op uit config.json
SITE_TITLE=$(jq -r '.site_title' $CONFIG_FILE)
ADMIN_USER=$(jq -r '.admin_user' $CONFIG_FILE)
ADMIN_PASSWORD=$(jq -r '.admin_password' $CONFIG_FILE)
ADMIN_EMAIL=$(jq -r '.admin_email' $CONFIG_FILE)
EXTERNAL_PLUGINS=$(jq -r '.external_plugins[]' $CONFIG_FILE)
ENABLE_REDIS=$(jq -r '.enable_redis' $CONFIG_FILE)
ENABLE_SEO=$(jq -r '.enable_seo' $CONFIG_FILE)

# Controleer of WordPress al is geïnstalleerd
if ! wp core is-installed --allow-root; then
    # Installeer WordPress met configuratiegegevens uit config.json
    wp core install --url="http://localhost:8080" \
    --title="$SITE_TITLE" \
    --admin_user="$ADMIN_USER" \
    --admin_password="$ADMIN_PASSWORD" \
    --admin_email="$ADMIN_EMAIL" \
    --allow-root

    echo "✅ WordPress installatie voltooid!"
else
    echo "⚠️ WordPress is al geïnstalleerd. Sla installatie over."
fi

# Installeer en activeer externe plugins
echo "🚀 Plugins installeren..."
for plugin_url in $EXTERNAL_PLUGINS; do
    if wp plugin is-installed $plugin_url --allow-root; then
        echo "🔄 Plugin bijwerken: $plugin_url"
        wp plugin update $plugin_url --allow-root
    else
        echo "🚀 Plugin installeren: $plugin_url"
        wp plugin install $plugin_url --activate --allow-root
    fi
done

# Basisconfiguratie van WordPress
echo "🔧 Standaard WordPress configuratie instellen..."
wp rewrite structure '/%postname%/' --hard --allow-root

# Redis caching inschakelen indien ingesteld in config.json
if [ "$ENABLE_REDIS" == "true" ]; then
    echo "🚀 Redis caching inschakelen..."
    wp redis enable --allow-root
fi

# Rank Math SEO herindexeren indien ingesteld
if [ "$ENABLE_SEO" == "true" ]; then
    echo "🚀 Rank Math SEO herindexeren..."
    wp rank-math tools reindex --allow-root
fi

echo "✅ WordPress setup en plugininstallatie voltooid!"
