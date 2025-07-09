# DHL API-Freischaltung für ByteDohm

## Übersicht
Für die automatische Erstellung echter DHL Versandmarken benötigen Sie eine API-Freischaltung bei DHL. Das System ist bereits vollständig implementiert und wartet nur auf die Freischaltung.

## Schritt 1: DHL Geschäftskunden Service kontaktieren

**Telefon:** 0228 4333112 (Mo-Fr 8-18 Uhr)
**E-Mail:** geschaeftskunden.info@dhl.com
**Online:** https://www.dhl.de/de/geschaeftskunden/kontakt.html

## Schritt 2: DHL API-Zugang beantragen

### Ihre aktuellen Daten für den Antrag:
- **EKP-Nummer:** [Ihre 10-stellige EKP aus den Secrets]
- **DHL Username:** [Aus den Replit Secrets]
- **DHL Passwort:** [Aus den Replit Secrets]
- **Firmenname:** ByteDohm GmbH
- **Verwendungszweck:** Automatische Versandetikett-Erstellung

### Bei DHL zu beantragen:
1. **DHL Paket DE API v2** - Freischaltung für Versandmarken
2. **OAuth 2.0 Authentication** - Für sichere API-Verbindung
3. **Produktions-API-Zugang** - Für Live-Betrieb

## Schritt 3: Technische Angaben

Teilen Sie DHL mit:
- **API-Endpunkt:** https://api-eu.dhl.com/post-de/shipping/v2/orders
- **Authentifizierung:** OAuth 2.0 mit Username/Passwort
- **Verwendung:** Automatische Versandetikett-Erstellung
- **Abrechnungsmodell:** Über bestehende EKP-Abrechnung

## Schritt 4: Nach der Freischaltung

Sobald DHL Ihren API-Zugang freigeschaltet hat:

1. **Testen Sie die Verbindung:**
   - Gehen Sie zu einer Bestellung im Admin-Panel
   - Klicken Sie auf "DHL Etikett erstellen"
   - Das System wird automatisch echte Versandmarken erstellen

2. **Überprüfen Sie die Abrechnung:**
   - Versandmarken werden über Ihr DHL Geschäftskonto abgerechnet
   - Keine zusätzlichen API-Kosten

## Schritt 5: Troubleshooting

**Häufige Probleme:**
- **401 Unauthorized:** API-Zugang noch nicht freigeschaltet
- **403 Forbidden:** Falsche Berechtigung für API-Endpunkt
- **404 Not Found:** Falsche API-URL oder Endpunkt

**Lösungen:**
- Kontaktieren Sie DHL erneut mit Ihrer EKP-Nummer
- Fragen Sie spezifisch nach "DHL Paket DE API v2 Freischaltung"
- Bestätigen Sie, dass OAuth 2.0 für Ihr Konto aktiviert ist

## Aktueller Status

✅ **Implementiert:**
- DHL API-Integration mit OAuth 2.0
- Automatische Versandetikett-Erstellung
- Fallback-System mit detaillierten Anweisungen
- Tracking-Integration

❌ **Fehlt:**
- API-Freischaltung durch DHL (Ihr Schritt)

## Kosten

- **API-Nutzung:** Kostenlos
- **Versandmarken:** Normale DHL Geschäftskunden-Tarife
- **Abrechnung:** Über bestehende EKP-Abrechnung

## Dauer

- **Beantragung:** 1-2 Arbeitstage
- **Freischaltung:** 3-5 Arbeitstage
- **Testphase:** 1-2 Arbeitstage

**Gesamt:** 5-10 Arbeitstage bis zur vollständigen Aktivierung