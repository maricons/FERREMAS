"""
FERREMAS Flask Application Package
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from .extensions import db
from .models import User, Product, Category, Order, OrderItem, CartItem, WebpayTransaction
from .auth import auth_bp
from .routes import main_bp
from .webpay_plus import WebpayPlus
from .currency_converter import CurrencyConverter

# Initialize extensions
mail = Mail()
migrate = Migrate()

def create_app(config=None):
    app = Flask(__name__)
    
    # Load default configuration
    app.config.from_object('flask_app.config.default')
    
    # Load environment specific configuration
    if config is not None:
        if isinstance(config, dict):
            app.config.update(config)
        else:
            app.config.from_object(config)
    
    # Initialize extensions
    db.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    
    return app

# Make models available at package level
__all__ = [
    'User',
    'Product',
    'Category',
    'Order',
    'OrderItem',
    'CartItem',
    'WebpayTransaction',
    'auth_bp',
    'WebpayPlus',
    'CurrencyConverter'
]
