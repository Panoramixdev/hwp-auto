#!/bin/bash

# data_migration.sh: Migratie van WordPress en database van Hostinger naar Docker setup

# Directories voor back-ups en migratiebestanden
EXPORT_DIR="/var/www/html/migration"
DATE=$(date +'%Y-%m-%d_%H-%M-%S')

# Maak de export directory aan als deze nog niet bestaat
mkdir -p $EXPORT_DIR

# WordPress en database configuratie
WP_URL="http://localhost:8080"
DB_CONTAINER="db"
DB_USER="root"
DB_PASSWORD="yourpassword"
DB_NAME="wp_news_site"

# Functie voor het exporteren van data vanaf Hostinger
export_data() {
    echo "🚀 Start met exporteren van data vanaf Hostinger..."

    # Exporteer WordPress bestanden
    echo "📦 Exporteren van wp-content map..."
    tar -czf $EXPORT_DIR/wp-content_$DATE.tar.gz /path/to/hostinger/wp-content

    # Exporteer database
    echo "💾 Exporteer database..."
    mysqldump -u $DB_USER -p$DB_PASSWORD $DB_NAME > $EXPORT_DIR/db_backup_$DATE.sql

    echo "✅ Export voltooid! Bestanden opgeslagen in $EXPORT_DIR"
}

# Functie voor het importeren van data naar Docker setup
import_data() {
    echo "🚨 Start met importeren van data naar Docker setup..."

    if [ -z "$1" ] || [ -z "$2" ]; then
        echo "⚠️ Onvoldoende argumenten opgegeven voor import!"
        echo "Gebruik: sh data_migration.sh import <db_backup.sql> <wp-content.tar.gz>"
        exit 1
    fi

    DB_BACKUP="$EXPORT_DIR/$1"
    WP_BACKUP="$EXPORT_DIR/$2"

    # Importeer database in Docker container
    echo "💾 Database importeren naar Docker..."
    docker cp $DB_BACKUP $DB_CONTAINER:/db_backup.sql
    docker exec -i $DB_CONTAINER mysql -u $DB_USER -p$DB_PASSWORD $DB_NAME < /db_backup.sql

    # Herstel WordPress bestanden in de container
    echo "📦 WordPress bestanden herstellen..."
    tar -xzf $WP_BACKUP -C /var/www/html/wp-content

    echo "✅ Data import voltooid! Controleer de website op $WP_URL"
}

# Controleer welk argument is meegegeven (export of import)
case "$1" in
    export)
        export_data
        ;;
    import)
        import_data "$2" "$3"
        ;;
    *)
        echo "⚠️ Onbekend commando. Gebruik 'export' of 'import'."
        echo "Voorbeelden:"
        echo "  sh data_migration.sh export"
        echo "  sh data_migration.sh import db_backup_2023-07-01.sql wp-content_2023-07-01.tar.gz"
        exit 1
        ;;
esac
