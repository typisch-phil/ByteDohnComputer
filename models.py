from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import json

class AdminUser(UserMixin, db.Model):
    __tablename__ = 'admin_users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<AdminUser {self.username}>'

class Configuration(db.Model):
    __tablename__ = 'configurations'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    components = db.Column(db.Text, nullable=False)  # JSON string of selected components
    total_price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Configuration {self.name}>'

class Component(db.Model):
    __tablename__ = 'components'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    specifications = db.Column(db.Text, nullable=False)  # JSON string of specs
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_specs(self):
        try:
            return json.loads(self.specifications)
        except:
            return {}
    
    def set_specs(self, specs_dict):
        self.specifications = json.dumps(specs_dict)
    
    def __repr__(self):
        return f'<Component {self.name}>'

class PrebuiltPC(db.Model):
    __tablename__ = 'prebuilt_pcs'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(500), nullable=True)
    category = db.Column(db.String(50), nullable=False)  # gaming, workstation, office
    description = db.Column(db.Text, nullable=False)
    specifications = db.Column(db.Text, nullable=False)  # JSON string of specs
    features = db.Column(db.Text, nullable=False)  # JSON string of features list
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_specs(self):
        try:
            return json.loads(self.specifications)
        except:
            return {}
    
    def set_specs(self, specs_dict):
        self.specifications = json.dumps(specs_dict)
    
    def get_features(self):
        try:
            return json.loads(self.features)
        except:
            return []
    
    def set_features(self, features_list):
        self.features = json.dumps(features_list)
    
    def __repr__(self):
        return f'<PrebuiltPC {self.name}>'
