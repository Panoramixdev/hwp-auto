# generate_docker_compose.py: Genereert het docker-compose.yml bestand dynamisch op basis van config.json

import json
import os

def generate_docker_compose(config_path: str = 'config/config.json', output_file: str = 'docker/docker-compose.yml'):
    """
    Genereert dynamisch het docker-compose.yml bestand op basis van input uit config.json.
    """

    # Laad de configuratiegegevens uit config.json
    with open(config_path, 'r') as file:
        config = json.load(file)

    # WordPress service configuratie
    wordpress_service = f"""
  wordpress:
    image: wordpress:latest
    container_name: wordpress
    volumes:
      - ../config/config.json:/var/www/html/config.json
      - ../scripts/init_wordpress.sh:/var/www/html/init_wordpress.sh
    environment:
      WORDPRESS_DB_HOST: {config.get('db_host', 'db:3306')}
      WORDPRESS_DB_NAME: {config.get('db_name', 'wp_news_site')}
      WORDPRESS_DB_USER: {config.get('db_user', 'root')}
      WORDPRESS_DB_PASSWORD: {config.get('db_password', 'yourpassword')}
    ports:
      - "{config.get('wp_port', '8080')}:80"
    restart: always
    entrypoint: ["sh", "/var/www/html/init_wordpress.sh"]
    """

    # Database service configuratie (MariaDB of PostgreSQL)
    if config.get('database_type', 'MariaDB') == 'PostgreSQL':
        db_service = f"""
  db:
    image: postgres:latest
    container_name: db
    environment:
      POSTGRES_USER: {config.get('db_user', 'postgres')}
      POSTGRES_PASSWORD: {config.get('db_password', 'yourpassword')}
      POSTGRES_DB: {config.get('db_name', 'wp_news_site')}
    ports:
      - "{config.get('db_port', '5432')}:5432"
    volumes:
      - db_data:/var/lib/postgresql/data
    restart: always
        """
    else:
        db_service = f"""
  db:
    image: mariadb:latest
    container_name: db
    environment:
      MYSQL_ROOT_PASSWORD: {config.get('db_password', 'yourpassword')}
      MYSQL_DATABASE: {config.get('db_name', 'wp_news_site')}
    ports:
      - "{config.get('db_port', '3306')}:3306"
    volumes:
      - db_data:/var/lib/mysql
    restart: always
        """

    # Redis service (optioneel)
    redis_service = ""
    if config.get('enable_redis', False):
        redis_service = """
  redis:
    image: redis:alpine
    container_name: redis-cache
    ports:
      - "6379:6379"
    restart: always
        """

    # n8n service (optioneel)
    n8n_service = ""
    if config.get('enable_n8n', False):
        n8n_service = """
  n8n:
    image: n8nio/n8n
    container_name: n8n-automation
    ports:
      - "5678:5678"
    restart: always
        """

    # NGINX service als reverse proxy
    nginx_service = f"""
  nginx:
    image: nginx:latest
    container_name: nginx-server
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ../config/nginx.conf:/etc/nginx/nginx.conf
      - ../web:/usr/share/nginx/html
      - ../config/ssl:/etc/nginx/ssl
    depends_on:
      - wordpress
      - app-server
    restart: always
    """

    # Flask backend service voor formulierverwerking
    app_service = f"""
  app-server:
    build: ../scripts
    container_name: app-server
    ports:
      - "5000:5000"
    volumes:
      - ../config:/app/config
      - ../scripts:/app/scripts
    command: ["python3", "app.py"]
    depends_on:
      - db
      - wordpress
    restart: always
    """

    # Combineer alle services in het Docker Compose bestand
    docker_compose_content = f"""
version: '3.9'

services:
{wordpress_service}
{db_service}
{redis_service}
{n8n_service}
{app_service}
{nginx_service}

volumes:
  db_data:
    """

    # Schrijf het dynamisch gegenereerde docker-compose.yml bestand
    with open(output_file, 'w') as file:
        file.write(docker_compose_content)

    print(f"✅ Dynamisch docker-compose.yml bestand aangemaakt: {output_file}")
