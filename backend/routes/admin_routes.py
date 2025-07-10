import json
from datetime import datetime
from flask import request, render_template, redirect, url_for, flash, session, jsonify
from flask_login import login_required, login_user, logout_user, UserMixin, current_user
from werkzeug.security import check_password_hash
from app import app, db
from backend.models.models import Component, PrebuiltPC, AdminUser, Order, OrderItem, Customer, Invoice
from backend.services.dhl_integration import create_shipping_label_for_order, track_order_shipment
from backend.services.email_service import send_registration_email, EmailService, send_newsletter_email

# Admin Authentication
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = AdminUser.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Erfolgreich angemeldet', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Ungültige Anmeldedaten', 'error')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
@login_required
def admin_logout():
    """Admin logout"""
    logout_user()
    flash('Erfolgreich abgemeldet', 'info')
    return redirect(url_for('admin_login'))

# Dashboard
@app.route('/admin')
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    """Admin dashboard with overview statistics"""
    from sqlalchemy import func
    
    # Component and prebuilt stats
    component_count = Component.query.count()
    active_component_count = Component.query.filter_by(is_active=True).count()
    prebuilt_count = PrebuiltPC.query.count()
    active_prebuilt_count = PrebuiltPC.query.filter_by(is_active=True).count()
    
    # Order and customer stats
    total_orders = Order.query.count()
    pending_orders = Order.query.filter_by(status='pending').count()
    processing_orders = Order.query.filter_by(status='processing').count()
    completed_orders = Order.query.filter_by(status='delivered').count()
    total_customers = Customer.query.count()
    
    # Revenue stats
    total_revenue = db.session.query(func.sum(Order.total_amount)).filter_by(payment_status='paid').scalar() or 0
    pending_revenue = db.session.query(func.sum(Order.total_amount)).filter_by(payment_status='pending').scalar() or 0
    
    # Invoice stats
    total_invoices = Invoice.query.count()
    paid_invoices = Invoice.query.filter_by(status='paid').count()
    overdue_invoices = Invoice.query.filter_by(status='overdue').count()
    
    # Recent data
    recent_components = Component.query.order_by(Component.created_at.desc()).limit(5).all()
    recent_prebuilts = PrebuiltPC.query.order_by(PrebuiltPC.created_at.desc()).limit(5).all()
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    recent_invoices = Invoice.query.order_by(Invoice.issue_date.desc()).limit(5).all()
    
    stats = {
        'components': {
            'total': component_count,
            'active': active_component_count,
            'inactive': component_count - active_component_count
        },
        'prebuilts': {
            'total': prebuilt_count,
            'active': active_prebuilt_count,
            'inactive': prebuilt_count - active_prebuilt_count
        },
        'orders': {
            'total': total_orders,
            'pending': pending_orders,
            'processing': processing_orders,
            'completed': completed_orders
        },
        'customers': {
            'total': total_customers
        },
        'revenue': {
            'total': total_revenue,
            'pending': pending_revenue
        },
        'invoices': {
            'total': total_invoices,
            'paid': paid_invoices,
            'overdue': overdue_invoices
        }
    }
    
    return render_template('admin/dashboard.html', 
                         stats=stats, 
                         recent_components=recent_components,
                         recent_prebuilts=recent_prebuilts,
                         recent_orders=recent_orders,
                         recent_invoices=recent_invoices)

