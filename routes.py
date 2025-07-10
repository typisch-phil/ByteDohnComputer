from flask import render_template, request, jsonify, redirect, url_for
from app import app, db
from models import Configuration, Component, PrebuiltPC, Customer, Order, OrderItem, Invoice
import json
import os
import stripe
from datetime import datetime
import logging

# Configure Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

def load_components():
    """Load component data from MySQL database only"""
    components = {}
    
    try:
        # Load from MySQL database only
        db_components = Component.query.filter_by(is_active=True).all()
        for comp in db_components:
            if comp.category not in components:
                components[comp.category] = []
            
            comp_data = {
                'id': comp.id,
                'name': comp.name,
                'price': comp.price,
                **comp.get_specs()
            }
            components[comp.category].append(comp_data)
    except Exception as e:
        # If database is not connected, return empty structure
        print(f"Database error: {e}")
    
    # Initialize empty categories if no components exist yet
    if not components:
        components = {
            'cpus': [],
            'motherboards': [],
            'ram': [],
            'gpus': [],
            'ssds': [],
            'cases': [],
            'psus': [],
            'coolers': []
        }
    
    return components

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/konfigurator')
def configurator():
    components = load_components()
    
    # Check if loading a saved configuration
    load_config_id = request.args.get('load')
    saved_config = None
    
    if load_config_id:
        try:
            saved_config = Configuration.query.get(int(load_config_id))
            if saved_config:
                # Parse the components JSON
                saved_config.components_data = json.loads(saved_config.components)
        except:
            saved_config = None
    
    return render_template('configurator.html', 
                         components=components, 
                         saved_config=saved_config)

@app.route('/fertig-pcs')
def prebuild():
    # Load exclusively from MySQL database - no fallback data
    prebuilt_pcs = []
    
    try:
        db_prebuilts = PrebuiltPC.query.filter_by(is_active=True).order_by(PrebuiltPC.created_at.desc()).all()
        
        for pc in db_prebuilts:
            prebuilt_pcs.append({
                'id': pc.id,
                'name': pc.name,
                'price': pc.price,
                'image': pc.image_url or f"https://via.placeholder.com/400x300/2d2d2d/ff6b35?text={pc.name.replace(' ', '+')}",
                'category': pc.category,
                'description': pc.description,
                'specs': pc.get_specs(),
                'features': pc.get_features()
            })
    except Exception as e:
        print(f"Database error loading prebuilt PCs: {e}")
        # No fallback data - show empty list if database fails
        prebuilt_pcs = []
    
    return render_template('prebuild.html', prebuilts=prebuilt_pcs)

