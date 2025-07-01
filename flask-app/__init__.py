"""
FERREMAS Flask Application Package
Aplicación de e-commerce para venta de artículos ferreteros
"""

from flask import Flask
from extensions import db
from models import User, Product, Category, CartItem, Order, OrderItem, WebpayTransaction

# Factory function para crear la aplicación
def create_app(config=None):
    """Factory function para crear la aplicación Flask"""
    app = Flask(__name__)
    
    # Configuración por defecto
    app.config.update({
        'SECRET_KEY': 'dev',
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'TESTING': False,
        'WTF_CSRF_ENABLED': True,
    })
    
    # Aplicar configuración personalizada si se proporciona
    if config:
        app.config.update(config)
    
    # Inicializar extensiones
    db.init_app(app)
    
    return app

# Importar la aplicación principal para compatibilidad
try:
    from app import app
except ImportError:
    # Si no se puede importar, crear una app básica
    app = create_app()

# Hacer disponibles los modelos a nivel de paquete para facilitar testing
__all__ = [
    'app', 'create_app', 'db',
    'User', 'Product', 'Category', 'CartItem', 
    'Order', 'OrderItem', 'WebpayTransaction'
] 