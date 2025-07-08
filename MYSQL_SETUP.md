# MySQL Setup für ByteDohm

## Voraussetzungen

Die Anwendung ist vollständig für MySQL konfiguriert. Alle anderen Datenbankquellen wurden entfernt.

## MySQL-Verbindung einrichten

### Option 1: Lokaler MySQL Server
1. MySQL Server installieren und starten
2. Datenbank erstellen:
   ```sql
   CREATE DATABASE bytedohm;
   ```
3. Umgebungsvariable setzen:
   ```bash
   export MYSQL_DATABASE_URL="mysql+pymysql://username:password@localhost:3306/bytedohm"
   ```

### Option 2: Externes MySQL (empfohlen)
Setzen Sie die Umgebungsvariable mit Ihrer MySQL-Verbindung:
```bash
export MYSQL_DATABASE_URL="mysql+pymysql://user:password@host:port/database"
```

## Standard-Konfiguration

- **Standardverbindung**: `mysql+pymysql://root:password@localhost:3306/bytedohm`
- **Admin-Anmeldung**: admin / admin123
- **Tabellen**: Werden automatisch erstellt
- **Demo-Daten**: Automatisch eingefügt beim ersten Start

## Funktionen

✅ Nur MySQL als Datenquelle
✅ Alle JSON-Fallbacks entfernt
✅ Admin Panel für Komponenten-Management
✅ Vollständige CRUD-Operationen für PC-Komponenten
✅ Fertig-PC Management
✅ Kompatibilitätsprüfung

## Nächste Schritte

1. MySQL-Datenbank bereitstellen
2. MYSQL_DATABASE_URL setzen
3. Anwendung neu starten
4. Admin Panel unter `/admin/login` aufrufen