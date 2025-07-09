# ByteDohm PC Configurator

## Overview

ByteDohm is a web-based PC configurator application that allows users to build custom computers by selecting compatible components. The application provides an intuitive interface for component selection with automatic compatibility checking, pricing calculations, and the ability to save configurations. It also features pre-built PC options for users who prefer ready-made solutions.

## System Architecture

The application follows a traditional web architecture pattern with:

- **Frontend**: HTML templates with Bootstrap for responsive design, vanilla JavaScript for interactive features
- **Backend**: Flask web framework with Python
- **Database**: SQLAlchemy ORM with MySQL-only support (alle anderen Datenbanken entfernt)
- **Data Storage**: Alle Daten werden ausschließlich in MySQL gespeichert, JSON-Fallbacks wurden entfernt
- **Payment Processing**: Vollständige Stripe-Integration mit automatischer Kunden- und Bestellerstellung
- **Static Assets**: CSS and JavaScript files served directly by Flask

## Key Components

### Backend Components

1. **Flask Application (`app.py`)**
   - Main application entry point
   - Database configuration and initialization
   - Session management with configurable secret key
   - Development and production environment support

2. **Database Models (`models.py`)**
   - `Configuration`: Stores user-created PC configurations with name, components (JSON), total price, and timestamp
   - `Component`: Stores individual hardware components with category, specifications (JSON), and pricing
   - Uses SQLAlchemy ORM with declarative base pattern

3. **Routes (`routes.py`)**
   - `/`: Homepage with hero section and service overview
   - `/konfigurator`: Interactive PC configurator interface
   - `/fertig-pcs`: Pre-built PC showcase page
   - Component data loading from JSON files

4. **Data Layer (`data/components.json`)**
   - Static component database with detailed specifications
   - Categories: CPUs, motherboards, RAM, GPUs, SSDs, cases, PSUs, coolers
   - Each component includes compatibility information (sockets, supported RAM types, etc.)

### Frontend Components

1. **Template System**
   - `base.html`: Common layout with navigation, Bootstrap integration, and meta tags
   - `index.html`: Landing page with hero section and feature highlights
   - `configurator.html`: Step-by-step PC building interface
   - `prebuild.html`: Pre-built PC catalog with filtering options

2. **JavaScript (`static/js/configurator.js`)**
   - `PCConfigurator` class managing component selection state
   - Step navigation and validation
   - Compatibility checking logic
   - Price calculation and summary updates

3. **Styling (`static/css/style.css`)**
   - Modern tech-focused design with CSS custom properties
   - Responsive layout with Bootstrap integration
   - Tech-themed color scheme (blues, grays, orange accents)

## Data Flow

1. **Component Loading**: JSON data is loaded server-side and passed to templates
2. **User Selection**: Frontend JavaScript manages component selection state
3. **Compatibility Validation**: Client-side checking of component compatibility (socket types, power requirements, etc.)
4. **Configuration Saving**: Selected components are serialized and stored in database
5. **Price Calculation**: Real-time price updates based on selected components

## External Dependencies

### Backend Dependencies
- **Flask**: Web framework for routing and templating
- **SQLAlchemy**: ORM for database operations
- **Flask-SQLAlchemy**: Flask integration for SQLAlchemy

### Frontend Dependencies
- **Bootstrap 5.3.0**: CSS framework for responsive design
- **Font Awesome 6.4.0**: Icon library for UI elements
- **Vanilla JavaScript**: No additional JavaScript frameworks

### Development Dependencies
- **Python 3.x**: Runtime environment
- **MySQL**: Einzige unterstützte Datenbank, konfiguriert über MYSQL_DATABASE_URL
- **PyMySQL**: MySQL-Connector für Python

## Deployment Strategy

The application is designed for flexible deployment:

1. **Development**: MySQL database with debug mode enabled
2. **Production**: Environment variable configuration for:
   - `MYSQL_DATABASE_URL`: MySQL database connection string (Required)
   - `SESSION_SECRET`: Secure session key
   - Host and port configuration via Flask's built-in server or WSGI

3. **Database Migration**: SQLAlchemy handles table creation automatically on startup
4. **Static Files**: Served directly by Flask (consider CDN for production)

## Changelog

- July 08, 2025: Initial setup
- July 08, 2025: Vollständige Migration zu MySQL - alle PostgreSQL und SQLite Komponenten entfernt, nur MySQL als Datenquelle
- July 08, 2025: MySQL-Konfigurationssystem implementiert, automatische Verbindungserkennung, komplette Dokumentation erstellt
- July 09, 2025: Preisberechnung Bug behoben - Komponenten-Datenübertragung vom Backend zu Frontend implementiert, RAM-Kategorie-Mapping korrigiert
- July 09, 2025: Modernes UI-System implementiert - Toast-Benachrichtigungen, Modal-Dialoge, Eingabefelder mit Validierung für bessere Benutzererfahrung
- July 09, 2025: Import/Export-System verbessert - Komponenten-Validierung beim Import, moderne Dialoge, Fehlerbehandlung mit Toast-Nachrichten
- July 09, 2025: Admin-Dashboard erweitert - Vollständige Bestellverwaltung, Kundendatenbank, Rechnungssystem und detaillierte Statistiken implementiert
- July 09, 2025: Vollständige Stripe-Integration - Automatische Kunden- und Bestellerstellung, Webhook-System, Rechnungsautomation, erweiterte Dashboard-Statistiken
- July 09, 2025: Kundensystem vollständig implementiert - Registrierung, Login, Dashboard mit MySQL-Backend, sichere Passwort-Hashing, separate customer/ Ordnerstruktur
- July 09, 2025: Konfigurationsspeicherung behoben - customer_id-Spalte hinzugefügt, Konfigurationen werden korrekt mit eingeloggten Benutzern verknüpft, Dashboard zeigt gespeicherte Konfigurationen an
- July 09, 2025: DHL API-Integration vollständig implementiert - Automatische Versandetiketten-Erstellung, Sendungsverfolgung, Admin-Panel Integration mit tracking_number und shipping_label_url Feldern, öffentliche Tracking-Seite unter /sendungsverfolgung
- July 09, 2025: Alternative DHL Tracking-Systeme implementiert - Weiterleitung zu DHL.de, 17track.net, ParcelsApp.com als Fallback-Optionen ohne API-Schlüssel
- July 09, 2025: Kundendashboard auf traditionelles Design umgestellt - Behält alle modernen Funktionen (Bestellungen, Rechnungen, Konfigurationen, Tracking) aber mit klassischem Layout
- July 09, 2025: Dashboard auf ursprüngliches, ganz einfaches Design zurückgesetzt - Minimaler Header, einfache Navigation, grundlegende Card-Layouts ohne komplexe Styling-Effekte
- July 09, 2025: Rechnungsanzeige im Kundendashboard behoben - Doppelte Routen entfernt, Template-Fehler korrigiert, Rechnungen werden nun korrekt angezeigt mit Pagination und vollständigen Informationen
- July 09, 2025: DHL Geschäftskunden API vollständig implementiert - OAuth 2.0 Authentifizierung, automatische Versandetikett-Erstellung über Geschäftskonto-Abrechnung, Demo-Fallback-System für Entwicklung
- July 09, 2025: DHL API-System bereit für Freischaltung - Vollständige Integration implementiert mit echten Credentials, detaillierte Freischaltungsanleitung erstellt, System wartet nur noch auf DHL API-Aktivierung für Live-Betrieb

## User Preferences

Preferred communication style: Simple, everyday language.