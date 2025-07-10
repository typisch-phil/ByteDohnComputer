"""
Configuration file for ByteDohm Flask Application
Environment-specific settings for development and production
"""
import os

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SESSION_SECRET') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://u6560-6636_bytedohm:HeikoCindy-8@45.88.108.231:3306/u6560-6636_bytedohm'

class ProductionConfig(Config):
    """Production configuration for Plesk hosting"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://u6560-6636_bytedohm:HeikoCindy-8@45.88.108.231:3306/u6560-6636_bytedohm'
    
    # Optimizations for production
    SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 1 year cache for static files

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}