# Component Management
@app.route('/admin/components')
@login_required
def admin_components():
    """List all components"""
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', '')
    
    query = Component.query
    if category:
        query = query.filter_by(category=category)
    
    components = query.order_by(Component.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    categories = ['cpus', 'motherboards', 'ram', 'gpus', 'ssds', 'cases', 'psus', 'coolers']
    
    return render_template('admin/components.html', 
                         components=components, 
                         categories=categories,
                         current_category=category)

@app.route('/admin/components/add', methods=['GET', 'POST'])
@login_required
def admin_add_component():
    """Add new component"""
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            category = request.form.get('category', '').strip()
            price_str = request.form.get('price', '0')
            
            if not name or not category:
                flash('Name und Kategorie sind erforderlich', 'error')
                return render_template('admin/add_component.html')
            
            try:
                price = float(price_str)
            except ValueError:
                flash('Ungültiger Preis', 'error')
                return render_template('admin/add_component.html')
            
            # Parse specifications JSON
            specs_json = request.form.get('specifications', '{}')
            try:
                specs = json.loads(specs_json)
            except json.JSONDecodeError:
                flash('Ungültiges JSON-Format in den Spezifikationen', 'error')
                return render_template('admin/add_component.html')
            
            component = Component(
                name=name,
                category=category,
                price=price,
                specifications=json.dumps(specs)
            )
            
            db.session.add(component)
            db.session.commit()
            
            flash(f'Komponente "{name}" erfolgreich hinzugefügt', 'success')
            return redirect(url_for('admin_components'))
            
        except Exception as e:
            flash(f'Fehler beim Hinzufügen der Komponente: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('admin/add_component.html')

@app.route('/admin/components/<int:component_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit_component(component_id):
    """Edit existing component"""
    component = Component.query.get_or_404(component_id)
    
    if request.method == 'POST':
        try:
            component.name = request.form['name']
            component.category = request.form['category']
            component.price = float(request.form['price'])
            component.is_active = bool(int(request.form.get('is_active', 1)))
            
            # Parse and validate specifications JSON
            try:
                specs = json.loads(request.form['specifications'])
                component.set_specs(specs)
            except json.JSONDecodeError:
                flash('Ungültiges JSON-Format in den Spezifikationen', 'error')
                return render_template('admin/edit_component.html', component=component)
            
            db.session.commit()
            flash(f'Komponente "{component.name}" erfolgreich aktualisiert', 'success')
            return redirect(url_for('admin_components'))
            
        except Exception as e:
            flash(f'Fehler beim Aktualisieren der Komponente: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('admin/edit_component.html', component=component)

@app.route('/admin/components/<int:component_id>/delete', methods=['POST'])
@login_required 
def admin_delete_component(component_id):
    """Delete component"""
    component = Component.query.get_or_404(component_id)
    
    try:
        db.session.delete(component)
        db.session.commit()
        flash(f'Komponente "{component.name}" erfolgreich gelöscht', 'success')
    except Exception as e:
        flash(f'Fehler beim Löschen der Komponente: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('admin_components'))

# Prebuilt PC Management
@app.route('/admin/prebuilts')
@login_required
def admin_prebuilts():
    """List all prebuilt PCs"""
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', '')
    
    query = PrebuiltPC.query
    if category:
        query = query.filter_by(category=category)
    
    prebuilts = query.order_by(PrebuiltPC.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    categories = ['gaming', 'workstation', 'office', 'budget']
    
    return render_template('admin/prebuilts.html', 
                         prebuilts=prebuilts, 
                         categories=categories,
                         current_category=category)

@app.route('/admin/prebuilts/add', methods=['GET', 'POST'])
@login_required
def admin_add_prebuilt():
    """Add new prebuilt PC"""
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            category = request.form.get('category', '').strip()
            description = request.form.get('description', '').strip()
            price_str = request.form.get('price', '0')
            image_url = request.form.get('image_url', '').strip()
            
            if not name or not category or not description:
                flash('Name, Kategorie und Beschreibung sind erforderlich', 'error')
                return render_template('admin/add_prebuilt.html')
            
            try:
                price = float(price_str)
            except ValueError:
                flash('Ungültiger Preis', 'error')
                return render_template('admin/add_prebuilt.html')
            
            # Parse specifications JSON
            specs_json = request.form.get('specifications', '{}')
            try:
                specs = json.loads(specs_json)
            except json.JSONDecodeError:
                flash('Ungültiges JSON-Format in den Spezifikationen', 'error')
                return render_template('admin/add_prebuilt.html')
            
            # Parse features JSON
            features_json = request.form.get('features', '[]')
            try:
                features = json.loads(features_json)
                if not isinstance(features, list):
                    raise ValueError('Features müssen als Array definiert werden')
            except (json.JSONDecodeError, ValueError) as e:
                flash(f'Ungültiges JSON-Format in den Features: {str(e)}', 'error')
                return render_template('admin/add_prebuilt.html')
            
            prebuilt = PrebuiltPC(
                name=name,
                price=price,
                category=category,
                description=description,
                image_url=image_url if image_url else None,
                specifications=json.dumps(specs),
                features=json.dumps(features)
            )
            
            db.session.add(prebuilt)
            db.session.commit()
            
            flash(f'Fertig-PC "{name}" erfolgreich hinzugefügt', 'success')
            return redirect(url_for('admin_prebuilts'))
            
        except Exception as e:
            flash(f'Fehler beim Hinzufügen des Fertig-PCs: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('admin/add_prebuilt.html')

@app.route('/admin/prebuilts/<int:prebuilt_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit_prebuilt(prebuilt_id):
    """Edit existing prebuilt PC"""
    prebuilt = PrebuiltPC.query.get_or_404(prebuilt_id)
    
    if request.method == 'POST':
        try:
            prebuilt.name = request.form['name']
            prebuilt.price = float(request.form['price'])
            prebuilt.category = request.form['category']
            prebuilt.description = request.form['description']
            prebuilt.image_url = request.form.get('image_url') or None
            prebuilt.is_active = bool(int(request.form.get('is_active', 1)))
            
            # Parse and validate specifications JSON
            try:
                specs = json.loads(request.form['specifications'])
                prebuilt.set_specs(specs)
            except json.JSONDecodeError:
                flash('Ungültiges JSON-Format in den Spezifikationen', 'error')
                return render_template('admin/edit_prebuilt.html', prebuilt=prebuilt)
            
            # Parse and validate features JSON
            try:
                features = json.loads(request.form['features'])
                if not isinstance(features, list):
                    raise ValueError('Features müssen als Array definiert werden')
                prebuilt.set_features(features)
            except (json.JSONDecodeError, ValueError) as e:
                flash(f'Ungültiges JSON-Format in den Features: {str(e)}', 'error')
                return render_template('admin/edit_prebuilt.html', prebuilt=prebuilt)
            
            db.session.commit()
            
            flash(f'Fertig-PC "{prebuilt.name}" erfolgreich aktualisiert', 'success')
            return redirect(url_for('admin_prebuilts'))
            
        except Exception as e:
            flash(f'Fehler beim Aktualisieren des Fertig-PCs: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('admin/edit_prebuilt.html', prebuilt=prebuilt)

@app.route('/admin/prebuilts/<int:prebuilt_id>/delete', methods=['POST'])
@login_required
def admin_delete_prebuilt(prebuilt_id):
    """Delete prebuilt PC"""
    prebuilt = PrebuiltPC.query.get_or_404(prebuilt_id)
    
    try:
        db.session.delete(prebuilt)
        db.session.commit()
        flash(f'Fertig-PC "{prebuilt.name}" erfolgreich gelöscht', 'success')
    except Exception as e:
        flash(f'Fehler beim Löschen des Fertig-PCs: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('admin_prebuilts'))

# API endpoints for dynamic forms
@app.route('/admin/api/component-fields/<category>')
@login_required
def get_component_fields(category):
    """Get form fields for specific component category"""
    fields = {
        'cpus': ['socket', 'cores', 'threads', 'base_clock', 'boost_clock', 'tdp', 'memory_support'],
        'motherboards': ['socket', 'chipset', 'form_factor', 'memory_slots', 'max_memory', 'memory_type'],
        'ram': ['type', 'capacity', 'speed', 'timings', 'voltage'],
        'gpus': ['memory', 'memory_type', 'core_clock', 'boost_clock', 'power_consumption', 'length'],
        'ssds': ['capacity', 'interface', 'form_factor', 'read_speed', 'write_speed'],
        'cases': ['form_factor', 'max_gpu_length', 'max_cpu_cooler_height', 'front_usb'],
        'psus': ['wattage', 'efficiency', 'modular', 'form_factor'],
        'coolers': ['type', 'height', 'compatible_sockets', 'tdp_rating']
    }
    
    return {'fields': fields.get(category, [])}

# Order Management
@app.route('/admin/orders')
@login_required
def admin_orders():
    """List all orders"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    payment_status = request.args.get('payment_status', '')
    
    query = Order.query
    if status:
        query = query.filter_by(status=status)
    if payment_status:
        query = query.filter_by(payment_status=payment_status)
    
    orders = query.order_by(Order.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/orders.html', 
                         orders=orders, 
                         current_status=status,
                         current_payment_status=payment_status)

@app.route('/admin/orders/<int:order_id>')
@login_required
def admin_order_detail(order_id):
    """View order details"""
    order = Order.query.get_or_404(order_id)
    return render_template('admin/order_detail.html', order=order)

@app.route('/admin/orders/<int:order_id>/create-shipping-label', methods=['POST'])
@login_required
def admin_create_shipping_label(order_id):
    """Erstelle DHL Versandetikett für Bestellung"""
    import logging
    logging.info(f"Starting DHL shipping label creation for order {order_id}")
    
    try:
        result = create_shipping_label_for_order(order_id)
        logging.info(f"DHL API Result: {result}")
        
        if result['success']:
            # Update order with shipping info
            order = Order.query.get(order_id)
            order.tracking_number = result['tracking_number']
            order.shipping_label_url = result.get('label_url')
            
            # Prüfe ob echte API-Verbindung oder Portal-Anweisungen
            if 'portal_instructions' in result:
                # Portal-Anweisungen - Status bleibt auf 'processing'
                order.status = 'processing'
                flash(f'DHL Portal-Anweisungen erstellt! Temp. Tracking: {result["tracking_number"]}', 'info')
                flash('Hinweis: Für echte Versandmarken muss der DHL API-Zugang freigeschaltet werden.', 'warning')
            else:
                # Echte API-Verbindung - Status auf 'shipped'
                order.status = 'shipped'
                flash(f'Versandetikett erfolgreich erstellt! Tracking: {result["tracking_number"]}', 'success')
            
            order.updated_at = datetime.utcnow()
            db.session.commit()
            logging.info(f"Successfully created DHL label for order {order_id}: {result['tracking_number']}")
        else:
            flash(f'Fehler beim Erstellen des Versandetiketts: {result["error"]}', 'error')
            logging.error(f"DHL label creation failed for order {order_id}: {result['error']}")
            
    except Exception as e:
        flash(f'Unerwarteter Fehler: {str(e)}', 'error')
        logging.error(f"Exception in DHL label creation for order {order_id}: {str(e)}")
    
    return redirect(url_for('admin_order_detail', order_id=order_id))

@app.route('/admin/dhl-api-guide')
@login_required
def admin_dhl_api_guide():
    """DHL API-Freischaltung Anleitung"""
    return render_template('admin/dhl_api_guide.html')

@app.route('/admin/orders/<int:order_id>/track-shipment')
@login_required
def admin_track_shipment(order_id):
    """Verfolge DHL Sendung"""
    order = Order.query.get_or_404(order_id)
    
    if not order.tracking_number:
        flash('Keine Tracking-Nummer verfügbar', 'warning')
        return redirect(url_for('admin_order_detail', order_id=order_id))
    
    try:
        result = track_order_shipment(order.tracking_number)
        
        if result['success']:
            tracking_data = result['data']
            flash('Tracking-Informationen erfolgreich abgerufen', 'success')
        else:
            flash(f'Fehler beim Tracking: {result["error"]}', 'error')
            
    except Exception as e:
        flash(f'Tracking-Fehler: {str(e)}', 'error')
    
    return redirect(url_for('admin_order_detail', order_id=order_id))

@app.route('/admin/orders/<int:order_id>/update-status', methods=['POST'])
@login_required
def admin_update_order_status(order_id):
    """Update order status"""
    order = Order.query.get_or_404(order_id)
    
    # Aktuelle Status speichern für E-Mail
    old_status = order.status
    old_payment_status = order.payment_status
    
    new_status = request.form.get('status')
    payment_status = request.form.get('payment_status')
    
    status_changed = False
    payment_changed = False
    
    if new_status and new_status in ['pending', 'processing', 'shipped', 'delivered', 'cancelled']:
        if new_status != old_status:
            order.status = new_status
            status_changed = True
        
    if payment_status and payment_status in ['pending', 'paid', 'failed', 'refunded']:
        if payment_status != old_payment_status:
            order.payment_status = payment_status
            payment_changed = True
    
    try:
        db.session.commit()
        
        # E-Mail-Benachrichtigung bei Status-Änderung
        if status_changed:
            try:
                from email_service import send_status_update_email
                
                # Bei "shipped" Status auch Versandbenachrichtigung senden (falls Tracking-Nummer vorhanden)
                if new_status == 'shipped' and order.tracking_number:
                    from email_service import send_shipping_notification_email
                    success = send_shipping_notification_email(order)
                    if success:
                        flash(f'Bestellung {order.order_number} als versandt markiert - Versandbenachrichtigung mit Tracking-Nummer gesendet', 'success')
                    else:
                        flash(f'Bestellung {order.order_number} Status aktualisiert - Versandbenachrichtigung fehlgeschlagen', 'warning')
                else:
                    # Standard Status-Update E-Mail
                    success = send_status_update_email(order, old_status, new_status)
                    if success:
                        flash(f'Bestellung {order.order_number} Status aktualisiert - E-Mail an Kunde gesendet', 'success')
                    else:
                        flash(f'Bestellung {order.order_number} Status aktualisiert - E-Mail-Versand fehlgeschlagen', 'warning')
            except Exception as e:
                flash(f'Bestellung {order.order_number} Status aktualisiert - E-Mail-Fehler: {str(e)}', 'warning')
        else:
            flash(f'Bestellung {order.order_number} Status aktualisiert', 'success')
            
    except Exception as e:
        flash(f'Fehler beim Aktualisieren des Status: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('admin_order_detail', order_id=order_id))

# Customer Management
@app.route('/admin/customers')
@login_required
def admin_customers():
    """List all customers"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = Customer.query
    if search:
        query = query.filter(
            Customer.email.contains(search) | 
            Customer.first_name.contains(search) | 
            Customer.last_name.contains(search)
        )
    
    customers = query.order_by(Customer.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/customers.html', 
                         customers=customers, 
                         search=search)

@app.route('/admin/customers/<int:customer_id>')
@login_required
def admin_customer_detail(customer_id):
    """View customer details"""
    customer = Customer.query.get_or_404(customer_id)
    orders = Order.query.filter_by(customer_id=customer_id).order_by(Order.created_at.desc()).all()
    
    return render_template('admin/customer_detail.html', 
                         customer=customer, 
                         orders=orders)

# Invoice Management
@app.route('/admin/invoices')
@login_required
def admin_invoices():
    """List all invoices"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    
    query = Invoice.query
    if status:
        query = query.filter_by(status=status)
    
    invoices = query.order_by(Invoice.issue_date.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/invoices.html', 
                         invoices=invoices, 
                         current_status=status)

@app.route('/admin/invoices/<int:invoice_id>')
@login_required
def admin_invoice_detail(invoice_id):
    """View invoice details"""
    invoice = Invoice.query.get_or_404(invoice_id)
    return render_template('admin/invoice_detail.html', invoice=invoice)

@app.route('/admin/invoices/<int:invoice_id>/update-status', methods=['POST'])
@login_required
def admin_update_invoice_status(invoice_id):
    """Update invoice status"""
    invoice = Invoice.query.get_or_404(invoice_id)
    
    new_status = request.form.get('status')
    
    if new_status and new_status in ['draft', 'sent', 'paid', 'overdue', 'cancelled']:
        invoice.status = new_status
        
        try:
            db.session.commit()
            flash(f'Rechnung {invoice.invoice_number} Status aktualisiert', 'success')
        except Exception as e:
            flash(f'Fehler beim Aktualisieren des Status: {str(e)}', 'error')
            db.session.rollback()
    
    return redirect(url_for('admin_invoice_detail', invoice_id=invoice_id))

# Statistics and Reports
@app.route('/admin/statistics')
@login_required
def admin_statistics():
    """Advanced statistics and reports"""
    from sqlalchemy import func, extract
    from datetime import datetime, timedelta
    
    # Date range for statistics
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)
    
    # Sales statistics
    total_sales = db.session.query(func.sum(Order.total_amount)).filter_by(payment_status='paid').scalar() or 0
    monthly_sales = db.session.query(func.sum(Order.total_amount)).filter(
        Order.payment_status == 'paid',
        Order.created_at >= start_date
    ).scalar() or 0
    
    # Order statistics by status
    order_stats = db.session.query(
        Order.status,
        func.count(Order.id).label('count')
    ).group_by(Order.status).all()
    
    # Payment statistics
    payment_stats_raw = db.session.query(
        Order.payment_status,
        func.count(Order.id).label('count'),
        func.sum(Order.total_amount).label('total')
    ).group_by(Order.payment_status).all()
    
    payment_stats = []
    for stat in payment_stats_raw:
        payment_stats.append({
            'payment_status': stat.payment_status,
            'count': stat.count,
            'total': float(stat.total) if stat.total else 0.0
        })
    
    # Monthly revenue trend
    monthly_revenue_raw = db.session.query(
        extract('month', Order.created_at).label('month'),
        func.sum(Order.total_amount).label('revenue')
    ).filter(
        Order.payment_status == 'paid',
        Order.created_at >= start_date
    ).group_by(extract('month', Order.created_at)).all()
    
    monthly_revenue = []
    for revenue in monthly_revenue_raw:
        monthly_revenue.append({
            'month': int(revenue.month),
            'revenue': float(revenue.revenue) if revenue.revenue else 0.0
        })
    
    # Top customers
    top_customers_raw = db.session.query(
        Customer.email,
        Customer.first_name,
        Customer.last_name,
        func.count(Order.id).label('order_count'),
        func.sum(Order.total_amount).label('total_spent')
    ).join(Order).filter(
        Order.payment_status == 'paid'
    ).group_by(Customer.id).order_by(func.sum(Order.total_amount).desc()).limit(10).all()
    
    top_customers = []
    for customer in top_customers_raw:
        top_customers.append({
            'email': customer.email,
            'first_name': customer.first_name,
            'last_name': customer.last_name,
            'order_count': customer.order_count,
            'total_spent': float(customer.total_spent) if customer.total_spent else 0.0
        })
    
    # Popular PCs statistics
    popular_pcs_raw = db.session.query(
        OrderItem.item_name,
        func.count(OrderItem.id).label('order_count'),
        func.sum(OrderItem.total_price).label('total_revenue')
    ).filter(
        OrderItem.item_type == 'prebuilt'
    ).group_by(OrderItem.item_name).order_by(func.count(OrderItem.id).desc()).limit(10).all()
    
    popular_pcs = []
    for pc in popular_pcs_raw:
        popular_pcs.append({
            'item_name': pc.item_name,
            'order_count': pc.order_count,
            'total_revenue': float(pc.total_revenue) if pc.total_revenue else 0.0
        })
    
    stats = {
        'total_sales': float(total_sales) if total_sales else 0.0,
        'monthly_sales': float(monthly_sales) if monthly_sales else 0.0,
        'order_stats': dict(order_stats),
        'payment_stats': payment_stats,
        'monthly_revenue': monthly_revenue,
        'top_customers': top_customers,
        'popular_pcs': popular_pcs
    }
    
    return render_template('admin/statistics.html', stats=stats)

# Newsletter Management
@app.route('/admin/newsletter')
@login_required
def admin_newsletter():
    """Newsletter creation page"""
    # Anzahl der Newsletter-Abonnenten
    subscriber_count = Customer.query.filter_by(newsletter_subscription=True).count()
    return render_template('admin/newsletter.html', subscriber_count=subscriber_count)

@app.route('/admin/newsletter/preview', methods=['POST'])
@login_required
def admin_newsletter_preview():
    """Generate newsletter preview"""
    try:
        subject = request.form.get('subject', '')
        preheader = request.form.get('preheader', '')
        content = request.form.get('content', '')
        footer_text = request.form.get('footer_text', '')
        
        # Create newsletter HTML template
        preview_html = f"""
        <div style="max-width: 600px; margin: 0 auto; font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <!-- Header -->
            <div style="background-color: #2c3e50; color: white; padding: 20px; text-align: center;">
                <h1 style="margin: 0; font-size: 28px;">ByteDohm Newsletter</h1>
                {f'<p style="margin: 5px 0 0 0; color: #ecf0f1; font-size: 14px;">{preheader}</p>' if preheader else ''}
            </div>
            
            <!-- Content -->
            <div style="background-color: white; padding: 30px; border-left: 3px solid #3498db;">
                <h2 style="color: #2c3e50; margin-top: 0;">{subject}</h2>
                <div style="margin: 20px 0;">
                    {content}
                </div>
            </div>
            
            <!-- Footer -->
            <div style="background-color: #34495e; color: white; padding: 20px; text-align: center;">
                {f'<p style="margin: 0 0 10px 0;">{footer_text}</p>' if footer_text else ''}
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
        """
        
        return jsonify({
            'success': True,
            'preview_html': preview_html
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/admin/newsletter/test', methods=['POST'])
@login_required
def admin_newsletter_test():
    """Send test newsletter"""
    try:
        subject = request.form.get('subject', '')
        preheader = request.form.get('preheader', '')
        content = request.form.get('content', '')
        footer_text = request.form.get('footer_text', '')
        test_email = request.form.get('test_email', '')
        
        if not test_email:
            return jsonify({
                'success': False,
                'error': 'Test-E-Mail-Adresse ist erforderlich'
            }), 400
        
        # Create a dummy customer object for test email
        class TestCustomer:
            def __init__(self, email):
                self.email = email
                self.first_name = "Test"
                self.last_name = "Benutzer"
                self.get_full_name = lambda: "Test Benutzer"
        
        test_customer = TestCustomer(test_email)
        
        # Send test email
        email_service = EmailService()
        success = email_service.send_newsletter_email(
            test_customer, 
            f"[TEST] {subject}", 
            content,
            preheader=preheader,
            footer_text=footer_text
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Test-E-Mail erfolgreich an {test_email} gesendet'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Fehler beim Senden der Test-E-Mail'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/admin/newsletter/send', methods=['POST'])
@login_required
def admin_newsletter_send():
    """Send newsletter to all subscribers"""
    try:
        subject = request.form.get('subject', '')
        preheader = request.form.get('preheader', '')
        content = request.form.get('content', '')
        footer_text = request.form.get('footer_text', '')
        
        if not subject or not content:
            return jsonify({
                'success': False,
                'error': 'Betreff und Inhalt sind erforderlich'
            }), 400
        
        # Get all newsletter subscribers
        subscribers = Customer.query.filter_by(newsletter_subscription=True).all()
        
        if not subscribers:
            return jsonify({
                'success': False,
                'error': 'Keine Newsletter-Abonnenten gefunden'
            }), 400
        
        # Send newsletter to all subscribers
        email_service = EmailService()
        sent_count = 0
        failed_count = 0
        
        for customer in subscribers:
            try:
                success = email_service.send_newsletter_email(
                    customer, 
                    subject, 
                    content,
                    preheader=preheader,
                    footer_text=footer_text
                )
                if success:
                    sent_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                print(f"Fehler beim Senden an {customer.email}: {e}")
                failed_count += 1
        
        # Save newsletter to history (could be expanded with a Newsletter model)
        
        return jsonify({
            'success': True,
            'sent_count': sent_count,
            'failed_count': failed_count,
            'message': f'Newsletter an {sent_count} Empfänger gesendet'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/admin/newsletter/history')
@login_required
def admin_newsletter_history():
    """Get newsletter history (placeholder - could be expanded with Newsletter model)"""
    try:
        # For now, return empty history
        # In the future, you could create a Newsletter model to track sent newsletters
        return jsonify({
            'success': True,
            'newsletters': []
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500