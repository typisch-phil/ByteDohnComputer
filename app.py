import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# DHL API Configuration - Use live API with provided credentials
os.environ['DHL_LIVE'] = 'true'

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

# Configure the database - MySQL only 
# Direct MySQL connection configuration
mysql_connection = "mysql+pymysql://u6560-6636_bytedohm:HeikoCindy-8@45.88.108.231:3306/u6560-6636_bytedohm"
app.config["SQLALCHEMY_DATABASE_URI"] = mysql_connection
logging.info("MySQL connection configured successfully")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with the extension
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'
login_manager.login_message = 'Bitte melden Sie sich an, um auf das Admin Panel zuzugreifen.'

@login_manager.user_loader
def load_user(user_id):
    from models import AdminUser
    return AdminUser.query.get(int(user_id))

# Add template filters
@app.template_filter('from_json')
def from_json_filter(value):
    """Parse JSON string to dictionary"""
    if isinstance(value, str):
        try:
            return json.loads(value)
        except (json.JSONDecodeError, ValueError):
            return {}
    return value or {}

# Import routes after app creation to avoid circular imports
from routes import *
from admin_routes import *
from dhl_routes import *

# Register customer blueprints
from customer.routes.auth_routes import customer_auth
from customer.routes.dashboard_routes import customer_dashboard

app.register_blueprint(customer_auth)
app.register_blueprint(customer_dashboard)

with app.app_context():
    # Import models to ensure tables are created
    import models
    try:
        db.create_all()
        
        # Create default admin user if none exists
        from models import AdminUser, Component, PrebuiltPC
        import json
        if not AdminUser.query.first():
            admin = AdminUser(
                username='admin',
                email='admin@bytedohm.de'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            logging.info("Default admin user created: admin / admin123")
        
        # Create sample components if none exist
        if not Component.query.first():
            sample_components = [
                # CPUs
                Component(
                name='AMD Ryzen 7 7800X3D',
                category='cpus',
                price=449.99,
                specifications=json.dumps({
                    'socket': 'AM5',
                    'cores': 8,
                    'threads': 16,
                    'base_clock': 4.2,
                    'boost_clock': 5.0,
                    'tdp': 120,
                    'memory_support': 'DDR5-5200'
                })
            ),
            Component(
                name='Intel Core i9-14900K',
                category='cpus',
                price=589.99,
                specifications=json.dumps({
                    'socket': 'LGA1700',
                    'cores': 24,
                    'threads': 32,
                    'base_clock': 3.2,
                    'boost_clock': 6.0,
                    'tdp': 125,
                    'memory_support': 'DDR5-5600'
                })
            ),
            # GPUs
            Component(
                name='RTX 4080 Super 16GB',
                category='gpus',
                price=1199.99,
                specifications=json.dumps({
                    'memory': 16,
                    'memory_type': 'GDDR6X',
                    'base_clock': 2295,
                    'boost_clock': 2550,
                    'power_consumption': 320,
                    'length': 304,
                    'width': 137,
                    'height': 61
                })
            ),
            # Motherboards
            Component(
                name='ASUS ROG Strix X670E-E',
                category='motherboards',
                price=399.99,
                specifications=json.dumps({
                    'socket': 'AM5',
                    'chipset': 'X670E',
                    'ram_slots': 4,
                    'ram_types': ['DDR5'],
                    'max_ram_speed': 6400,
                    'max_ram_capacity': 128,
                    'form_factor': 'ATX',
                    'power_consumption': 50
                })
            ),
            # RAM
            Component(
                name='32GB DDR5-5600 Kit',
                category='ram',
                price=189.99,
                specifications=json.dumps({
                    'type': 'DDR5',
                    'capacity': 32,
                    'speed': 5600,
                    'modules': 2,
                    'latency': 'CL30',
                    'power_consumption': 15
                })
            )
        ]
        
            for component in sample_components:
                db.session.add(component)
            
            db.session.commit()
            logging.info("Sample components created")
        
        # Create sample prebuilt PCs if none exist
        if not PrebuiltPC.query.first():
            sample_prebuilts = [
                PrebuiltPC(
                name='Gaming Beast Pro',
                price=1899.99,
                category='gaming',
                description='High-End Gaming PC für 4K Gaming und Streaming',
                image_url='https://via.placeholder.com/400x300/0066cc/ffffff?text=Gaming+Beast+Pro',
                specifications=json.dumps({
                    'cpu': 'AMD Ryzen 7 7800X3D',
                    'gpu': 'RTX 4080 Super 16GB',
                    'ram': '32GB DDR5-5600',
                    'storage': '1TB NVMe SSD',
                    'motherboard': 'ASUS ROG Strix X670E-E',
                    'cooler': 'Noctua NH-D15',
                    'case': 'Fractal Design Define 7',
                    'psu': 'Corsair RM850x 850W 80+ Gold'
                }),
                features=json.dumps([
                    'Ultra-hochauflösendes Gaming in 4K',
                    'Ray Tracing unterstützt',
                    'Whisper-leise Kühlung',
                    'RGB-Beleuchtung',
                    'Windows 11 Pro vorinstalliert',
                    '3 Jahre Garantie'
                ])
            ),
            PrebuiltPC(
                name='Workstation Master',
                price=2499.99,
                category='workstation',
                description='Professionelle Workstation für Content Creation und 3D-Rendering',
                image_url='https://via.placeholder.com/400x300/ff6600/ffffff?text=Workstation+Master',
                specifications=json.dumps({
                    'cpu': 'Intel Core i9-14900K',
                    'gpu': 'RTX 4090 24GB',
                    'ram': '64GB DDR5-5600',
                    'storage': '2TB NVMe SSD',
                    'motherboard': 'ASUS ProArt Z790-CREATOR',
                    'cooler': 'Corsair H150i Elite AIO',
                    'case': 'Lian Li O11 Dynamic EVO',
                    'psu': 'Seasonic PRIME TX-1000 80+ Titanium'
                }),
                features=json.dumps([
                    'Optimiert für Content Creation',
                    'Professionelle GPU mit 24GB VRAM',
                    'Blitzschnelle NVMe-Speicher',
                    'Wasserkühlung für maximale Leistung',
                    'ECC-Speicher-Unterstützung',
                    '5 Jahre Garantie'
                ])
            )
            ]
            
            for prebuilt in sample_prebuilts:
                db.session.add(prebuilt)
            
            db.session.commit()
            logging.info("Sample prebuilt PCs created")
    except Exception as e:
        logging.error(f"Database connection failed: {e}")
        logging.info("Application will start but database features will not work until MySQL is connected")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