@app.route('/api/validate-compatibility', methods=['POST'])
def validate_compatibility():
    """Validate PC component compatibility"""
    try:
        data = request.json
        components = load_components()
        
        errors = []
        warnings = []
        
        # Get selected components - safely handle missing categories  
        # Map database categories to component types
        category_mapping = {
            'cpu': 'cpus',
            'motherboard': 'motherboards', 
            'ram': 'ram',
            'gpu': 'gpus',
            'ssd': 'ssds',
            'case': 'cases',
            'psu': 'psus',
            'cooler': 'coolers'
        }
        
        selected_cpu = None
        selected_mb = None
        selected_ram = None
        selected_gpu = None
        selected_cooler = None
        selected_case = None
        selected_psu = None
        
        # Handle all categories from the database structure
        all_components = {}
        for category in ['cpus', 'motherboards', 'ram', 'gpus', 'ssds', 'cases', 'psus', 'coolers']:
            all_components[category] = components.get(category, [])
        
        print(f"Debug - Received data: {data}")
        print(f"Debug - Available components: {list(components.keys())}")
        
        if data.get('cpu'):
            selected_cpu = next((cpu for cpu in all_components['cpus'] if cpu['id'] == data.get('cpu')), None)
            print(f"Debug - Selected CPU: {selected_cpu}")
        if data.get('motherboard'):
            selected_mb = next((mb for mb in all_components['motherboards'] if mb['id'] == data.get('motherboard')), None)
            print(f"Debug - Selected Motherboard: {selected_mb}")
        if data.get('ram'):
            selected_ram = next((ram for ram in all_components['ram'] if ram['id'] == data.get('ram')), None)
            print(f"Debug - Selected RAM: {selected_ram}")
        if data.get('gpu'):
            selected_gpu = next((gpu for gpu in all_components['gpus'] if gpu['id'] == data.get('gpu')), None)
        if data.get('cooler'):
            selected_cooler = next((cooler for cooler in all_components['coolers'] if cooler['id'] == data.get('cooler')), None)
        if data.get('case'):
            selected_case = next((case for case in all_components['cases'] if case['id'] == data.get('case')), None)
        if data.get('psu'):
            selected_psu = next((psu for psu in all_components['psus'] if psu['id'] == data.get('psu')), None)
        
        # CPU and Motherboard socket compatibility
        if selected_cpu and selected_mb:
            if selected_cpu.get('socket') != selected_mb.get('socket'):
                errors.append(f"CPU-Socket {selected_cpu.get('socket')} ist nicht kompatibel mit Motherboard-Socket {selected_mb.get('socket')}")
        
        # RAM compatibility
        if selected_ram and selected_mb:
            ram_type = selected_ram.get('type')
            # Handle both memory_type (string) and ram_types (array) formats
            mb_memory_types = selected_mb.get('memory_type')
            mb_ram_types = selected_mb.get('ram_types', [])
            
            print(f"Debug - RAM type: {ram_type}")
            print(f"Debug - MB memory_type: {mb_memory_types}")
            print(f"Debug - MB ram_types: {mb_ram_types}")
            
            # Check compatibility with either format
            compatible = False
            if mb_memory_types and ram_type == mb_memory_types:
                compatible = True
            elif mb_ram_types and ram_type in mb_ram_types:
                compatible = True
            
            if not compatible:
                supported_types = mb_memory_types or ', '.join(mb_ram_types) if mb_ram_types else 'Unbekannt'
                errors.append(f"RAM-Typ {ram_type} ist nicht kompatibel mit Motherboard (unterstützt: {supported_types})")
        elif selected_ram and not selected_mb:
            print(f"Debug - RAM selected but no motherboard found")
            errors.append(f"Kein kompatibles Motherboard ausgewählt für RAM-Typ {selected_ram.get('type')}")
        elif not selected_ram and selected_mb:
            print(f"Debug - Motherboard selected but no RAM found")
        
        # GPU and Case compatibility
        if selected_gpu and selected_case:
            if selected_gpu.get('length', 0) > selected_case.get('max_gpu_length', 999):
                errors.append(f"GPU zu lang ({selected_gpu.get('length')}mm) für das Gehäuse (max. {selected_case.get('max_gpu_length')}mm)")
        
        # Cooler compatibility
        if selected_cooler and selected_cpu:
            compatible_sockets = selected_cooler.get('compatible_sockets', [])
            if selected_cpu.get('socket') not in compatible_sockets:
                errors.append(f"Kühler nicht kompatibel mit CPU-Socket {selected_cpu.get('socket')}")
        
        if selected_cooler and selected_case:
            if selected_cooler.get('height', 0) > selected_case.get('max_cpu_cooler_height', 999):
                errors.append(f"Kühler zu hoch ({selected_cooler.get('height')}mm) für das Gehäuse (max. {selected_case.get('max_cpu_cooler_height')}mm)")
        
        # PSU power compatibility (basic check)
        if selected_psu and selected_cpu and selected_gpu:
            estimated_power = selected_cpu.get('tdp', 0) + selected_gpu.get('power_consumption', 0) + 150  # Base system power
            if selected_psu.get('wattage', 0) < estimated_power * 1.2:  # 20% headroom
                warnings.append(f"Netzteil könnte zu schwach sein. Geschätzt: {estimated_power}W, PSU: {selected_psu.get('wattage')}W")
    
        return jsonify({
            'compatible': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        })
    except Exception as e:
        print(f"Compatibility validation error: {e}")
        return jsonify({
            'compatible': True,
            'errors': [],
            'warnings': ['Kompatibilitätsprüfung temporär nicht verfügbar']
        })

@app.route('/api/components/<category>')
def get_components(category):
    """Get components by category"""
    components = load_components()
    return jsonify(components.get(category, []))

