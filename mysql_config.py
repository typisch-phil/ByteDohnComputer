#!/usr/bin/env python3
"""
MySQL Configuration Helper für ByteDohm
Konfiguriert automatisch MySQL-Verbindung
"""

import os
import logging

def get_mysql_connection_string():
    """
    Gibt MySQL-Verbindungsstring zurück
    Priorisiert Umgebungsvariablen, dann lokale Konfiguration
    """
    
    # 1. Prüfe MYSQL_DATABASE_URL (höchste Priorität)
    mysql_url = os.environ.get("MYSQL_DATABASE_URL")
    if mysql_url:
        logging.info("Using MYSQL_DATABASE_URL from environment")
        return mysql_url
    
    # 2. Prüfe generische DATABASE_URL für MySQL
    database_url = os.environ.get("DATABASE_URL")
    if database_url and "mysql" in database_url:
        logging.info("Using DATABASE_URL (MySQL detected)")
        return database_url
    
    # 3. Lokale Entwicklungsumgebung
    # Verschiedene MySQL-Konfigurationen testen
    local_configs = [
        "mysql+pymysql://root@localhost:3306/bytedohm",
        "mysql+pymysql://root:@localhost:3306/bytedohm", 
        "mysql+pymysql://mysql@localhost:3306/bytedohm",
        "mysql+pymysql://bytedohm:bytedohm@localhost:3306/bytedohm"
    ]
    
    for config in local_configs:
        logging.info(f"Trying local MySQL config: {config}")
        # Hier könnten wir eine Testverbindung machen
        
    # Standard-Rückgabe für lokale Entwicklung
    return "mysql+pymysql://root@localhost:3306/bytedohm"

def setup_mysql_env():
    """
    Setzt MySQL-Umgebungsvariablen für die Anwendung
    """
    mysql_url = get_mysql_connection_string()
    os.environ["SQLALCHEMY_DATABASE_URI"] = mysql_url
    
    logging.info(f"MySQL configured: {mysql_url}")
    return mysql_url

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    connection_string = setup_mysql_env()
    print(f"MySQL Connection String: {connection_string}")