from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user
from sqlalchemy import func, desc
from app import db
from customer.auth import customer_login_required
from models import Customer, Order, Configuration, Component

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


@customer_dashboard.route('/profil', methods=['GET', 'POST'])
@customer_login_required
def profile():
    """Customer profile page"""
    customer = current_user
    
    if request.method == 'POST':
        # Update profile information
        customer.first_name = request.form.get('first_name', '').strip()
        customer.last_name = request.form.get('last_name', '').strip()
        customer.phone = request.form.get('phone', '').strip() or None
        
        # Address information
        customer.street = request.form.get('street', '').strip() or None
        customer.house_number = request.form.get('house_number', '').strip() or None
        customer.postal_code = request.form.get('postal_code', '').strip() or None
        customer.city = request.form.get('city', '').strip() or None
        customer.country = request.form.get('country', 'Deutschland').strip()
        
        # Newsletter subscription
        customer.newsletter_subscription = bool(request.form.get('newsletter'))
        
        try:
            db.session.commit()
            flash('Profil erfolgreich aktualisiert.', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Fehler beim Aktualisieren des Profils.', 'error')
    
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