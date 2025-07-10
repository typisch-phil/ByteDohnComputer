# E-Mail-Setup für ByteDohm.de

## Übersicht
Das E-Mail-System ist vollständig implementiert und sendet automatisch:
- ✅ Willkommens-E-Mails bei Registrierung
- ✅ Bestellbestätigungs-E-Mails  
- ✅ Versandbenachrichtigungen mit Tracking-Nummer
- ✅ Status-Update E-Mails
- ✅ Newsletter-E-Mails

## Aktueller Status
**Derzeit werden E-Mails nur in der Konsole geloggt** (für Entwicklung/Testing).

## Produktions-Setup (SMTP-Konfiguration)

### Umgebungsvariablen setzen:
```bash
# SMTP-Server Einstellungen
SMTP_SERVER=smtp.gmail.com          # oder Ihr SMTP-Server
SMTP_PORT=587                       # Standard für TLS
SMTP_USERNAME=ihr-email@domain.de   # Ihr E-Mail-Account
SMTP_PASSWORD=ihr-app-passwort      # App-Passwort (nicht Ihr normales Passwort!)
FROM_EMAIL=ByteDohm.de <noreply@bytedohm.de>  # Absender-Name und E-Mail
```

### Empfohlene E-Mail-Anbieter:

#### 1. **Google Gmail** (einfachste Option)
- SMTP-Server: `smtp.gmail.com`
- Port: `587`
- Benötigt: **App-Passwort** (nicht Ihr normales Gmail-Passwort)
- Setup: Google Account → Sicherheit → 2-Faktor-Auth aktivieren → App-Passwörter erstellen

#### 2. **Microsoft Outlook/Hotmail**
- SMTP-Server: `smtp-mail.outlook.com`
- Port: `587`
- Authentifizierung: Normale Anmeldedaten

#### 3. **Professionelle E-Mail-Services**
- **SendGrid** (empfohlen für Geschäfte)
- **Mailgun**
- **Amazon SES**
- **PostMark**

### Gmail App-Passwort erstellen:
1. Gmail-Account öffnen
2. Google Account-Einstellungen → Sicherheit
3. 2-Faktor-Authentifizierung aktivieren
4. App-Passwörter → "ByteDohm" auswählen
5. Generiertes 16-stelliges Passwort als `SMTP_PASSWORD` verwenden

### Beispiel-Konfiguration (Gmail):
```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=ihre-email@gmail.com
SMTP_PASSWORD=abcd efgh ijkl mnop    # 16-stelliges App-Passwort
FROM_EMAIL=ByteDohm.de <noreply@gmail.com>
```

## Testen der E-Mail-Funktion

### Manueller Test im Admin-Panel:
```python
from email_service import EmailService
service = EmailService()
# Test-E-Mail senden
service.send_registration_email(customer_objekt)
```

### E-Mail-Logs überprüfen:
```bash
# In der Replit-Konsole nach E-Mail-Logs suchen
grep "E-Mail" logs/
```

## Wichtige Hinweise

### Sicherheit:
- **Niemals** normale Passwörter verwenden
- Immer App-Passwörter oder API-Keys verwenden
- E-Mail-Credentials als **Replit Secrets** speichern (nicht in Code)

### Replit Secrets hinzufügen:
1. Replit-Projekt öffnen
2. Secrets-Tab (Schloss-Symbol)
3. Folgende Secrets hinzufügen:
   - `SMTP_SERVER`
   - `SMTP_PORT`
   - `SMTP_USERNAME`  
   - `SMTP_PASSWORD`
   - `FROM_EMAIL`

### Troubleshooting:
- **"Authentication failed"**: App-Passwort verwenden, nicht normales Passwort
- **"Connection refused"**: Port und Server prüfen
- **"Less secure apps"**: Bei Gmail App-Passwort verwenden statt "less secure apps"

## Aktueller E-Mail-Flow

### Bei Kundenregistrierung:
```
Kunde registriert sich → Willkommens-E-Mail wird gesendet
```

### Bei Bestellung:
```
Checkout abgeschlossen → Bestellbestätigungs-E-Mail
Status "shipped" → Versandbenachrichtigung mit DHL-Tracking
```

### Bei Status-Änderung:
```
Admin ändert Bestellstatus → Automatische Status-Update E-Mail
```

## Bereit für Produktionsstart:
Sobald Sie die SMTP-Einstellungen konfiguriert haben, funktioniert das E-Mail-System vollautomatisch!