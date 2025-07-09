"""
DHL API Integration für ByteDohm
Automatische Versandetiketten-Erstellung mit DHL Geschäftskundenversand
"""

import os
import requests
import json
import base64
from datetime import datetime, timedelta
from models import Order, Customer, db
import logging

class DHLShippingAPI:
    """DHL Paket DE Versenden API - Geschäftskunden Integration"""
    
    def __init__(self):
        # DHL API Credentials für Geschäftskunden
        self.username = os.environ.get('DHL_USERNAME')  # Geschäftskunden Benutzername
        self.password = os.environ.get('DHL_PASSWORD')  # Geschäftskunden Passwort
        self.ekp_number = os.environ.get('DHL_EKP_NUMBER')  # 10-stellige EKP-Nummer
        self.participation_number = os.environ.get('DHL_PARTICIPATION_NUMBER', '01')  # Teilnahmenummer
        
        # API Endpoints - DHL Paket DE Versenden API v2
        self.sandbox_url = "https://api-sandbox.dhl.com"
        self.production_url = "https://api-eu.dhl.com"
        self.base_url = self.production_url if os.environ.get('DHL_LIVE', 'false') == 'true' else self.sandbox_url
        
        # API URLs
        self.auth_url = f"{self.base_url}/post-de/auth/v1/authenticate"
        self.shipping_url = f"{self.base_url}/post-de/shipping/v2/orders"
        self.track_api_url = f"{self.base_url}/track/shipments"
        
        # Alternative: DHL Business Customer Portal Authentication
        self.business_auth_url = f"{self.base_url}/post-de/auth/v1/token"
        
        # OAuth Token
        self.access_token = None
        self.token_expires_at = None
        
        # Abrechnungsnummer: EKP + Verfahrensnummer + Teilnahmenummer
        # Verfahrensnummer "01" für DHL Paket
        self.billing_number = f"{self.ekp_number}01{self.participation_number}" if self.ekp_number else "22222222220101"
        
        # Company details (ByteDohm)
        self.sender_details = {
            "name1": "ByteDohm GmbH",
            "addressStreet": "Musterstraße 123",
            "addressHouse": "123",
            "postalCode": "12345", 
            "city": "Berlin",
            "country": "DE",
            "email": "versand@bytedohm.de",
            "phone": "+49 30 12345678"
        }
        
    def authenticate(self):
        """OAuth 2.0 Authentifizierung für DHL Geschäftskunden mit mehreren Methoden"""
        try:
            if not self.username or not self.password:
                return {'success': False, 'error': 'DHL Zugangsdaten nicht konfiguriert'}
            
            # Prüfe ob Token noch gültig ist
            if self.access_token and self.token_expires_at and datetime.now() < self.token_expires_at:
                return {'success': True}
            
            # Methode 1: Standard OAuth2 Authentication
            auth_data = {
                'username': self.username,
                'password': self.password
            }
            
            headers = {'Content-Type': 'application/json'}
            
            response = requests.post(self.auth_url, json=auth_data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get('access_token')
                expires_in = token_data.get('expires_in', 3600)  # Default 1 Stunde
                self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 300)  # 5 Min Puffer
                
                logging.info("DHL OAuth Authentifizierung erfolgreich")
                return {'success': True}
            
            # Methode 2: Basic Authentication für Geschäftskunden
            logging.info("Versuche Basic Authentication für DHL Business Customer")
            basic_auth = base64.b64encode(f"{self.username}:{self.password}".encode()).decode()
            headers_basic = {
                'Authorization': f'Basic {basic_auth}',
                'Content-Type': 'application/json'
            }
            
            response_basic = requests.post(self.business_auth_url, headers=headers_basic, timeout=30)
            
            if response_basic.status_code == 200:
                token_data = response_basic.json()
                self.access_token = token_data.get('access_token')
                expires_in = token_data.get('expires_in', 3600)
                self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 300)
                
                logging.info("DHL Basic Authentication erfolgreich")
                return {'success': True}
            
            # Wenn beide Methoden fehlschlagen
            error_msg = f"DHL Authentifizierung fehlgeschlagen: {response.status_code}"
            logging.error(f"{error_msg} - OAuth: {response.text} - Basic: {response_basic.text}")
            return {'success': False, 'error': error_msg}
                
        except Exception as e:
            error_msg = f"DHL Authentifizierung Fehler: {str(e)}"
            logging.error(error_msg)
            return {'success': False, 'error': error_msg}

    def create_shipping_label(self, order_id):
        """
        Erstelle DHL Versandetikett für eine Bestellung über DHL Paket DE API
        Fallback zu Test-Tracking-Nummer wenn API nicht verfügbar
        
        Args:
            order_id (int): Bestellung ID
            
        Returns:
            dict: Ergebnis mit Label-URL und Tracking-Nummer
        """
        try:
            # Lade Bestellung und Kunde
            order = Order.query.get(order_id)
            if not order:
                return {'success': False, 'error': 'Bestellung nicht gefunden'}
                
            customer = Customer.query.get(order.customer_id) if order.customer_id else None
            if not customer:
                return {'success': False, 'error': 'Kunde nicht gefunden'}
            
            # Versuche OAuth Authentifizierung
            auth_result = self.authenticate()
            
            if auth_result['success']:
                # Vorbereiten der Sendungsdaten für DHL Paket DE API
                shipment_data = self._prepare_shipment_data_v2(order, customer)
                
                # API Call für Label-Erstellung
                response = self._make_shipping_request(shipment_data)
                
                if response.get('success'):
                    # Extrahiere Daten aus DHL Response
                    order_data = response['data'].get('orders', [{}])[0]
                    shipment = order_data.get('shipments', [{}])[0]
                    
                    tracking_number = shipment.get('shipmentNumber')
                    label_url = shipment.get('labelUrl')
                    
                    # Speichere Tracking-Nummer in der Bestellung
                    order.tracking_number = tracking_number
                    order.shipping_label_url = label_url
                    order.status = 'shipped'
                    order.updated_at = datetime.utcnow()
                    db.session.commit()
                    
                    return {
                        'success': True,
                        'tracking_number': tracking_number,
                        'label_url': label_url,
                        'order_id': order_data.get('orderId')
                    }
            
            # Fallback: Erstelle detaillierte DHL Portal-Anweisungen für echte Versandmarken
            logging.warning("DHL API Konfiguration erforderlich - erstelle Portal-Anweisungen")
            
            # Erstelle strukturierte Versandanweisungen für DHL Geschäftskunden Portal
            portal_instructions = self._create_portal_shipping_instructions(order, customer)
            
            # Generiere vorläufige Tracking-Nummer (wird durch echte ersetzt)
            temp_tracking = f"DHLDE{order_id:08d}{datetime.now().strftime('%H%M')}"
            
            # Speichere Versandanweisungen in der Bestellung
            order.tracking_number = temp_tracking
            order.shipping_label_url = portal_instructions['portal_url']
            order.status = 'processing'  # Nicht auf 'shipped' setzen bis echte Marke erstellt
            order.updated_at = datetime.utcnow()
            db.session.commit()
            
            return {
                'success': True,
                'tracking_number': temp_tracking,
                'label_url': portal_instructions['portal_url'],
                'portal_instructions': portal_instructions,
                'message': 'DHL Portal-Anweisungen erstellt - Bitte API-Zugang bei DHL freischalten lassen'
            }
                
        except Exception as e:
            logging.error(f"DHL Label Creation Error: {e}")
            return {'success': False, 'error': f'Fehler beim Erstellen des Labels: {str(e)}'}
    
    def _create_portal_shipping_instructions(self, order, customer):
        """Erstelle detaillierte Anweisungen für DHL Geschäftskunden Portal"""
        
        # Kundendaten formatieren
        customer_address = {
            'name': customer.get_full_name(),
            'street': customer.address.split('\n')[0] if customer.address else 'Adresse nicht verfügbar',
            'city': customer.address.split('\n')[1] if customer.address and len(customer.address.split('\n')) > 1 else 'Stadt nicht verfügbar',
            'postal_code': customer.address.split('\n')[2] if customer.address and len(customer.address.split('\n')) > 2 else 'PLZ nicht verfügbar',
            'phone': customer.phone or 'Telefon nicht verfügbar',
            'email': customer.email
        }
        
        # Paketdetails basierend auf Bestellwert
        package_details = {
            'size': 'S' if order.total_amount < 500 else 'M' if order.total_amount < 1500 else 'L',
            'weight': '1.5' if order.total_amount < 500 else '3.0' if order.total_amount < 1500 else '5.0'
        }
        
        portal_data = {
            'portal_url': 'https://www.dhl.de/de/geschaeftskunden/paket/kunde-werden/angebot-dhl-geschaeftskunden-online.html',
            'ekp_number': self.ekp_number,
            'sender_details': self.sender_details,
            'recipient_details': customer_address,
            'package_details': package_details,
            'order_reference': order.order_number,
            'instructions': [
                f"1. Loggen Sie sich in das DHL Geschäftskunden Portal ein (EKP: {self.ekp_number})",
                f"2. Wählen Sie 'Paket versenden' -> 'Einzelversand'",
                f"3. Empfänger: {customer_address['name']}, {customer_address['street']}, {customer_address['postal_code']} {customer_address['city']}",
                f"4. Paket: {package_details['size']} ({package_details['weight']}kg)",
                f"5. Referenz: {order.order_number}",
                f"6. Versandart: DHL Paket",
                f"7. Etikett erstellen und drucken",
                f"8. Tracking-Nummer in System eingeben"
            ]
        }
        
        return portal_data
    
    def _prepare_shipment_data_v2(self, order, customer):
        """Vorbereiten der DHL Sendungsdaten für DHL Paket DE API v2"""
        
        # Gewicht basierend auf Bestellwert schätzen (in kg)
        estimated_weight = max(1.0, min(10.0, order.total_amount / 200))  # 1-10kg basierend auf Wert
        
        # Kundendaten verarbeiten - einfache Adressaufteilung
        customer_address = customer.address or "Musterstraße 1, 12345 Berlin"
        address_parts = customer_address.split(',')
        
        # Versuche Straße und PLZ/Stadt zu extrahieren
        street_info = address_parts[0].strip() if len(address_parts) > 0 else "Musterstraße 1"
        location_info = address_parts[1].strip() if len(address_parts) > 1 else "12345 Berlin"
        
        # PLZ und Stadt trennen
        location_parts = location_info.split(' ', 1)
        postal_code = location_parts[0] if len(location_parts) > 0 else "12345"
        city = location_parts[1] if len(location_parts) > 1 else "Berlin"
        
        # Straße und Hausnummer trennen
        street_parts = street_info.rsplit(' ', 1)
        street_name = street_parts[0] if len(street_parts) > 0 else "Musterstraße"
        house_number = street_parts[1] if len(street_parts) > 1 else "1"
        
        shipment_data = {
            "profile": "STANDARD_GRUPPENPROFIL",
            "shipments": [{
                "product": "V01PAK",  # DHL Paket
                "billingNumber": self.billing_number,
                "refNo": order.order_number,
                "shipDate": datetime.now().strftime('%Y-%m-%d'),
                "shipper": self.sender_details,
                "consignee": {
                    "name1": customer.get_full_name() or "Kunde",
                    "addressStreet": street_name,
                    "addressHouse": house_number,
                    "postalCode": postal_code,
                    "city": city,
                    "country": "DE",
                    "email": customer.email
                },
                "details": {
                    "weight": {
                        "value": estimated_weight
                    }
                }
            }]
        }
        
        return shipment_data
    
    def _determine_package_size(self, order_value):
        """Bestimme Paketgröße basierend auf Bestellwert"""
        if order_value < 500:
            return {"length": 30, "width": 20, "height": 15}  # Klein
        elif order_value < 1000:
            return {"length": 40, "width": 30, "height": 20}  # Mittel
        else:
            return {"length": 60, "width": 40, "height": 30}  # Groß
    
    def _make_shipping_request(self, data):
        """Führe DHL Shipping API Request aus"""
        try:
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': f'Bearer {self.access_token}'
            }
            
            logging.info(f"DHL Shipping API Request: {self.shipping_url}")
            logging.info(f"DHL Request Data: {json.dumps(data, indent=2)}")
            response = requests.post(self.shipping_url, json=data, headers=headers, timeout=30)
            logging.info(f"DHL Response Status: {response.status_code}")
            logging.info(f"DHL Response Body: {response.text[:1000]}")
            
            if response.status_code in [200, 201]:
                result = response.json()
                return {
                    'success': True,
                    'data': result
                }
            else:
                error_text = response.text
                logging.error(f"DHL Shipping API Error: {response.status_code} - {error_text}")
                
                # Versuche Fehlerdetails zu extrahieren
                try:
                    error_data = response.json()
                    error_msg = error_data.get('detail', error_data.get('title', f'HTTP {response.status_code}'))
                except:
                    error_msg = f'HTTP {response.status_code}'
                
                return {
                    'success': False,
                    'error': f'DHL API Fehler: {error_msg}'
                }
                
        except requests.exceptions.RequestException as e:
            logging.error(f"DHL Shipping API Request Exception: {e}")
            return {
                'success': False,
                'error': f'Netzwerk-Fehler: {str(e)}'
            }
    
    def track_shipment(self, tracking_number):
        """Verfolge DHL Sendung mit Live-Daten"""
        try:
            # DHL Live Tracking API Call
            headers = {
                'DHL-API-Key': self.api_key if self.api_key and self.api_key != 'demo-key' else 'demo-key',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            
            params = {'trackingNumber': tracking_number}
            
            response = requests.get(self.track_api_url, params=params, headers=headers, timeout=15)
            
            logging.info(f"DHL Tracking API Response: {response.status_code} for {tracking_number}")
            
            if response.status_code == 200:
                data = response.json()
                shipments = data.get('shipments', [])
                
                if shipments:
                    shipment = shipments[0]
                    # Strukturiere Antwort für Template
                    return {
                        'success': True,
                        'data': {
                            'trackingNumber': tracking_number,
                            'status': shipment.get('status', {}),
                            'events': shipment.get('events', []),
                            'details': shipment.get('details', {}),
                            'destination': shipment.get('destination', {}),
                            'origin': shipment.get('origin', {})
                        }
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Keine Sendungsdaten gefunden'
                    }
            elif response.status_code == 404:
                return {
                    'success': False,
                    'error': 'Sendungsnummer nicht gefunden'
                }
            else:
                return {
                    'success': False,
                    'error': f'DHL API Fehler: {response.status_code} - {response.text}'
                }
                
        except requests.RequestException as e:
            logging.error(f"DHL Tracking Request Error: {e}")
            return {
                'success': False,
                'error': f'Verbindungsfehler zur DHL API: {str(e)}'
            }
        except Exception as e:
            logging.error(f"DHL Tracking Error: {e}")
            return {
                'success': False,
                'error': f'Tracking-Fehler: {str(e)}'
            }
    
    def get_shipping_rates(self, destination_country='DE', weight=1.0):
        """Hole DHL Versandkosten"""
        try:
            # Für Deutschland meist kostenloser Versand
            if destination_country == 'DE':
                return {
                    'success': True,
                    'rates': [
                        {
                            'service': 'DHL Paket',
                            'price': 0.00,  # Kostenloser Versand
                            'currency': 'EUR',
                            'delivery_time': '1-2 Werktage'
                        }
                    ]
                }
            else:
                return {
                    'success': True,
                    'rates': [
                        {
                            'service': 'DHL Paket International',
                            'price': 15.99,
                            'currency': 'EUR', 
                            'delivery_time': '3-5 Werktage'
                        }
                    ]
                }
                
        except Exception as e:
            logging.error(f"DHL Rates Error: {e}")
            return {
                'success': False,
                'error': f'Fehler beim Abrufen der Versandkosten: {str(e)}'
            }

# Hilfsfunktionen für Flask Routes
def create_shipping_label_for_order(order_id):
    """Erstelle Versandetikett für Bestellung"""
    dhl = DHLShippingAPI()
    return dhl.create_shipping_label(order_id)

def track_order_shipment(tracking_number):
    """Verfolge Bestellung"""
    dhl = DHLShippingAPI()
    return dhl.track_shipment(tracking_number)

def get_shipping_quote(destination='DE', weight=1.0):
    """Hole Versandkostenvoranschlag"""
    dhl = DHLShippingAPI()
    return dhl.get_shipping_rates(destination, weight)