@app.route('/api/save-configuration', methods=['POST'])
def save_configuration():
    """Save PC configuration to database"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('name') or not data.get('components'):
            return jsonify({'error': 'Name und Komponenten sind erforderlich'}), 400
        
        # Get current customer if logged in
        customer_id = None
        try:
            from flask_login import current_user
            if current_user.is_authenticated and hasattr(current_user, 'id'):
                customer_id = current_user.id
        except:
            pass
        
        # Save configuration to database
        config = Configuration(
            name=data['name'],
            components=json.dumps(data['components']),
            total_price=data.get('total_price', 0),
            customer_id=customer_id,
            created_at=datetime.utcnow()
        )
        
        db.session.add(config)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Konfiguration gespeichert!',
            'config_id': config.id
        })
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error saving configuration: {e}")
        return jsonify({'error': 'Fehler beim Speichern der Konfiguration'}), 500

@app.route('/api/create-checkout-session', methods=['POST'])
def create_checkout_session():
    """Create Stripe checkout session for PC configuration"""
    try:
        data = request.get_json()
        
        # Validate required data
        if not data.get('components') or not data.get('total_price'):
            return jsonify({'error': 'Komponenten und Gesamtpreis sind erforderlich'}), 400
        
        # Get domain for redirect URLs
        domain = os.environ.get('REPLIT_DEV_DOMAIN') if os.environ.get('REPLIT_DEPLOYMENT') != 'true' else os.environ.get('REPLIT_DOMAINS', '').split(',')[0]
        
        if not domain:
            return jsonify({'error': 'Domain nicht konfiguriert'}), 500
        
        # Create line items from components
        line_items = []
        
        # Add each component as a line item
        for category, component_id in data['components'].items():
            if component_id:
                # Find component details
                component = Component.query.get(component_id)
                if component:
                    line_items.append({
                        'price_data': {
                            'currency': 'eur',
                            'product_data': {
                                'name': f"{component.name} ({category.upper()})",
                                'description': f"PC-Komponente: {component.name}",
                            },
                            'unit_amount': int(component.price * 100),  # Convert to cents
                        },
                        'quantity': 1,
                    })
        
        if not line_items:
            return jsonify({'error': 'Keine gültigen Komponenten gefunden'}), 400
        
        # Get current customer if logged in
        customer_id = None
        try:
            from flask_login import current_user
            if current_user.is_authenticated and hasattr(current_user, 'id'):
                customer_id = current_user.id
        except:
            pass
        
        # Save configuration before checkout
        config_name = data.get('config_name', f"PC-Konfiguration {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        config = Configuration(
            name=config_name,
            components=json.dumps(data['components']),
            total_price=data['total_price'],
            customer_id=customer_id,
            created_at=datetime.utcnow()
        )
        
        db.session.add(config)
        db.session.commit()
        
        # Create anonymous customer for checkout (no name required)
        customer = None
        customer_email = data.get('customer_email')
        
        if customer_email:
            # Find existing customer by email or create new one without name requirement
            customer = Customer.query.filter_by(email=customer_email).first()
            if not customer:
                customer = Customer(
                    email=customer_email,
                    created_at=datetime.utcnow()
                )
                db.session.add(customer)
                db.session.commit()
        
        # Create order
        order_number = f"ORD-{datetime.now().strftime('%Y%m%d')}-{config.id:04d}"
        order = Order(
            customer_id=customer.id if customer else None,
            order_number=order_number,
            order_type='custom',
            total_amount=data['total_price'],
            status='pending',
            payment_status='pending',
            created_at=datetime.utcnow()
        )
        db.session.add(order)
        db.session.commit()
        
        # Create order items
        for category, component_id in data['components'].items():
            if component_id:
                component = Component.query.get(component_id)
                if component:
                    order_item = OrderItem(
                        order_id=order.id,
                        item_type='component',
                        item_id=component.id,
                        item_name=component.name,
                        quantity=1,
                        unit_price=component.price,
                        total_price=component.price
                    )
                    db.session.add(order_item)
        
        db.session.commit()
        
        # Create Stripe checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=f'https://{domain}/checkout/success?session_id={{CHECKOUT_SESSION_ID}}&order_id={order.id}',
            cancel_url=f'https://{domain}/checkout/cancel?order_id={order.id}',
            metadata={
                'order_id': str(order.id),
                'order_number': order_number,
                'config_id': str(config.id)
            }
        )
        
        # Update order with Stripe session ID
        order.stripe_session_id = checkout_session.id
        db.session.commit()
        
        return jsonify({
            'success': True,
            'checkout_url': checkout_session.url,
            'session_id': checkout_session.id,
            'order_id': order.id,
            'order_number': order_number
        })
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating checkout session: {e}")
        return jsonify({'error': f'Fehler beim Erstellen der Checkout-Session: {str(e)}'}), 500

@app.route('/checkout/success')
def checkout_success():
    """Handle successful checkout"""
    session_id = request.args.get('session_id')
    order_id = request.args.get('order_id')
    config_id = request.args.get('config_id')
    
    try:
        # Retrieve the checkout session from Stripe
        checkout_session = stripe.checkout.Session.retrieve(session_id)
        
        # Get order - try multiple methods
        order = None
        if order_id:
            order = Order.query.get(order_id)
        elif checkout_session.id:
            # Try to find by stripe session ID
            order = Order.query.filter_by(stripe_session_id=checkout_session.id).first()
        elif config_id:
            # If from cart, try to find the most recent order for this config
            order = Order.query.filter_by(status='pending').order_by(Order.created_at.desc()).first()
        
        if order and checkout_session.payment_status == 'paid':
            # Update order status
            order.payment_status = 'paid'
            order.status = 'processing'
            order.updated_at = datetime.utcnow()
            
            # Create invoice
            invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-{order.id:04d}"
            invoice = Invoice(
                order_id=order.id,
                invoice_number=invoice_number,
                issue_date=datetime.utcnow(),
                due_date=datetime.utcnow(),  # Immediate due date for paid orders
                total_amount=order.total_amount,
                tax_amount=order.total_amount * 0.19,  # 19% German VAT
                status='paid'
            )
            db.session.add(invoice)
            db.session.commit()
            
            # Send order confirmation email
            try:
                from email_service import send_order_confirmation_email, EmailService
                send_order_confirmation_email(order)
            except Exception as e:
                logging.error(f"Fehler beim Senden der Bestellbestätigung: {e}")
        
        return render_template('checkout_success.html', 
                             session=checkout_session,
                             order=order)
        
    except Exception as e:
        logging.error(f"Error handling checkout success: {e}")
        return render_template('checkout_error.html', 
                             error="Fehler beim Abrufen der Bestelldetails")

@app.route('/checkout/cancel')
def checkout_cancel():
    """Handle cancelled checkout"""
    order_id = request.args.get('order_id')
    order = Order.query.get(order_id) if order_id else None
    
    if order:
        # Update order status to cancelled
        order.status = 'cancelled'
        order.payment_status = 'failed'
        order.updated_at = datetime.utcnow()
        db.session.commit()
    
    return render_template('checkout_cancel.html', order=order)

# Stripe Webhook Handler
@app.route('/webhook/stripe', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook events"""
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        # Verify webhook signature (in production, use webhook secret)
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.environ.get('STRIPE_WEBHOOK_SECRET', '')
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return '', 400
    
    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        # Find order by Stripe session ID
        order = Order.query.filter_by(stripe_session_id=session['id']).first()
        
        if order:
            # Update order status
            order.payment_status = 'paid'
            order.status = 'processing'
            order.updated_at = datetime.utcnow()
            
            # Create invoice if not exists
            existing_invoice = Invoice.query.filter_by(order_id=order.id).first()
            if not existing_invoice:
                invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-{order.id:04d}"
                invoice = Invoice(
                    order_id=order.id,
                    invoice_number=invoice_number,
                    issue_date=datetime.utcnow(),
                    due_date=datetime.utcnow(),
                    total_amount=order.total_amount,
                    tax_amount=order.total_amount * 0.19,  # 19% German VAT
                    status='paid'
                )
                db.session.add(invoice)
            
            db.session.commit()
    
    elif event['type'] == 'checkout.session.expired':
        session = event['data']['object']
        
        # Find order by Stripe session ID
        order = Order.query.filter_by(stripe_session_id=session['id']).first()
        
        if order:
            # Update order status to cancelled
            order.status = 'cancelled'
            order.payment_status = 'failed'
            order.updated_at = datetime.utcnow()
            db.session.commit()
    
    return '', 200


