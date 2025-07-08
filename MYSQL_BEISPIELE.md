# MySQL Verbindungsbeispiele für ByteDohm

## 🔗 Verbindungsformat
```
mysql+pymysql://username:password@host:port/database?optionen
```

## 📋 Häufige Beispiele

### Lokaler MySQL Server
```
mysql+pymysql://root:password@localhost:3306/bytedohm
```

### MySQL mit SSL
```
mysql+pymysql://user:pass@db.example.com:3306/bytedohm?ssl=required
```

### Cloud-Provider

#### AWS RDS
```
mysql+pymysql://admin:password@database.cluster-xyz.region.rds.amazonaws.com:3306/bytedohm?ssl=required
```

#### PlanetScale
```
mysql+pymysql://username:password@aws.connect.psdb.cloud:3306/database?ssl=required
```

#### DigitalOcean
```
mysql+pymysql://doadmin:password@db-mysql-fra1-12345-do-user-12345-0.b.db.ondigitalocean.com:25060/defaultdb?ssl=required
```

## ⚙️ Setup in Replit

1. **Secrets verwenden**:
   - Sidebar → "Secrets"
   - Key: `MYSQL_DATABASE_URL`
   - Value: Ihre Verbindungszeichenfolge

2. **Anwendung neu starten**:
   - Das System erkennt automatisch die neue Verbindung
   - Tabellen werden automatisch erstellt
   - Demo-Daten werden eingefügt

## 🎯 Nach dem Setup verfügbar

- **Admin Panel**: `/admin/login`
- **Benutzername**: `admin`
- **Passwort**: `admin123`
- **Komponenten-Management**: Vollständige CRUD-Operationen
- **PC-Konfigurator**: Mit Echtzeit-Daten aus MySQL

## ❓ Hilfe benötigt?

Teilen Sie einfach Ihre MySQL-Verbindungsdaten mit, und ich konfiguriere alles automatisch für Sie!