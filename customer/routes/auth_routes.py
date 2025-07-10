from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_user, logout_user, current_user
from app import db
from backend.models.models import Customer
from customer.auth import (
    create_customer_session, 
    invalidate_customer_session,
    get_customer_ip,
    get_customer_user_agent,
    validate_password_strength,
    validate_email_format
)

# Create blueprint for customer authentication
customer_auth = Blueprint('customer_auth', __name__, 
                         template_folder='../templates',
                         static_folder='../static',
                         url_prefix='/kunde')


@customer_auth.route('/anmelden', methods=['GET', 'POST'])
def login():
    """Customer login page"""
    if current_user.is_authenticated and isinstance(current_user, Customer):
        return redirect(url_for('customer_dashboard.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember_me = bool(request.form.get('remember_me'))
        
        # Validate input
        if not email or not password:
            flash('Bitte geben Sie E-Mail und Passwort ein.', 'error')
            return render_template('customer/auth/login.html')
        
        # Find customer
        customer = Customer.query.filter_by(email=email).first()
        
        if not customer or not customer.check_password(password):
            flash('Ungültige E-Mail oder Passwort.', 'error')
            return render_template('customer/auth/login.html')
        
        # Login customer
        login_user(customer, remember=remember_me)
        customer.update_last_login()
        
        flash(f'Willkommen zurück, {customer.first_name}!', 'success')
        
        # Redirect to intended page or dashboard
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        
        return redirect(url_for('customer_dashboard.dashboard'))
    
    return render_template('customer/auth/login.html')


@customer_auth.route('/registrieren', methods=['GET', 'POST'])
def register():
    """Customer registration page"""
    if current_user.is_authenticated and isinstance(current_user, Customer):
        return redirect(url_for('customer_dashboard.dashboard'))
    
    if request.method == 'POST':
        # Get form data
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        phone = request.form.get('phone', '').strip()
        
        # Address data
        street = request.form.get('street', '').strip()
        house_number = request.form.get('house_number', '').strip()
        postal_code = request.form.get('postal_code', '').strip()
        city = request.form.get('city', '').strip()
        country = request.form.get('country', 'Deutschland').strip()
        
        # Optional settings
        newsletter = bool(request.form.get('newsletter'))
        terms_accepted = bool(request.form.get('terms'))
        
        # Validation
        errors = []
        
        # Required fields
        if not email:
            errors.append('E-Mail ist erforderlich.')
        elif not validate_email_format(email):
            errors.append('Ungültige E-Mail-Adresse.')
        elif Customer.query.filter_by(email=email).first():
            errors.append('Diese E-Mail-Adresse ist bereits registriert.')
        
        if not first_name:
            errors.append('Vorname ist erforderlich.')
        
        if not last_name:
            errors.append('Nachname ist erforderlich.')
        
        if not password:
            errors.append('Passwort ist erforderlich.')
        elif password != password_confirm:
            errors.append('Passwörter stimmen nicht überein.')
        else:
            password_errors = validate_password_strength(password)
            errors.extend(password_errors)
        
        if not terms_accepted:
            errors.append('Sie müssen die Allgemeinen Geschäftsbedingungen akzeptieren.')
        
        # Display errors
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('customer/auth/register.html')
        
        try:
            # Create new customer with basic fields only
            customer = Customer(
                email=email,
                first_name=first_name,
                last_name=last_name,
                phone=phone or None,
                address=f"{street or ''} {house_number or ''}, {postal_code or ''} {city or ''}, {country}".strip(', ')
            )
            
            customer.set_password(password)
            
            db.session.add(customer)
            db.session.commit()
            
            # Auto-login after registration
            login_user(customer)
            customer.update_last_login()
            
            flash(f'Willkommen bei ByteDohm, {customer.first_name}! Ihr Konto wurde erfolgreich erstellt.', 'success')
            return redirect(url_for('customer_dashboard.dashboard'))
            
        except Exception as e:
            db.session.rollback()
            import traceback
            print(f"Registration error: {e}")
            print(traceback.format_exc())
            flash(f'Ein Fehler ist aufgetreten: {str(e)}', 'error')
            return render_template('customer/auth/register.html')
    
    return render_template('customer/auth/register.html')


@customer_auth.route('/abmelden')
def logout():
    """Customer logout"""
    if current_user.is_authenticated:
        invalidate_customer_session()
        logout_user()
        flash('Sie wurden erfolgreich abgemeldet.', 'info')
    
    return redirect(url_for('index'))


@customer_auth.route('/passwort-vergessen', methods=['GET', 'POST'])
def forgot_password():
    """Forgot password page - placeholder for future implementation"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        
        if email:
            # TODO: Implement password reset functionality
            flash('Falls ein Konto mit dieser E-Mail-Adresse existiert, wurde eine E-Mail mit Anweisungen zum Zurücksetzen des Passworts gesendet.', 'info')
        else:
            flash('Bitte geben Sie Ihre E-Mail-Adresse ein.', 'error')
    
    return render_template('customer/auth/forgot_password.html')

@customer_auth.route('/api/login', methods=['POST'])
def api_login():
    """API endpoint for customer login"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        # Validate input
        if not email or not password:
            return jsonify({'success': False, 'error': 'E-Mail und Passwort sind erforderlich'}), 400
        
        # Find customer
        customer = Customer.query.filter_by(email=email).first()
        
        if not customer or not customer.check_password(password):
            return jsonify({'success': False, 'error': 'Ungültige E-Mail oder Passwort'}), 401
        
        # Login customer
        login_user(customer, remember=True)
        customer.update_last_login()
        
        return jsonify({
            'success': True,
            'message': f'Willkommen zurück, {customer.first_name}!',
            'customer': {
                'id': customer.id,
                'email': customer.email,
                'first_name': customer.first_name,
                'last_name': customer.last_name,
                'full_name': customer.get_full_name()
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': 'Anmeldung fehlgeschlagen'}), 500

@customer_auth.route('/api/register', methods=['POST'])
def api_register():
    """API endpoint for customer registration"""
    try:
        data = request.get_json()
        
        # Get form data
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        terms_accepted = data.get('terms', False)
        
        # Validation
        errors = []
        
        # Required fields
        if not email:
            errors.append('E-Mail ist erforderlich.')
        elif not validate_email_format(email):
            errors.append('Ungültige E-Mail-Adresse.')
        elif Customer.query.filter_by(email=email).first():
            errors.append('Diese E-Mail-Adresse ist bereits registriert.')
        
        if not first_name:
            errors.append('Vorname ist erforderlich.')
        
        if not last_name:
            errors.append('Nachname ist erforderlich.')
        
        if not password:
            errors.append('Passwort ist erforderlich.')
        elif not validate_password_strength(password):
            errors.append('Passwort muss mindestens 8 Zeichen lang sein.')
        
        if not terms_accepted:
            errors.append('Sie müssen die AGB akzeptieren.')
        
        if errors:
            return jsonify({'success': False, 'error': '; '.join(errors)}), 400
        
        # Create new customer
        from datetime import datetime
        customer = Customer(
            email=email,
            first_name=first_name,
            last_name=last_name,
            created_at=datetime.utcnow()
        )
        customer.set_password(password)
        
        try:
            db.session.add(customer)
            db.session.commit()
            
            # Login customer immediately
            login_user(customer, remember=True)
            
            # Send welcome email
            try:
                from email_service import send_registration_email
                send_registration_email(customer)
            except Exception as e:
                print(f"Failed to send welcome email: {e}")
            
            return jsonify({
                'success': True,
                'message': f'Willkommen bei ByteDohm, {customer.first_name}!',
                'customer': {
                    'id': customer.id,
                    'email': customer.email,
                    'first_name': customer.first_name,
                    'last_name': customer.last_name,
                    'full_name': customer.get_full_name()
                }
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': 'Registrierung fehlgeschlagen'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': 'Registrierung fehlgeschlagen'}), 500