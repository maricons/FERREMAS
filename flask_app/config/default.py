"""Default configuration for the Flask application."""

import os
from urllib.parse import quote_plus

# Flask configuration
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev')
TESTING = False
DEBUG = False

# Database configuration
def get_db_url():
    user = quote_plus(os.environ.get("POSTGRES_USER", "postgres"))
    password = quote_plus(os.environ.get("POSTGRES_PASSWORD", "admin"))
    host = quote_plus(os.environ.get("POSTGRES_HOST", "localhost"))
    port = quote_plus(os.environ.get("POSTGRES_PORT", "5432"))
    db = quote_plus(os.environ.get("POSTGRES_DB", "ferremas"))
    return f'postgresql://{user}:{password}@{host}:{port}/{db}?client_encoding=utf8'

SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', get_db_url())
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Upload configuration
UPLOAD_FOLDER = 'static/uploads'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

# Email configuration
MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')

# Google OAuth configuration
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
GOOGLE_DISCOVERY_URL = 'https://accounts.google.com/.well-known/openid-configuration'

# WebPay configuration
WEBPAY_COMMERCE_CODE = os.environ.get('WEBPAY_COMMERCE_CODE', '597055555532')
WEBPAY_API_KEY = os.environ.get('WEBPAY_API_KEY', '579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C')
WEBPAY_ENVIRONMENT = os.environ.get('WEBPAY_ENVIRONMENT', 'TEST')

# Application configuration
BASE_URL = os.environ.get('BASE_URL', 'http://localhost:5000') 