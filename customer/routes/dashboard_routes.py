from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user
from sqlalchemy import func, desc
from app import db
from customer.auth import customer_login_required
from backend.models.models import Customer, Order, Configuration, Component, Invoice

# Create blueprint for customer dashboard
customer_dashboard = Blueprint('customer_dashboard', __name__, 
                              template_folder='../templates',
                              static_folder='../static',
                              url_prefix='/kunde')


@customer_dashboard.route('/dashboard')
@customer_login_required
def dashboard():
    """Customer dashboard overview"""
    customer = current_user
    
    # Get customer statistics
    total_orders = len(customer.orders)
    total_spent = customer.get_total_spent()
    recent_orders = customer.get_recent_orders(limit=5)
    
    # Get customer configurations
    recent_configs = Configuration.query.filter_by(
        customer_id=customer.id
    ).order_by(desc(Configuration.created_at)).limit(5).all()
    
    # Order status counts
    order_status_counts = {}
    for order in customer.orders:
        status = order.status
        order_status_counts[status] = order_status_counts.get(status, 0) + 1
    
    stats = {
        'total_orders': total_orders,
        'total_spent': total_spent,
        'recent_orders': recent_orders,
        'recent_configs': recent_configs,
        'order_status_counts': order_status_counts
    }
    
    return render_template('customer/dashboard/overview.html', stats=stats)


@customer_dashboard.route('/bestellungen')
@customer_login_required
def orders():
    """Customer orders page"""
    customer = current_user
    
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Get orders with pagination
    orders = Order.query.filter_by(customer_id=customer.id).order_by(
        desc(Order.created_at)
    ).paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    return render_template('customer/dashboard/orders.html', orders=orders)


@customer_dashboard.route('/bestellung/<int:order_id>')
@customer_login_required
def order_detail(order_id):
    """Customer order detail page"""
    customer = current_user
    
    order = Order.query.filter_by(
        id=order_id, 
        customer_id=customer.id
    ).first_or_404()
    
    return render_template('customer/dashboard/order_detail.html', order=order)


@customer_dashboard.route('/konfigurationen')
@customer_login_required
def configurations():
    """Customer configurations page"""
    customer = current_user
    
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Get configurations with pagination
    configs = Configuration.query.filter_by(
        customer_id=customer.id
    ).order_by(desc(Configuration.created_at)).paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    return render_template('customer/dashboard/configurations.html', configs=configs)


@customer_dashboard.route('/api/configuration/<int:config_id>')
@customer_login_required
def get_configuration_api(config_id):
    """API endpoint to get configuration data with component details"""
    customer = current_user
    
    # Get configuration that belongs to the customer
    config = Configuration.query.filter_by(
        id=config_id, 
        customer_id=customer.id
    ).first()
    
    if not config:
        return jsonify({'success': False, 'error': 'Konfiguration nicht gefunden'}), 404
    
    try:
        # Parse components from JSON
        import json
        components_data = json.loads(config.components)
        
        # Fetch component details for each category
        enriched_components = {}
        
        for category, component_id in components_data.items():
            if component_id:
                # Get component from database
                component = Component.query.filter_by(
                    id=component_id,
                    category=category + 's' if category != 'ram' else 'ram'
                ).first()
                
                if component:
                    enriched_components[category] = {
                        'id': component.id,
                        'name': component.name,
                        'price': component.price,
                        'category': component.category
                    }
        
        return jsonify({
            'success': True,
            'configuration': {
                'id': config.id,
                'name': config.name,
                'total_price': config.total_price,
                'components': enriched_components,
                'created_at': config.created_at.isoformat()
            }
        })
        
    except Exception as e:
        print(f"Error loading configuration {config_id}: {e}")
        return jsonify({'success': False, 'error': 'Fehler beim Laden der Konfiguration'}), 500


