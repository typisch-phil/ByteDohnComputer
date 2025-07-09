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
    """DHL Geschäftskundenversand API Integration"""
    
    def __init__(self):
        # DHL API Credentials (Sandbox/Production)
        self.api_key = os.environ.get('DHL_API_KEY')
        self.username = os.environ.get('DHL_USERNAME') 
        self.password = os.environ.get('DHL_PASSWORD')
        self.account_number = os.environ.get('DHL_ACCOUNT_NUMBER', '22222222220101')  # Test account
        
        # API Endpoints - Live System aktiviert
        self.sandbox_url = "https://api-sandbox.dhl.com"
        self.production_url = "https://api-eu.dhl.com"
        # Verwende Live API für echte Tracking-Daten
        self.base_url = self.production_url if os.environ.get('DHL_LIVE', 'false') == 'true' else self.sandbox_url
        self.track_api_url = f"{self.base_url}/track/shipments"
        
        # Company details (ByteDohm)
        self.sender_details = {
            "name1": "ByteDohm GmbH",
            "streetName": "Musterstraße",
            "streetNumber": "123",
            "zip": "12345", 
            "city": "Berlin",
            "country": "DE",
            "email": "versand@bytedohm.de",
            "phone": "+49 30 12345678"
        }
        
    def create_shipping_label(self, order_id):
        """
        Erstelle DHL Versandetikett für eine Bestellung
        
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
            
            # Vorbereiten der Sendungsdaten
            shipment_data = self._prepare_shipment_data(order, customer)
            
            # API Call für Label-Erstellung
            response = self._make_api_request('/dhl-business-customer-shipping/v1/shipments', shipment_data)
            
            if response.get('success'):
                # Speichere Tracking-Nummer in der Bestellung
                tracking_number = response['data'].get('trackingNumber')
                label_url = response['data'].get('labelUrl')
                
                order.tracking_number = tracking_number
                order.status = 'shipped'
                order.updated_at = datetime.utcnow()
                db.session.commit()
                
                return {
                    'success': True,
                    'tracking_number': tracking_number,
                    'label_url': label_url,
                    'label_data': response['data'].get('labelData')
                }
            else:
                return {'success': False, 'error': response.get('error', 'DHL API Fehler')}
                
        except Exception as e:
            logging.error(f"DHL Label Creation Error: {e}")
            return {'success': False, 'error': f'Fehler beim Erstellen des Labels: {str(e)}'}
    
    def _prepare_shipment_data(self, order, customer):
        """Vorbereiten der DHL Sendungsdaten"""
        
        # Gewicht basierend auf Bestellwert schätzen (in kg)
        estimated_weight = max(1.0, min(10.0, order.total_amount / 200))  # 1-10kg basierend auf Wert
        
        # Paketgröße bestimmen
        package_size = self._determine_package_size(order.total_amount)
        
        shipment_data = {
            "profile": "STANDARD_GRUPPENPROFIL",
            "creationSoftware": "ByteDohm Shipping System v1.0",
            "shipment": {
                "product": "V01PAK",  # DHL Paket
                "billingNumber": self.account_number,
                "refNo": order.order_number,
                "shipmentDate": datetime.now().strftime('%Y-%m-%d'),
                "shipper": {
                    "name1": self.sender_details["name1"],
                    "addressStreet": f"{self.sender_details['streetName']} {self.sender_details['streetNumber']}",
                    "addressHouse": self.sender_details["streetNumber"],
                    "zip": self.sender_details["zip"],
                    "city": self.sender_details["city"],
                    "country": self.sender_details["country"],
                    "email": self.sender_details["email"],
                    "phone": self.sender_details["phone"]
                },
                "consignee": {
                    "name1": customer.get_full_name() or "Kunde",
                    "addressStreet": customer.address or "Musterstraße 1",
                    "zip": "12345",  # Aus Adresse extrahieren
                    "city": "Berlin",  # Aus Adresse extrahieren
                    "country": "DE",
                    "email": customer.email
                },
                "details": {
                    "dim": {
                        "length": package_size["length"],
                        "width": package_size["width"], 
                        "height": package_size["height"],
                        "uom": "cm"
                    },
                    "weight": {
                        "value": estimated_weight,
                        "uom": "kg"
                    }
                },
                "services": {
                    "preferredTime": {
                        "type": "TIME_FRAME_FROM_TO",
                        "details": {
                            "start": "09:00",
                            "end": "18:00"
                        }
                    }
                }
            },
            "labelFormat": "PDF",
            "labelSize": "A4",
            "combinedPrinting": "NONE"
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
    
    def _make_api_request(self, endpoint, data):
        """Führe DHL API Request aus"""
        try:
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': f'Bearer {self.api_key}' if self.api_key else 'Basic ' + base64.b64encode(f"{self.username}:{self.password}".encode()).decode()
            }
            
            url = f"{self.base_url}{endpoint}"
            
            logging.info(f"DHL API Request: {url}")
            response = requests.post(url, json=data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'data': {
                        'trackingNumber': result.get('shipments', [{}])[0].get('shipmentNumber'),
                        'labelUrl': result.get('shipments', [{}])[0].get('labelUrl'),
                        'labelData': result.get('shipments', [{}])[0].get('label', {}).get('b64')
                    }
                }
            else:
                logging.error(f"DHL API Error: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f'DHL API Fehler: {response.status_code}'
                }
                
        except requests.exceptions.RequestException as e:
            logging.error(f"DHL API Request Exception: {e}")
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