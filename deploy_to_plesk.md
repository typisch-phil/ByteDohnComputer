# Schnelle Plesk Deployment Anleitung

## Problem im Screenshot
Das CSS lädt nicht korrekt. Hier die Lösung:

## 1. Dateien hochladen
Laden Sie ALLE Dateien in `/httpdocs` hoch:
- ✅ passenger_wsgi.py (Wichtig!)
- ✅ .htaccess (Wichtig!)
- ✅ app.py
- ✅ backend/ Ordner (komplett)
- ✅ templates/ Ordner (komplett)
- ✅ static/ Ordner (komplett)
- ✅ customer/ Ordner (komplett)

## 2. Python in Plesk konfigurieren
1. Domain auswählen → Python
2. Python Version: **3.8 oder höher**
3. **Startup file: `passenger_wsgi.py`**
4. Application root: `/var/www/vhosts/bytedohm.de/httpdocs`

## 3. Packages installieren
In Plesk → Python → Packages → Diese hinzufügen:
```
flask
flask-sqlalchemy
flask-login
pymysql
python-dotenv
requests
stripe
sendgrid
werkzeug
sqlalchemy
```

## 4. Umgebungsvariablen (Wichtig!)
Plesk → Python → Environment variables:
```
SESSION_SECRET=ByteDohm2025SecretKey!
SMTP_SERVER=mail.bytedohm.de
SMTP_PORT=465
SMTP_USERNAME=no-reply@bytedohm.de
SMTP_PASSWORD=HeikoCindy-8
FROM_EMAIL=no-reply@bytedohm.de
STRIPE_SECRET_KEY=sk_test_...
```

## 5. Domain neu starten
Nach allen Änderungen:
- Plesk → Domain → Python → **"Restart App"** klicken

## Häufige Probleme:
- **CSS lädt nicht**: `static/` Ordner prüfen
- **500 Fehler**: Error Logs in Plesk prüfen
- **Database Error**: MySQL-Verbindung ist bereits konfiguriert

Die Website sollte dann funktionieren!