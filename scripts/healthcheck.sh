#!/bin/bash

# healthcheck.sh: Voert healthchecks uit voor de Docker containers van hwp-auto

# Container namen
WORDPRESS_CONTAINER="wordpress"
DB_CONTAINER="db"
REDIS_CONTAINER="redis-cache"

# Controleer of WordPress bereikbaar is via de API
check_wordpress() {
    echo "🔍 Controleer WordPress API status..."
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/wp-json)

    if [ "$STATUS" == "200" ]; then
        echo "✅ WordPress API is bereikbaar!"
    else
        echo "❌ WordPress API geeft een foutmelding: HTTP $STATUS"
    fi
}

# Controleer of de databasecontainer actief is
check_database() {
    echo "🔍 Controleer database container..."
    if docker exec $DB_CONTAINER mysqladmin ping -u root -pyourpassword --silent; then
        echo "✅ Database (MariaDB) is actief en bereikbaar!"
    else
        echo "❌ Database (MariaDB) is niet bereikbaar!"
    fi
}

# Controleer of Redis caching actief is
check_redis() {
    echo "🔍 Controleer Redis container..."
    if docker exec $REDIS_CONTAINER redis-cli ping | grep -q "PONG"; then
        echo "✅ Redis caching werkt correct!"
    else
        echo "❌ Redis caching is niet actief!"
    fi
}

# Voer alle healthchecks uit
echo "🚦 Start healthchecks voor hwp-auto..."
check_wordpress
check_database
check_redis

echo "🏁 Healthchecks voltooid!"
