"""
Alternative DHL Tracking Methoden ohne API-Key
Verschiedene Optionen für die Sendungsverfolgung
"""

import requests
import re
import logging

class DHLAlternativeTracking:
    """Alternative DHL Tracking Methoden"""
    
    def __init__(self):
        self.dhl_base_url = "https://www.dhl.de"
        self.tracking_url = "https://www.dhl.de/de/privatkunden/pakete-empfangen/verfolgen.html"
        
    def get_tracking_options(self, tracking_number):
        """Verschiedene Tracking-Optionen für eine Sendungsnummer"""
        options = []
        
        # Option 1: Direkte DHL Website Weiterleitung
        options.append({
            'type': 'redirect',
            'name': 'DHL Website',
            'url': f"{self.tracking_url}?lang=de&idc={tracking_number}",
            'description': 'Öffnet die offizielle DHL Sendungsverfolgung'
        })
        
        # Option 2: 17track.net (Universeller Tracking Service)
        options.append({
            'type': 'redirect',
            'name': '17track.net',
            'url': f"https://www.17track.net/de/track#nums={tracking_number}",
            'description': 'Universeller Tracking-Service für verschiedene Carrier'
        })
        
        # Option 3: Parcelsapp.com
        options.append({
            'type': 'redirect',
            'name': 'ParcelsApp',
            'url': f"https://parcelsapp.com/de/tracking/{tracking_number}",
            'description': 'Tracking-Service mit detaillierten Informationen'
        })
        
        # Option 4: Lokaler Status Check
        options.append({
            'type': 'local',
            'name': 'Lokaler Status',
            'description': 'Zeigt den letzten bekannten Status aus unserer Datenbank'
        })
        
        return options
    
    def get_tracking_iframe_url(self, tracking_number):
        """Erstelle URL für DHL Tracking iFrame"""
        return f"https://www.dhl.de/de/privatkunden/pakete-empfangen/verfolgen.html?lang=de&idc={tracking_number}&embedded=true"
    
    def validate_dhl_tracking_number(self, tracking_number):
        """Validiere DHL Tracking-Nummer Format"""
        # DHL Deutschland Tracking-Nummern
        patterns = [
            r'^\d{12}$',  # 12 Ziffern
            r'^\d{20}$',  # 20 Ziffern
            r'^00340\d{15}$',  # DHL Express
            r'^JD\d{18}$',  # DHL Paket
        ]
        
        for pattern in patterns:
            if re.match(pattern, tracking_number):
                return True
        return False
    
    def get_alternative_tracking_html(self, tracking_number):
        """Generiere HTML für alternative Tracking-Methoden"""
        if not self.validate_dhl_tracking_number(tracking_number):
            return {
                'valid': False,
                'error': 'Ungültige DHL Tracking-Nummer'
            }
        
        options = self.get_tracking_options(tracking_number)
        iframe_url = self.get_tracking_iframe_url(tracking_number)
        
        return {
            'valid': True,
            'tracking_number': tracking_number,
            'options': options,
            'iframe_url': iframe_url,
            'direct_dhl_url': f"{self.tracking_url}?lang=de&idc={tracking_number}"
        }

def get_alternative_tracking_data(tracking_number):
    """Hauptfunktion für alternative Tracking-Daten"""
    tracker = DHLAlternativeTracking()
    return tracker.get_alternative_tracking_html(tracking_number)

def create_tracking_widget_html(tracking_number):
    """Erstelle HTML Widget für Tracking"""
    data = get_alternative_tracking_data(tracking_number)
    
    if not data['valid']:
        return f"""
        <div class="alert alert-danger">
            <h5><i class="fas fa-exclamation-triangle"></i> Fehler</h5>
            <p>{data['error']}</p>
        </div>
        """
    
    html = f"""
    <div class="tracking-widget">
        <div class="card">
            <div class="card-header">
                <h5><i class="fas fa-truck"></i> Sendungsverfolgung</h5>
                <p class="mb-0">Tracking-Nummer: <strong>{tracking_number}</strong></p>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-8">
                        <h6>Tracking-Optionen:</h6>
                        <div class="list-group">
    """
    
    for option in data['options']:
        if option['type'] == 'redirect':
            html += f"""
                        <a href="{option['url']}" target="_blank" class="list-group-item list-group-item-action">
                            <div class="d-flex w-100 justify-content-between">
                                <h6 class="mb-1">{option['name']}</h6>
                                <small><i class="fas fa-external-link-alt"></i></small>
                            </div>
                            <p class="mb-1">{option['description']}</p>
                        </a>
            """
    
    html += f"""
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card bg-light">
                            <div class="card-body text-center">
                                <h6>Schnell-Link</h6>
                                <a href="{data['direct_dhl_url']}" target="_blank" class="btn btn-primary">
                                    <i class="fas fa-truck"></i> Bei DHL verfolgen
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """
    
    return html