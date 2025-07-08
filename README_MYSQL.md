# MySQL Konfiguration für ByteDohm

## ✅ Aktueller Status
Die Anwendung ist **vollständig auf MySQL umgestellt**:
- ❌ PostgreSQL entfernt
- ❌ SQLite entfernt  
- ❌ JSON-Fallbacks entfernt
- ✅ Nur MySQL als Datenquelle

## 🔧 MySQL-Verbindung einrichten

### Option 1: Replit Secrets (Empfohlen)
1. Gehen Sie zu "Secrets" in der Replit-Sidebar
2. Fügen Sie einen neuen Secret hinzu:
   - **Key**: `MYSQL_DATABASE_URL` 
   - **Value**: `mysql+pymysql://username:password@host:port/database`

### Option 2: Umgebungsvariable
```bash
export MYSQL_DATABASE_URL="mysql+pymysql://username:password@host:port/database"
```

### Option 2: Lokale MySQL-Installation
```bash
# MySQL installieren und starten
sudo apt-get install mysql-server
sudo service mysql start

# Datenbank erstellen
mysql -u root -p
CREATE DATABASE bytedohm;
CREATE USER 'bytedohm'@'localhost' IDENTIFIED BY 'bytedohm123';
GRANT ALL PRIVILEGES ON bytedohm.* TO 'bytedohm'@'localhost';
FLUSH PRIVILEGES;

# Umgebungsvariable setzen
export MYSQL_DATABASE_URL="mysql+pymysql://bytedohm:bytedohm123@localhost:3306/bytedohm"
```

### Option 3: Cloud MySQL (PlanetScale, AWS RDS, etc.)
Erstellen Sie eine Cloud-MySQL-Instanz und verwenden Sie die Verbindungszeichenfolge:
```bash
export MYSQL_DATABASE_URL="mysql+pymysql://user:pass@host.com:3306/dbname?ssl=required"
```

## 🚀 Nach MySQL-Setup
1. Umgebungsvariable setzen
2. Anwendung neu starten
3. Tabellen werden automatisch erstellt
4. Demo-Daten werden eingefügt
5. Admin Panel verfügbar unter `/admin/login`

## 📊 Admin-Zugang
- **URL**: `/admin/login`
- **Benutzername**: `admin`
- **Passwort**: `admin123`

## 🛠️ Funktionen mit MySQL
- ✅ Komponenten-Management
- ✅ Fertig-PC-Verwaltung
- ✅ Kompatibilitätsprüfung
- ✅ Konfigurator mit Echtzeit-Daten
- ✅ CRUD-Operationen für alle Daten

## 🔍 Troubleshooting
Die Anwendung läuft auch ohne MySQL-Verbindung, aber ohne Datenbankfunktionen. Prüfen Sie die Logs für Verbindungsfehler und stellen Sie sicher, dass MySQL erreichbar ist.