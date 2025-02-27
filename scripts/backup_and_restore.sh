#!/bin/bash

# backup_and_restore.sh: Automatisch back-up en herstel van WordPress en MariaDB database

# Directories voor back-upbestanden
BACKUP_DIR="/var/www/html/backups"
DATE=$(date +'%Y-%m-%d_%H-%M-%S')

# Maak de back-up directory aan als deze nog niet bestaat
mkdir -p $BACKUP_DIR

# Functie voor het maken van een back-up
backup() {
    echo "🚀 Start met het maken van een back-up..."

    # WordPress bestanden back-uppen
    echo "📦 Back-up van WordPress bestanden..."
    tar -czf $BACKUP_DIR/wp-content_$DATE.tar.gz /var/www/html/wp-content

    # Database back-uppen via WP-CLI
    echo "💾 Back-up van database..."
    wp db export $BACKUP_DIR/db_backup_$DATE.sql --allow-root

    echo "✅ Back-up voltooid! Bestanden opgeslagen in $BACKUP_DIR"
}

# Functie voor het herstellen van een back-up
restore() {
    echo "🚨 Start met herstellen van back-up..."

    if [ -z "$1" ]; then
        echo "⚠️ Geen back-upbestand opgegeven voor herstel!"
        echo "Gebruik: sh backup_and_restore.sh restore <bestandsnaam>"
        exit 1
    fi

    BACKUP_FILE="$BACKUP_DIR/$1"

    if [[ $1 == *.sql ]]; then
        echo "💾 Database herstellen..."
        wp db import $BACKUP_FILE --allow-root
    elif [[ $1 == *.tar.gz ]]; then
        echo "📦 WordPress bestanden herstellen..."
        tar -xzf $BACKUP_FILE -C /var/www/html/wp-content
    else
        echo "❌ Ongeldig back-upbestand. Gebruik een .sql of .tar.gz bestand."
        exit 1
    fi

    echo "✅ Herstel voltooid!"
}

# Controleer welk argument is meegegeven (backup of restore)
case "$1" in
    backup)
        backup
        ;;
    restore)
        restore "$2"
        ;;
    *)
        echo "⚠️ Onbekend commando. Gebruik 'backup' of 'restore'."
        echo "Voorbeelden:"
        echo "  sh backup_and_restore.sh backup"
        echo "  sh backup_and_restore.sh restore db_backup_2023-07-01_10-30-00.sql"
        exit 1
        ;;
esac
