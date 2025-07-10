import secrets
from datetime import datetime, timedelta
from functools import wraps
from flask import session, request, redirect, url_for, flash, current_app
from flask_login import LoginManager, login_user, logout_user, current_user
from app import app, db
from models import Customer, CustomerSession

# Initialize Flask-Login for customer authentication
customer_login_manager = LoginManager()
customer_login_manager.init_app(app)
customer_login_manager.login_view = 'customer_auth.login'
customer_login_manager.login_message = 'Bitte melden Sie sich an, um auf diese Seite zuzugreifen.'
customer_login_manager.login_message_category = 'info'


@customer_login_manager.user_loader
def load_customer(customer_id):
    """Load customer for Flask-Login"""
    return Customer.query.get(int(customer_id))


def customer_login_required(f):
    """Decorator to require customer login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not isinstance(current_user, Customer):
            return redirect(url_for('customer_auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def create_customer_session(customer, ip_address=None, user_agent=None):
    """Create a new customer session"""
    # Generate secure session token
    session_token = secrets.token_urlsafe(32)
    
    # Set expiration (30 days)
    expires_at = datetime.utcnow() + timedelta(days=30)
    
    # Create session record
    customer_session = CustomerSession(
        customer_id=customer.id,
        session_token=session_token,
        ip_address=ip_address,
        user_agent=user_agent,
        expires_at=expires_at
    )
    
    db.session.add(customer_session)
    db.session.commit()
    
    # Store session token in Flask session
    session['customer_session_token'] = session_token
    
    return customer_session


def validate_customer_session():
    """Validate current customer session"""
    try:
        # First check Flask-Login
        from flask_login import current_user
        if current_user.is_authenticated and isinstance(current_user, Customer):
            return current_user
        
        # Then check custom session token
        session_token = session.get('customer_session_token')
        
        if not session_token:
            return None
        
        # Find active session
        customer_session = CustomerSession.query.filter_by(
            session_token=session_token,
            is_active=True
        ).first()
        
        if not customer_session:
            return None
        
        # Check if session has expired
        if customer_session.expires_at < datetime.utcnow():
            customer_session.is_active = False
            db.session.commit()
            session.pop('customer_session_token', None)
            return None
        
        return customer_session.customer
    except Exception as e:
        print(f"Error validating customer session: {e}")
        return None


def invalidate_customer_session():
    """Invalidate current customer session"""
    session_token = session.get('customer_session_token')
    
    if session_token:
        customer_session = CustomerSession.query.filter_by(
            session_token=session_token,
            is_active=True
        ).first()
        
        if customer_session:
            customer_session.is_active = False
            db.session.commit()
    
    session.pop('customer_session_token', None)


def cleanup_expired_sessions():
    """Clean up expired customer sessions"""
    expired_sessions = CustomerSession.query.filter(
        CustomerSession.expires_at < datetime.utcnow(),
        CustomerSession.is_active == True
    ).all()
    
    for session_obj in expired_sessions:
        session_obj.is_active = False
    
    db.session.commit()
    
    return len(expired_sessions)


def get_customer_ip():
    """Get customer IP address"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        return request.remote_addr


def get_customer_user_agent():
    """Get customer user agent"""
    return request.headers.get('User-Agent', '')[:500]  # Limit length


def validate_password_strength(password):
    """Validate password strength"""
    errors = []
    
    if len(password) < 8:
        errors.append('Passwort muss mindestens 8 Zeichen lang sein')
    
    if not any(c.isupper() for c in password):
        errors.append('Passwort muss mindestens einen Großbuchstaben enthalten')
    
    if not any(c.islower() for c in password):
        errors.append('Passwort muss mindestens einen Kleinbuchstaben enthalten')
    
    if not any(c.isdigit() for c in password):
        errors.append('Passwort muss mindestens eine Zahl enthalten')
    
    return errors


def validate_email_format(email):
    """Basic email format validation"""
    import re
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_pattern, email) is not None