@customer_dashboard.route('/profil', methods=['GET', 'POST'])
@customer_login_required
def profile():
    """Customer profile page"""
    customer = current_user
    
    if request.method == 'POST':
        try:
            print(f"Debug - Form data received: {dict(request.form)}")
            
            # Update customer profile
            customer.first_name = request.form.get('first_name', '').strip()
            customer.last_name = request.form.get('last_name', '').strip()
            customer.phone = request.form.get('phone', '').strip()
            
            # Update separate address fields
            customer.street = request.form.get('street', '').strip()
            customer.house_number = request.form.get('house_number', '').strip()
            customer.postal_code = request.form.get('postal_code', '').strip()
            customer.city = request.form.get('city', '').strip()
            customer.country = request.form.get('country', 'Deutschland').strip()
            
            print(f"Debug - Address fields: street={customer.street}, house_number={customer.house_number}, postal_code={customer.postal_code}, city={customer.city}, country={customer.country}")
            
            # Update newsletter subscription
            customer.newsletter_subscription = 'newsletter' in request.form
            
            # Update combined address field for compatibility
            if customer.street or customer.house_number or customer.postal_code or customer.city:
                address_parts = []
                if customer.street:
                    street_part = customer.street
                    if customer.house_number:
                        street_part += f" {customer.house_number}"
                    address_parts.append(street_part)
                if customer.postal_code or customer.city:
                    city_part = ""
                    if customer.postal_code:
                        city_part += customer.postal_code
                    if customer.city:
                        if city_part:
                            city_part += f" {customer.city}"
                        else:
                            city_part = customer.city
                    if city_part:
                        address_parts.append(city_part)
                if customer.country and customer.country != 'Deutschland':
                    address_parts.append(customer.country)
                customer.address = ", ".join(address_parts)
                print(f"Debug - Combined address: {customer.address}")
            else:
                customer.address = ""
            
            # Verify customer has required attributes
            print(f"Debug - Customer before save: id={customer.id}, email={customer.email}")
            
            db.session.add(customer)  # Ensure customer is in session
            db.session.commit()
            
            print(f"Debug - Profile saved successfully for customer {customer.id}")
            flash('Profil erfolgreich aktualisiert.', 'success')
            return redirect(url_for('customer_dashboard.profile'))
        except Exception as e:
            db.session.rollback()
            print(f"Error updating profile: {e}")
            import traceback
            traceback.print_exc()
            flash(f'Fehler beim Aktualisieren des Profils: {str(e)}', 'error')
    
    return render_template('customer/dashboard/profile.html', customer=customer)


@customer_dashboard.route('/passwort-aendern', methods=['GET', 'POST'])
@customer_login_required
def change_password():
    """Change customer password"""
    customer = current_user
    
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        if not customer.check_password(current_password):
            flash('Aktuelles Passwort ist falsch.', 'error')
        elif new_password != confirm_password:
            flash('Neue Passwörter stimmen nicht überein.', 'error')
        elif len(new_password) < 8:
            flash('Neues Passwort muss mindestens 8 Zeichen lang sein.', 'error')
        else:
            try:
                customer.set_password(new_password)
                db.session.commit()
                flash('Passwort erfolgreich geändert.', 'success')
                return redirect(url_for('customer_dashboard.profile'))
            except Exception as e:
                db.session.rollback()
                flash('Fehler beim Ändern des Passworts.', 'error')
    
    return render_template('customer/dashboard/change_password.html')


@customer_dashboard.route('/rechnungen')
@customer_login_required  
def invoices():
    """Customer invoices page"""
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Get invoices for customer's orders with pagination
    invoices = db.session.query(Invoice).join(Order).filter(
        Order.customer_id == current_user.id
    ).order_by(Invoice.issue_date.desc()).paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    return render_template('customer/dashboard/invoices.html', invoices=invoices)


@customer_dashboard.route('/rechnung/<int:invoice_id>')
@customer_login_required
def invoice_detail(invoice_id):
    """Customer invoice detail page"""
    # Ensure invoice belongs to current customer
    invoice = db.session.query(Invoice).join(Order).filter(
        Invoice.id == invoice_id,
        Order.customer_id == current_user.id
    ).first_or_404()
    
    return render_template('customer/dashboard/invoice_detail.html', invoice=invoice)


@customer_dashboard.route('/api/quick-stats')
@customer_login_required
def api_quick_stats():
    """API endpoint for quick customer statistics"""
    customer = current_user
    
    stats = {
        'total_orders': len(customer.orders),
        'total_spent': float(customer.get_total_spent()),
        'pending_orders': len([o for o in customer.orders if o.status == 'pending']),
        'completed_orders': len([o for o in customer.orders if o.status == 'delivered'])
    }
    
    return jsonify(stats)


@customer_dashboard.route('/einstellungen')
@customer_login_required
def settings():
    """Customer account settings"""
    customer = current_user
    
    return render_template('customer/dashboard/settings.html', customer=customer)


@customer_dashboard.route('/konto-loeschen', methods=['GET', 'POST'])
@customer_login_required
def delete_account():
    """Delete customer account - placeholder for future implementation"""
    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm_deletion = request.form.get('confirm_deletion')
        
        if not current_user.check_password(password):
            flash('Falsches Passwort.', 'error')
        elif not confirm_deletion:
            flash('Bitte bestätigen Sie die Löschung.', 'error')
        else:
            # TODO: Implement account deletion logic
            flash('Kontolöschung ist derzeit nicht verfügbar. Bitte kontaktieren Sie den Support.', 'info')
    
    return render_template('customer/dashboard/delete_account.html')