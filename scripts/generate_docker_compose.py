import json
import os

def generate_docker_compose(config_path: str = 'config/config.json', output_file: str = 'docker/docker-compose.yml'):
    """
    Genereert het docker-compose.yml bestand dynamisch voor WordPress (headless setup).
    """

    # Lees configuratie uit config.json
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
    networks:
      - agile_network
    """

    # Database service configuratie (MariaDB)
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
    networks:
      - agile_network
    """

    # NGINX reverse proxy service
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
    networks:
      - agile_network
    """

    # Flask backend (app-server)
    app_service = f"""
  app-server:
    build:
      context: ..
      dockerfile: docker/Dockerfile
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
    networks:
      - agile_network
    """

    # Samengevoegde docker-compose.yml inhoud
    docker_compose_content = f"""
name: WP_Project # Naam van het project     
services:
{wordpress_service}
{db_service}
{app_service}
{nginx_service}

volumes:
  db_data:

networks:
  agile_network:
    external: true
    """

    # Schrijf naar het bestand
    with open(output_file, 'w') as file:
        file.write(docker_compose_content)

    print(f"✅ docker-compose.yml aangemaakt op: {output_file}")