# Legal pages
@app.route('/widerrufsrecht')
def widerrufsrecht():
    """Widerrufsrecht page"""
    return render_template('legal/widerrufsrecht.html')

@app.route('/agb')
def agb():
    """AGB page"""
    return render_template('legal/agb.html')

@app.route('/datenschutz')
def datenschutz():
    """Datenschutzerklärung page"""
    return render_template('legal/datenschutz.html')

@app.route('/zahlungsmethoden')
def zahlungsmethoden():
    """Zahlungsmethoden page"""
    return render_template('legal/zahlungsmethoden.html')

@app.route('/test-email')
def test_email():
    """Test E-Mail-System mit verschiedenen Konfigurationen"""
    try:
        from email_service import EmailService
        email_service = EmailService()
        
        # Netzwerk-Tests
        import socket
        test_results = []
        
        # Test 1: DNS-Auflösung
        try:
            import socket
            ip = socket.gethostbyname('mail.bytedohm.de')
            test_results.append(f"✅ DNS: mail.bytedohm.de → {ip}")
        except Exception as e:
            test_results.append(f"❌ DNS-Fehler: {e}")
            
        # Test 2: Port 465 Verbindung
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex(('mail.bytedohm.de', 465))
            sock.close()
            if result == 0:
                test_results.append("✅ Port 465: Verbindung erfolgreich")
            else:
                test_results.append(f"❌ Port 465: Verbindung fehlgeschlagen ({result})")
        except Exception as e:
            test_results.append(f"❌ Port 465 Test-Fehler: {e}")
            
        # Test 3: Port 587 Verbindung
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex(('mail.bytedohm.de', 587))
            sock.close()
            if result == 0:
                test_results.append("✅ Port 587: Verbindung erfolgreich")
            else:
                test_results.append(f"❌ Port 587: Verbindung fehlgeschlagen ({result})")
        except Exception as e:
            test_results.append(f"❌ Port 587 Test-Fehler: {e}")
        
        test_output = "<br>".join(test_results)
        
        # E-Mail-Versand mit Port 587 testen
        test_email = "info@bytedohm.de"
        subject = "ByteDohm E-Mail Test"
        html_body = """
        <html>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f8f9fa;">
            <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px;">
                <h2 style="color: #0d6efd; text-align: center;">ByteDohm E-Mail Test</h2>
                <p>Dies ist eine Test-E-Mail vom ByteDohm E-Mail-System.</p>
                <p>Wenn Sie diese E-Mail erhalten, funktioniert das System korrekt.</p>
                <hr style="margin: 20px 0;">
                <small style="color: #666;">ByteDohm.de - Ihr PC-Konfigurator</small>
            </div>
        </body>
        </html>
        """
        
        text_body = """
        ByteDohm E-Mail Test
        
        Dies ist eine Test-E-Mail vom ByteDohm E-Mail-System.
        Wenn Sie diese E-Mail erhalten, funktioniert das System korrekt.
        
        ByteDohm.de - Ihr PC-Konfigurator
        """
        
        # E-Mail senden mit Fehlerbehandlung
        try:
            success = email_service._send_email(test_email, subject, html_body, text_body)
        except Exception as email_error:
            print(f"E-Mail-Fehler: {email_error}")
            success = False
        
        if success:
            return f"""
            <div style="font-family: Arial, sans-serif; max-width: 800px; margin: 20px auto; padding: 20px;">
                <h2>✅ E-Mail-Test ERFOLGREICH!</h2>
                <p>Test-E-Mail wurde an {test_email} gesendet.</p>
                
                <h3>🔍 Netzwerk-Diagnose:</h3>
                <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0;">
                    {test_output}
                </div>
                
                <p><a href="/" style="color: #0d6efd;">Zurück zur Startseite</a></p>
            </div>
            """
        else:
            return f"""
            <div style="font-family: Arial, sans-serif; max-width: 800px; margin: 20px auto; padding: 20px;">
                <h2>❌ E-Mail-Test FEHLGESCHLAGEN!</h2>
                <p>Test-E-Mail konnte nicht an {test_email} gesendet werden.</p>
                
                <h3>🔍 Netzwerk-Diagnose:</h3>
                <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0;">
                    {test_output}
                </div>
                
                <h3>💡 Mögliche Lösungen:</h3>
                <ul>
                    <li>Überprüfen Sie die SMTP-Konfiguration in den Umgebungsvariablen</li>
                    <li>Stellen Sie sicher, dass mail.mailthree24.de erreichbar ist</li>
                    <li>Testen Sie Port 587 statt 465 (bereits konfiguriert)</li>
                    <li>Kontaktieren Sie den E-Mail-Provider für Firewall-Einstellungen</li>
                </ul>
                
                <p><a href="/" style="color: #0d6efd;">Zurück zur Startseite</a></p>
            </div>
            """
            
    except Exception as e:
        return f"""
        <h2>❌ E-Mail-Test FEHLER!</h2>
        <p>Fehler: {str(e)}</p>
        <p><a href="/">Zurück zur Startseite</a></p>
        """

