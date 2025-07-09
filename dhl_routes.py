"""
DHL API Routes für ByteDohm
Versand-Routen für Kundenseite
"""

from flask import jsonify, request, render_template
from app import app
from dhl_integration import create_shipping_label_for_order, track_order_shipment, get_shipping_quote
from models import Order
import logging

@app.route('/api/shipping/rates', methods=['POST'])
def get_shipping_rates():
    """Hole Versandkosten für Checkout"""
    try:
        data = request.get_json()
        destination = data.get('country', 'DE')
        weight = data.get('weight', 1.0)
        
        result = get_shipping_quote(destination, weight)
        
        if result['success']:
            return jsonify({
                'success': True,
                'rates': result['rates']
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
            
    except Exception as e:
        logging.error(f"Shipping rates error: {e}")
        return jsonify({
            'success': False,
            'error': 'Fehler beim Abrufen der Versandkosten'
        }), 500

@app.route('/api/track/<tracking_number>')
def track_shipment(tracking_number):
    """Öffentliche Sendungsverfolgung"""
    try:
        result = track_order_shipment(tracking_number)
        
        if result['success']:
            return jsonify({
                'success': True,
                'tracking_data': result['data']
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
            
    except Exception as e:
        logging.error(f"Tracking error: {e}")
        return jsonify({
            'success': False,
            'error': 'Fehler beim Verfolgen der Sendung'
        }), 500

@app.route('/sendungsverfolgung')
def tracking_page():
    """Sendungsverfolgung Seite mit Alternativen"""
    tracking_number = request.args.get('tracking')
    tracking_data = None
    error = None
    alternatives = None
    
    if tracking_number:
        try:
            # Versuche primäre API
            result = track_order_shipment(tracking_number)
            if result['success']:
                tracking_data = result['data']
            else:
                error = result['error']
                
            # Immer alternative Optionen bereitstellen
            from dhl_alternatives import get_alternative_tracking_data
            alternatives = get_alternative_tracking_data(tracking_number)
            
        except Exception as e:
            error = f"Fehler beim Verfolgen: {str(e)}"
            # Auch bei Fehlern alternative Optionen anbieten
            try:
                from dhl_alternatives import get_alternative_tracking_data
                alternatives = get_alternative_tracking_data(tracking_number)
            except:
                pass
    
    return render_template('tracking.html', 
                         tracking_number=tracking_number,
                         tracking_data=tracking_data,
                         error=error,
                         alternatives=alternatives)

@app.route('/api/shipping/estimate', methods=['POST'])
def estimate_shipping():
    """Schätze Versandkosten basierend auf Warenkorb"""
    try:
        data = request.get_json()
        cart_items = data.get('cart_items', [])
        destination = data.get('country', 'DE')
        
        # Gewicht basierend auf Artikeln schätzen
        total_weight = 0.0
        for item in cart_items:
            # Standard-Gewichte für PC-Komponenten
            if item.get('type') == 'component':
                category = item.get('category', '')
                if 'cpu' in category.lower():
                    total_weight += 0.5
                elif 'gpu' in category.lower():
                    total_weight += 1.5
                elif 'motherboard' in category.lower():
                    total_weight += 1.0
                elif 'ram' in category.lower():
                    total_weight += 0.2
                elif 'ssd' in category.lower():
                    total_weight += 0.1
                elif 'case' in category.lower():
                    total_weight += 3.0
                elif 'psu' in category.lower():
                    total_weight += 1.5
                else:
                    total_weight += 0.5
            elif item.get('type') == 'prebuilt':
                total_weight += 8.0  # Kompletter PC
        
        # Mindestgewicht 1kg
        total_weight = max(1.0, total_weight)
        
        result = get_shipping_quote(destination, total_weight)
        
        if result['success']:
            return jsonify({
                'success': True,
                'rates': result['rates'],
                'estimated_weight': total_weight
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
            
    except Exception as e:
        logging.error(f"Shipping estimate error: {e}")
        return jsonify({
            'success': False,
            'error': 'Fehler bei der Versandkostenschätzung'
        }), 500