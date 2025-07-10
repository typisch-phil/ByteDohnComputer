# ByteDohm.de - Plesk Deployment Guide

## Notwendige Schritte für Plesk Hosting

### 1. Dateien Upload
Laden Sie alle Projektdateien in das `/httpdocs` Verzeichnis Ihrer Domain hoch:
- Alle Python-Dateien (app.py, backend/, customer/, templates/, static/)
- passenger_wsgi.py (WSGI-Entry-Point für Plesk)
- .htaccess (Apache-Konfiguration)

### 2. Python-Version konfigurieren
1. In Plesk Control Panel → Ihre Domain auswählen
2. "Python" → Python-Version 3.8+ auswählen
3. Startup file: `passenger_wsgi.py`
4. Application root: `/var/www/vhosts/bytedohm.de/httpdocs`

### 3. Python-Packages installieren
Fügen Sie diese Packages in Plesk hinzu (Python → Packages):
```
email-validator==2.2.0
flask==3.1.0
flask-dance==7.0.0
flask-login==0.6.3
flask-sqlalchemy==3.1.1
gunicorn==23.0.0
lxml==5.3.0
oauthlib==3.2.2
pyjwt==2.10.1
pymysql==1.1.1
python-dotenv==1.0.1
requests==2.32.3
sendgrid==6.11.0
sqlalchemy==2.0.36
stripe==11.1.1
werkzeug==3.1.3
zeep==4.3.1
```

### 4. Umgebungsvariablen setzen
In Plesk Control Panel → Ihrer Domain → Python → Environment variables:

```
SESSION_SECRET=IhrSicheresSessionSecret123
MYSQL_DATABASE_URL=mysql+pymysql://u6560-6636_bytedohm:HeikoCindy-8@45.88.108.231:3306/u6560-6636_bytedohm
SMTP_SERVER=mail.bytedohm.de
SMTP_PORT=465
SMTP_USERNAME=no-reply@bytedohm.de
SMTP_PASSWORD=HeikoCindy-8
FROM_EMAIL=no-reply@bytedohm.de
DHL_USERNAME=IhrDHLUsername
DHL_PASSWORD=IhrDHLPassword
DHL_EKP_NUMBER=IhreDHLEKP
STRIPE_SECRET_KEY=IhrStripeSecretKey
```

### 5. MySQL Datenbank
Die Datenbank ist bereits konfiguriert:
- Host: 45.88.108.231
- Datenbank: u6560-6636_bytedohm
- User: u6560-6636_bytedohm
- Password: HeikoCindy-8

### 6. Statische Dateien
Stellen Sie sicher, dass die `static/` Ordner korrekt hochgeladen wurde:
- `/static/css/style.css`
- `/static/js/configurator.js`

### 7. SSL-Zertifikat
Aktivieren Sie Let's Encrypt SSL in Plesk für HTTPS-Unterstützung.

### 8. Testen
Nach dem Deployment:
1. Besuchen Sie https://bytedohm.de
2. Testen Sie den PC-Konfigurator
3. Prüfen Sie das Admin-Panel (/admin)
4. Testen Sie die E-Mail-Funktionen

## Typische Probleme und Lösungen

### Problem: CSS/JS laden nicht
**Lösung:** Überprüfen Sie die Pfade in `templates/base.html` und stellen Sie sicher, dass der `static/` Ordner korrekt hochgeladen wurde.

### Problem: Database connection error
**Lösung:** Überprüfen Sie die MySQL-Verbindungsparameter in den Umgebungsvariablen.

### Problem: 500 Internal Server Error
**Lösung:** Überprüfen Sie die Error-Logs in Plesk und stellen Sie sicher, dass alle Python-Packages installiert sind.

### Problem: E-Mails werden nicht gesendet
**Lösung:** Überprüfen Sie die SMTP-Konfiguration in den Umgebungsvariablen.

## Support
Bei Problemen können Sie die Anwendung lokal testen mit:
```bash
python main.py
```

Die Anwendung läuft dann auf http://localhost:5000