@app.route('/warenkorb')
def cart():
    """Shopping cart page"""
    return render_template('cart.html')

@app.route('/api/check-auth-status', methods=['GET'])
def check_auth_status():
    """Check if user is authenticated"""
    try:
        # Check customer authentication
        from customer.auth import validate_customer_session
        customer = validate_customer_session()
        
        if customer:
            return jsonify({
                'is_authenticated': True,
                'user_type': 'customer',
                'user_id': customer.id,
                'user_name': customer.get_full_name() or customer.email
            })
        
        # Check admin authentication
        try:
            from flask_login import current_user
            if current_user.is_authenticated and hasattr(current_user, 'username'):
                return jsonify({
                    'is_authenticated': True,
                    'user_type': 'admin',
                    'user_id': current_user.id,
                    'user_name': current_user.username
                })
        except:
            pass
        
        return jsonify({
            'is_authenticated': False,
            'user_type': None,
            'user_id': None,
            'user_name': None
        })
        
    except Exception as e:
        logging.error(f"Error checking auth status: {e}")
        return jsonify({
            'is_authenticated': False,
            'error': 'Fehler beim Überprüfen des Anmeldestatus'
        }), 500

@app.route('/api/create-checkout-session-from-cart', methods=['POST'])
def create_checkout_session_from_cart():
    """Create Stripe checkout session from cart items"""
    try:
        # Check authentication first
        from customer.auth import validate_customer_session
        customer = validate_customer_session()
        
        if not customer:
            return jsonify({'error': 'Sie müssen sich anmelden, um eine Bestellung aufzugeben'}), 401
        
        data = request.get_json()
        
        # Validate required data
        if not data.get('cart_items') or not data.get('total_price'):
            return jsonify({'error': 'Warenkorb-Daten und Gesamtpreis sind erforderlich'}), 400
        
        # Get domain for redirect URLs
        domain = os.environ.get('REPLIT_DEV_DOMAIN') if os.environ.get('REPLIT_DEPLOYMENT') != 'true' else os.environ.get('REPLIT_DOMAINS', '').split(',')[0]
        
        if not domain:
            return jsonify({'error': 'Domain nicht konfiguriert'}), 500
        
        # Create line items from cart
        line_items = []
        
        # Load components to get details
        components = load_components()
        
        for cart_item in data['cart_items']:
            quantity = cart_item.get('quantity', 1)
            
            if cart_item.get('type') == 'prebuilt':
                # Handle prebuilt PC
                prebuilt_id = cart_item['prebuiltId']
                prebuilt_name = cart_item['name']
                prebuilt_price = cart_item['price']
                
                line_items.append({
                    'price_data': {
                        'currency': 'eur',
                        'product_data': {
                            'name': f"{prebuilt_name} (FERTIG-PC)",
                            'description': f"Fertig-PC: {prebuilt_name}",
                        },
                        'unit_amount': int(prebuilt_price * 100),  # Convert to cents
                    },
                    'quantity': quantity,
                })
            else:
                # Handle component
                component_id = cart_item['componentId']
                category = cart_item['category']
                
                # Find component in loaded data
                if category in components:
                    component = next((comp for comp in components[category] if comp['id'] == component_id), None)
                    if component:
                        line_items.append({
                            'price_data': {
                                'currency': 'eur',
                                'product_data': {
                                    'name': f"{component['name']} ({category.upper()})",
                                    'description': f"PC-Komponente: {component['name']}",
                                },
                                'unit_amount': int(component['price'] * 100),  # Convert to cents
                            },
                            'quantity': quantity,
                        })
        
        if not line_items:
            return jsonify({'error': 'Keine gültigen Komponenten im Warenkorb gefunden'}), 400
        
        # Convert cart items to configuration format for saving
        config_components = {}
        config_prebuilts = []
        
        for cart_item in data['cart_items']:
            if cart_item.get('type') == 'prebuilt':
                # Store prebuilt PC info
                config_prebuilts.append({
                    'id': cart_item['prebuiltId'],
                    'name': cart_item['name'],
                    'quantity': cart_item.get('quantity', 1)
                })
            else:
                # Store component info
                category_key = cart_item['category'].rstrip('s')  # Remove 's' from category
                config_components[category_key] = cart_item['componentId']
        
        # Create combined configuration data
        config_data = {
            'components': config_components,
            'prebuilts': config_prebuilts
        }
        
        # Use authenticated customer
        customer_id = customer.id
        
        # Save configuration before checkout
        config_name = data.get('config_name', f"PC-Bestellung {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        config = Configuration(
            name=config_name,
            components=json.dumps(config_data),
            total_price=data['total_price'],
            customer_id=customer_id,
            created_at=datetime.utcnow()
        )
        
        db.session.add(config)
        db.session.commit()
        
        # Create order
        order_number = f"ORD-{datetime.now().strftime('%Y%m%d')}-{config.id:04d}"
        order = Order(
            customer_id=customer_id,
            order_number=order_number,
            order_type='mixed',  # Can contain both components and prebuilts
            total_amount=data['total_price'],
            status='pending',
            payment_status='pending',
            created_at=datetime.utcnow()
        )
        db.session.add(order)
        db.session.commit()
        
        # Create order items
        for cart_item in data['cart_items']:
            quantity = cart_item.get('quantity', 1)
            
            if cart_item.get('type') == 'prebuilt':
                # Add prebuilt PC as order item
                prebuilt_id = cart_item['prebuiltId']
                prebuilt_name = cart_item['name']
                prebuilt_price = cart_item['price']
                
                order_item = OrderItem(
                    order_id=order.id,
                    item_type='prebuilt',
                    item_id=prebuilt_id,
                    item_name=prebuilt_name,
                    quantity=quantity,
                    unit_price=prebuilt_price,
                    total_price=prebuilt_price * quantity
                )
                db.session.add(order_item)
            else:
                # Add component as order item
                component_id = cart_item['componentId']
                category = cart_item['category']
                
                # Find component in loaded data to get details
                if category in components:
                    component = next((comp for comp in components[category] if comp['id'] == component_id), None)
                    if component:
                        order_item = OrderItem(
                            order_id=order.id,
                            item_type='component',
                            item_id=component_id,
                            item_name=component['name'],
                            quantity=quantity,
                            unit_price=component['price'],
                            total_price=component['price'] * quantity
                        )
                        db.session.add(order_item)
        
        db.session.commit()
        
        # Create Stripe checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=f'https://{domain}/checkout/success?session_id={{CHECKOUT_SESSION_ID}}&order_id={order.id}&config_id={config.id}',
            cancel_url=f'https://{domain}/warenkorb',
            metadata={
                'order_id': str(order.id),
                'order_number': order_number,
                'config_id': str(config.id),
                'config_name': config_name,
                'source': 'cart'
            }
        )
        
        # Update order with Stripe session ID
        order.stripe_session_id = checkout_session.id
        db.session.commit()
        
        return jsonify({
            'success': True,
            'checkout_url': checkout_session.url,
            'session_id': checkout_session.id,
            'order_id': order.id,
            'order_number': order_number
        })
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating checkout session from cart: {e}")
        return jsonify({'error': f'Fehler beim Erstellen der Checkout-Session: {str(e)}'}), 500