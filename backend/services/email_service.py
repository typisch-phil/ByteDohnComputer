"""
E-Mail Service für ByteDohm
Sendet automatische E-Mails für Registrierung, Bestellungen, Status-Updates und Newsletter
"""
import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from flask import render_template_string
from backend.models.models import Customer, Order


class EmailService:
    """E-Mail Service Klasse"""

    def __init__(self):
        # SMTP Konfiguration
        self.smtp_server = os.environ.get('SMTP_SERVER', 'mail.bytedohm.de')
        self.smtp_port = int(os.environ.get('SMTP_PORT',
                                            '465'))  # Port 465 für SSL
        self.smtp_username = os.environ.get('SMTP_USERNAME',
                                            'no-reply@bytedohm.de')
        self.smtp_password = os.environ.get('SMTP_PASSWORD', 'HeikoCindy-8')
        self.sender_email = os.environ.get('FROM_EMAIL',
                                           'no-reply@bytedohm.de')
        self.sender_name = "ByteDohm.de"

    def _send_email(self, to_email, subject, html_body, text_body=None):
        """Interne Funktion zum E-Mail-Versand"""
        try:
            print(f"\n=== E-MAIL DEBUG ===")
            print(f"SMTP Server: {self.smtp_server}")
            print(f"SMTP Port: {self.smtp_port}")
            print(f"SMTP Username: {self.smtp_username}")
            print(
                f"SMTP Password: {'*' * len(self.smtp_password) if self.smtp_password else 'None'}"
            )
            print(
                f"Username length: {len(self.smtp_username) if self.smtp_username else 0}"
            )
            print(
                f"Password length: {len(self.smtp_password) if self.smtp_password else 0}"
            )
            print(f"From Email: {self.sender_email}")
            print(f"To Email: {to_email}")
            print(f"Subject: {subject}")
            print(f"===================\n")

            if not self.smtp_username or not self.smtp_password:
                logging.warning(
                    "SMTP Credentials nicht konfiguriert - E-Mail wird nicht gesendet"
                )
                print("FEHLER: SMTP Credentials fehlen!")
                return False

            # E-Mail erstellen
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.sender_name} <{self.sender_email}>"
            msg['To'] = to_email
            msg['Subject'] = subject

            # Text-Version
            if text_body:
                text_part = MIMEText(text_body, 'plain', 'utf-8')
                msg.attach(text_part)

            # HTML-Version
            html_part = MIMEText(html_body, 'html', 'utf-8')
            msg.attach(html_part)

            print("Verbinde mit SMTP Server...")
            # SMTP-Verbindung mit SSL/TLS-Verschlüsselung
            import ssl

            # Sichere SSL/TLS-Konfiguration
            context = ssl.create_default_context()

            # SMTP-Verbindung mit verbesserter Fehlerbehandlung
            server = None
            try:
                if self.smtp_port == 465:
                    # SSL-Verbindung für Port 465
                    server = smtplib.SMTP_SSL(self.smtp_server,
                                              self.smtp_port,
                                              context=context)
                    print("SSL-Verbindung hergestellt")
                else:
                    # STARTTLS für Port 587
                    server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                    print("SMTP Verbindung hergestellt")
                    server.starttls(context=context)
                    print("TLS-Verschlüsselung aktiviert")

                server.set_debuglevel(1)
                server.login(self.smtp_username, self.smtp_password)
                print("Login erfolgreich")
                server.send_message(msg)
                print("E-Mail gesendet!")

            finally:
                # Server-Verbindung sicher schließen
                if server:
                    try:
                        server.quit()
                    except:
                        pass

            logging.info(
                f"E-Mail erfolgreich gesendet an {to_email}: {subject}")
            print(f"SUCCESS: E-Mail an {to_email} gesendet!")
            return True

        except Exception as e:
            logging.error(f"E-Mail-Versand fehlgeschlagen an {to_email}: {e}")
            print(f"FEHLER beim E-Mail-Versand: {e}")
            print(f"Fehlertyp: {type(e).__name__}")
            return False

    def send_registration_email(self, customer):
        """Willkommens-E-Mail nach Registrierung"""
        subject = "Willkommen bei ByteDohm.de!"

        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f8f9fa; }
                .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }
                .header { text-align: center; color: #0d6efd; margin-bottom: 30px; }
                .content { line-height: 1.6; color: #333; }
                .footer { margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #666; font-size: 14px; }
                .button { display: inline-block; padding: 12px 24px; background: #0d6efd; color: white; text-decoration: none; border-radius: 4px; margin: 15px 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Willkommen bei ByteDohm.de!</h1>
                </div>
                <div class="content">
                    <p>Hallo {{ customer.first_name or 'lieber Kunde' }},</p>
                    
                    <p>herzlich willkommen bei ByteDohm.de! Wir freuen uns, dass Sie sich für unser PC-Konfigurations- und Prebuilt-System entschieden haben.</p>
                    
                    <p><strong>Ihre Vorteile:</strong></p>
                    <ul>
                        <li>🔧 Professioneller PC-Konfigurator mit Kompatibilitätsprüfung</li>
                        <li>💻 Hochwertige Prebuilt-PCs für Gaming und Workstation</li>
                        <li>🚚 Schneller Versand mit DHL-Tracking</li>
                        <li>📊 Persönliches Dashboard für Bestellungen und Konfigurationen</li>
                        <li>💳 Sichere Zahlung mit Stripe</li>
                    </ul>
                    
                    <div style="text-align: center;">
                        <a href="https://{{ domain }}/kunde/dashboard" class="button">Zum Dashboard</a>
                    </div>
                    
                    <p>Bei Fragen stehen wir Ihnen gerne zur Verfügung!</p>
                    
                    <p>Viele Grüße,<br>
                    Ihr ByteDohm.de Team</p>
                </div>
                <div class="footer">
                    <p>ByteDohm.de - Ihr Partner für maßgeschneiderte PC-Systeme</p>
                    <p>Diese E-Mail wurde automatisch generiert.</p>
                </div>
            </div>
        </body>
        </html>
        """

        domain = os.environ.get('REPLIT_DEV_DOMAIN', 'localhost:5000')
        html_body = render_template_string(html_template,
                                           customer=customer,
                                           domain=domain)

        return self._send_email(customer.email, subject, html_body)

    def send_order_confirmation_email(self, order):
        """Bestellbestätigungs-E-Mail"""
        subject = f"Bestellbestätigung #{order.order_number} - ByteDohm.de"

        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f8f9fa; }
                .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }
                .header { text-align: center; color: #0d6efd; margin-bottom: 30px; }
                .content { line-height: 1.6; color: #333; }
                .order-details { background: #f8f9fa; padding: 20px; border-radius: 4px; margin: 20px 0; }
                .footer { margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #666; font-size: 14px; }
                .item { border-bottom: 1px solid #eee; padding: 10px 0; }
                .total { font-weight: bold; font-size: 18px; color: #0d6efd; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Bestellbestätigung</h1>
                    <h2>#{{ order.order_number }}</h2>
                </div>
                <div class="content">
                    <p>Hallo {{ order.customer.first_name or 'lieber Kunde' }},</p>
                    
                    <p>vielen Dank für Ihre Bestellung bei ByteDohm.de! Wir haben Ihre Bestellung erhalten und bearbeiten sie umgehend.</p>
                    
                    <div class="order-details">
                        <h3>Bestelldetails</h3>
                        <p><strong>Bestellnummer:</strong> {{ order.order_number }}</p>
                        <p><strong>Bestelldatum:</strong> {{ order.created_at.strftime('%d.%m.%Y %H:%M') }}</p>
                        <p><strong>Status:</strong> {{ order.status }}</p>
                        <p><strong>Zahlungsstatus:</strong> {{ order.payment_status }}</p>
                        
                        <h4>Bestellte Artikel:</h4>
                        {% for item in order.order_items %}
                        <div class="item">
                            <strong>{{ item.item_name }}</strong><br>
                            Anzahl: {{ item.quantity }} × {{ "%.2f"|format(item.unit_price) }}€ = {{ "%.2f"|format(item.total_price) }}€
                        </div>
                        {% endfor %}
                        
                        <div class="total">
                            Gesamtsumme: {{ "%.2f"|format(order.total_amount) }}€
                        </div>
                    </div>
                    
                    <p><strong>Nächste Schritte:</strong></p>
                    <ul>
                        <li>Wir prüfen Ihre Bestellung und beginnen mit der Bearbeitung</li>
                        <li>Sie erhalten eine E-Mail, sobald Ihre Bestellung versandt wird</li>
                        <li>Verfolgen Sie den Status in Ihrem Dashboard</li>
                    </ul>
                    
                    <p>Bei Fragen zu Ihrer Bestellung stehen wir Ihnen gerne zur Verfügung!</p>
                    
                    <p>Viele Grüße,<br>
                    Ihr ByteDohm.de Team</p>
                </div>
                <div class="footer">
                    <p>ByteDohm.de - Ihr Partner für maßgeschneiderte PC-Systeme</p>
                </div>
            </div>
        </body>
        </html>
        """

        html_body = render_template_string(html_template, order=order)

        return self._send_email(order.customer.email, subject, html_body)

    def send_shipping_notification_email(self, order):
        """Versandbenachrichtigung mit Tracking-Nummer"""
        subject = f"Ihre Bestellung #{order.order_number} wurde versandt - ByteDohm.de"

        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f8f9fa; }
                .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }
                .header { text-align: center; color: #28a745; margin-bottom: 30px; }
                .content { line-height: 1.6; color: #333; }
                .tracking-info { background: #e8f5e8; padding: 20px; border-radius: 4px; margin: 20px 0; text-align: center; }
                .footer { margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #666; font-size: 14px; }
                .button { display: inline-block; padding: 12px 24px; background: #28a745; color: white; text-decoration: none; border-radius: 4px; margin: 15px 0; }
                .tracking-number { font-size: 24px; font-weight: bold; color: #28a745; font-family: monospace; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📦 Ihre Bestellung wurde versandt!</h1>
                    <h2>#{{ order.order_number }}</h2>
                </div>
                <div class="content">
                    <p>Hallo {{ order.customer.first_name or 'lieber Kunde' }},</p>
                    
                    <p>großartige Neuigkeiten! Ihre Bestellung wurde soeben versandt und ist auf dem Weg zu Ihnen.</p>
                    
                    {% if order.tracking_number %}
                    <div class="tracking-info">
                        <h3>🚚 Sendungsverfolgung</h3>
                        <p><strong>Tracking-Nummer:</strong></p>
                        <div class="tracking-number">{{ order.tracking_number }}</div>
                        <p>Verfolgen Sie Ihre Sendung in Echtzeit:</p>
                        <a href="https://www.dhl.de/de/privatkunden/pakete-empfangen/verfolgen.html?lang=de&idc={{ order.tracking_number }}" class="button" target="_blank">
                            Sendung verfolgen
                        </a>
                        <p><small>Alternativ können Sie die Tracking-Nummer direkt auf der DHL-Website eingeben.</small></p>
                    </div>
                    {% endif %}
                    
                    <div style="background: #f8f9fa; padding: 20px; border-radius: 4px; margin: 20px 0;">
                        <h3>Versanddetails</h3>
                        <p><strong>Bestellnummer:</strong> {{ order.order_number }}</p>
                        <p><strong>Versanddatum:</strong> {{ order.updated_at.strftime('%d.%m.%Y') }}</p>
                        <p><strong>Versanddienstleister:</strong> DHL</p>
                        <p><strong>Geschätzte Lieferzeit:</strong> 1-2 Werktage</p>
                    </div>
                    
                    <p><strong>Was passiert als nächstes?</strong></p>
                    <ul>
                        <li>Ihre Sendung ist unterwegs zu der angegebenen Lieferadresse</li>
                        <li>Sie erhalten eine SMS/E-Mail von DHL mit der genauen Zustellzeit</li>
                        <li>Verfolgen Sie den Sendungsstatus über die Tracking-Nummer</li>
                        <li>Bei Fragen wenden Sie sich gerne an unseren Kundenservice</li>
                    </ul>
                    
                    <p>Wir hoffen, dass Sie mit Ihrer Bestellung zufrieden sind!</p>
                    
                    <p>Viele Grüße,<br>
                    Ihr ByteDohm.de Team</p>
                </div>
                <div class="footer">
                    <p>ByteDohm.de - Ihr Partner für maßgeschneiderte PC-Systeme</p>
                </div>
            </div>
        </body>
        </html>
        """

        html_body = render_template_string(html_template, order=order)

        return self._send_email(order.customer.email, subject, html_body)

    def send_status_update_email(self, order, old_status, new_status):
        """Status-Update E-Mail"""
        status_names = {
            'pending': 'Ausstehend',
            'processing': 'In Bearbeitung',
            'shipped': 'Versandt',
            'delivered': 'Geliefert',
            'cancelled': 'Storniert'
        }

        subject = f"Status-Update für Bestellung #{order.order_number} - ByteDohm.de"

        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f8f9fa; }
                .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }
                .header { text-align: center; color: #0d6efd; margin-bottom: 30px; }
                .content { line-height: 1.6; color: #333; }
                .status-update { background: #e8f4fd; padding: 20px; border-radius: 4px; margin: 20px 0; text-align: center; }
                .footer { margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #666; font-size: 14px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📋 Status-Update</h1>
                    <h2>#{{ order.order_number }}</h2>
                </div>
                <div class="content">
                    <p>Hallo {{ order.customer.first_name or 'lieber Kunde' }},</p>
                    
                    <p>der Status Ihrer Bestellung hat sich geändert:</p>
                    
                    <div class="status-update">
                        <h3>Neuer Status</h3>
                        <p style="font-size: 18px; color: #0d6efd; font-weight: bold;">{{ new_status_name }}</p>
                        <p><small>Vorher: {{ old_status_name }}</small></p>
                        
                        {% if new_status == 'shipped' and order.tracking_number %}
                        <div style="margin-top: 20px; padding: 15px; background: #e8f5e8; border-radius: 4px;">
                            <h4 style="color: #28a745; margin: 0 0 10px 0;">📦 Sendungsverfolgung</h4>
                            <p><strong>Tracking-Nummer:</strong></p>
                            <p style="font-size: 20px; font-weight: bold; color: #28a745; font-family: monospace; margin: 10px 0;">{{ order.tracking_number }}</p>
                            <p style="margin: 15px 0 5px 0;">
                                <a href="https://www.dhl.de/de/privatkunden/pakete-empfangen/verfolgen.html?lang=de&idc={{ order.tracking_number }}" 
                                   style="display: inline-block; padding: 10px 20px; background: #28a745; color: white; text-decoration: none; border-radius: 4px;"
                                   target="_blank">
                                    Sendung verfolgen
                                </a>
                            </p>
                            <p><small>Geschätzte Lieferzeit: 1-2 Werktage</small></p>
                        </div>
                        {% endif %}
                    </div>
                    
                    <p>Sie können den aktuellen Status jederzeit in Ihrem Dashboard einsehen.</p>
                    
                    <p>Bei Fragen stehen wir Ihnen gerne zur Verfügung!</p>
                    
                    <p>Viele Grüße,<br>
                    Ihr ByteDohm.de Team</p>
                </div>
                <div class="footer">
                    <p>ByteDohm.de - Ihr Partner für maßgeschneiderte PC-Systeme</p>
                </div>
            </div>
        </body>
        </html>
        """

        html_body = render_template_string(
            html_template,
            order=order,
            old_status_name=status_names.get(old_status, old_status),
            new_status_name=status_names.get(new_status, new_status))

        return self._send_email(order.customer.email, subject, html_body)

    def send_newsletter_email(self, customer, subject, content, preheader=None, footer_text=None):
        """Newsletter E-Mail mit erweiterten Optionen"""
        try:
            # HTML E-Mail Template für Newsletter
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>{subject}</title>
                {f'<meta name="description" content="{preheader}">' if preheader else ''}
            </head>
            <body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f4f4f4;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white;">

                    <!-- Preheader (für E-Mail-Client Vorschau) -->
                    {f'<div style="display: none; font-size: 1px; color: #fefefe; line-height: 1px; max-height: 0px; max-width: 0px; opacity: 0; overflow: hidden;">{preheader}</div>' if preheader else ''}

                    <!-- Header -->
                    <div style="background-color: #2c3e50; color: white; text-align: center; padding: 30px;">
                        <h1 style="margin: 0; font-size: 32px;">ByteDohm Newsletter</h1>
                        <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">Ihr PC-Konfigurator</p>
                    </div>

                    <!-- Content -->
                    <div style="padding: 30px;">
                        <h2 style="color: #2c3e50; margin-top: 0; font-size: 24px;">{subject}</h2>

                        <div style="line-height: 1.6; color: #333; font-size: 16px;">
                            {content}
                        </div>

                        <div style="margin-top: 30px; padding: 20px; background-color: #f8f9fa; border-left: 4px solid #3498db;">
                            <p style="margin: 0; font-size: 14px; color: #666;">
                                💡 <strong>Tipp:</strong> Besuchen Sie unseren 
                                <a href="https://bytedohm.de/konfigurator" style="color: #3498db;">PC-Konfigurator</a> 
                                und erstellen Sie Ihren Traum-PC!
                            </p>
                        </div>

                        {f'<div style="margin-top: 20px; padding: 15px; background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 4px;"><p style="margin: 0; font-size: 14px; color: #856404;">{footer_text}</p></div>' if footer_text else ''}
                    </div>
                    
                    <!-- Footer -->
                    <div style="background-color: #34495e; color: white; padding: 20px; text-align: center;">
                        <p style="margin: 0; font-size: 14px;">
                            Diese E-Mail wurde an Newsletter-Abonnenten von ByteDohm.de gesendet.<br>
                            <strong>ByteDohm.de</strong> | Ihr Experte für PC-Konfiguration
                        </p>
                        <div style="margin-top: 15px; font-size: 12px; opacity: 0.8;">
                            <a href="https://bytedohm.de/newsletter/abmelden" style="color: #bdc3c7; text-decoration: none; margin: 0 10px;">Newsletter abbestellen</a> |
                            <a href="#" style="color: #bdc3c7; text-decoration: none; margin: 0 10px;">Im Browser anzeigen</a>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """

            # Text-Version für E-Mail-Clients die HTML nicht unterstützen
            text_body = f"""
            ByteDohm Newsletter

            {subject}

            {content}

            {f'{footer_text}' if footer_text else ''}
            
            ---
            ByteDohm.de - Ihr PC-Konfigurator
            Diese E-Mail wurde an Newsletter-Abonnenten gesendet.
            Abmelden: https://bytedohm.de/newsletter/abmelden
            """

            return self._send_email(customer.email, subject, html_body, text_body)

        except Exception as e:
            logging.error(f"Fehler beim Senden der Newsletter-E-Mail: {e}")
            return False


# Global instance
email_service = EmailService()


# Helper functions
def send_registration_email(customer):
    """Sende Willkommens-E-Mail"""
    return email_service.send_registration_email(customer)


def send_order_confirmation_email(order):
    """Sende Bestellbestätigung"""
    return email_service.send_order_confirmation_email(order)


def send_shipping_notification_email(order):
    """Sende Versandbenachrichtigung"""
    return email_service.send_shipping_notification_email(order)


def send_status_update_email(order, old_status, new_status):
    """Sende Status-Update"""
    return email_service.send_status_update_email(order, old_status,
                                                  new_status)


def send_newsletter_email(customer,
                          subject,
                          content,
                          preheader=None,
                          footer_text=None):
    """Sende Newsletter"""
    return email_service.send_newsletter_email(customer, subject, content,
                                               preheader, footer_text)
