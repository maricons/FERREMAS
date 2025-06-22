"""
FERREMAS Flask Application Package
"""

from flask import Flask
from flask_mail import Mail
from flask_migrate import Migrate

from .auth import auth_bp
from .extensions import db
from .models import (
    CartItem,
    Category,
    Order,
    OrderItem,
    Product,
    User,
    WebpayTransaction,
)
from .routes import main_bp
from .webpay_plus import WebpayPlus

# Initialize extensions
mail = Mail()
migrate = Migrate()


def create_app(config=None):
    app = Flask(__name__)

    # Load default configuration
    app.config.from_object("flask_app.config.default")

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
    "User",
    "Product",
    "Category",
    "Order",
    "OrderItem",
    "CartItem",
    "WebpayTransaction",
    "auth_bp",
    "WebpayPlus",
    "CurrencyConverter",
]
