#!/usr/bin/env python3
"""
MySQL Setup Script für ByteDohm
Hilft beim Einrichten der MySQL-Verbindung
"""

def setup_mysql_connection():
    print("=== ByteDohm MySQL Setup ===")
    print("\nBitte geben Sie Ihre MySQL-Verbindungsdaten ein:")
    
    host = input("MySQL Host (z.B. localhost oder db.example.com): ").strip()
    port = input("MySQL Port (Standard: 3306): ").strip() or "3306"
    username = input("MySQL Benutzername: ").strip()
    password = input("MySQL Passwort: ").strip()
    database = input("Datenbankname (Standard: bytedohm): ").strip() or "bytedohm"
    
    # SSL Option
    ssl_required = input("SSL erforderlich? (y/n, Standard: n): ").strip().lower()
    ssl_params = "?ssl=required" if ssl_required in ['y', 'yes', 'ja'] else ""
    
    # Verbindungsstring erstellen
    connection_string = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}{ssl_params}"
    
    print(f"\n=== Generierte Verbindungszeichenfolge ===")
    print(f"MYSQL_DATABASE_URL={connection_string}")
    
    print(f"\n=== Nächste Schritte ===")
    print("1. Kopieren Sie die obige MYSQL_DATABASE_URL")
    print("2. Setzen Sie sie als Umgebungsvariable:")
    print(f"   export MYSQL_DATABASE_URL='{connection_string}'")
    print("3. Starten Sie die Anwendung neu")
    print("\nOder setzen Sie die Variable direkt in Replit:")
    print("- Gehen Sie zu 'Secrets' in der Sidebar")
    print("- Fügen Sie einen neuen Secret hinzu:")
    print("  Key: MYSQL_DATABASE_URL")
    print(f"  Value: {connection_string}")
    
    return connection_string

if __name__ == "__main__":
    setup_mysql_connection()