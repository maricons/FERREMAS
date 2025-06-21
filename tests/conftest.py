# tests/conftest.py

import pytest
import sys
import os
from pathlib import Path
from datetime import datetime
from decimal import Decimal
from flask_app import create_app, db, User, Product, Category, CartItem, Order
from werkzeug.security import generate_password_hash
from urllib.parse import quote_plus

# Add parent directory to Python path to find the flask-app package
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from flask import Flask

# Force UTF-8 encoding for all string operations
import codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
sys.stdin = codecs.getreader('utf-8')(sys.stdin.buffer)

# Set environment variables for database
os.environ['POSTGRES_USER'] = 'postgres'
os.environ['POSTGRES_PASSWORD'] = 'postgres'
os.environ['POSTGRES_HOST'] = 'localhost'
os.environ['POSTGRES_PORT'] = '5432'
os.environ['POSTGRES_DB'] = 'ferremas'
os.environ['PYTHONIOENCODING'] = 'utf-8'

def get_test_db_url():
    user = quote_plus(os.environ["POSTGRES_USER"])
    password = quote_plus(os.environ["POSTGRES_PASSWORD"])
    host = quote_plus(os.environ["POSTGRES_HOST"])
    port = quote_plus(os.environ["POSTGRES_PORT"])
    db = quote_plus(os.environ["POSTGRES_DB"])
    return f'postgresql://{user}:{password}@{host}:{port}/{db}?client_encoding=utf8'

@pytest.fixture
def test_db(app):
    """Create a database session for testing."""
    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    from flask_app import create_app, db
    
    # Create the app with test config
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SECRET_KEY': 'test',
        'WTF_CSRF_ENABLED': False
    })

    # Create the database and load test data
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def test_user(app):
    """Create a test user."""
    from flask_app import db
    with app.app_context():
        user = User(
            username='testuser',
            email='test@test.com',
            password=generate_password_hash('password123')
        )
        db.session.add(user)
        db.session.commit()
        
        # Refresh the user object to ensure it's bound to the session
        db.session.refresh(user)
        return user

@pytest.fixture(scope='function')
def test_category(app):
    """Get or create a test category."""
    from flask_app import db
    with app.app_context():
        category = Category.query.first()
        if not category:
            category = Category(name='Test Category')
            db.session.add(category)
            db.session.commit()
            
        # Refresh to ensure it's bound to the session
        db.session.refresh(category)
        return category

@pytest.fixture(scope='function')
def test_product(app, test_category):
    """Get or create a test product."""
    from flask_app import db
    with app.app_context():
        product = Product.query.first()
        if not product:
            product = Product(
                name='Test Product',
                description='Test Description',
                price=Decimal('99.99'),
                stock=10,
                category_id=test_category.id
            )
            db.session.add(product)
            db.session.commit()
            
        # Refresh to ensure it's bound to the session
        db.session.refresh(product)
        assert float(product.price) == float(Decimal('99.99'))
        return product

@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()

@pytest.fixture
def test_order(app, test_user, test_product):
    """Create a test order."""
    from flask_app import db
    with app.app_context():
        order = Order(
            user_id=test_user.id,
            total_amount=Decimal('1000.00'),
            status='pending'
        )
        db.session.add(order)
        db.session.commit()
        
        # Refresh to ensure it's bound to the session
        db.session.refresh(order)
        return order

@pytest.fixture
def test_cart_item(app, test_user, test_product):
    """Create a test cart item."""
    from flask_app import db
    with app.app_context():
        cart_item = CartItem.query.filter_by(
            user_id=test_user.id,
            product_id=test_product.id
        ).first()
        
        if not cart_item:
            cart_item = CartItem(
                user_id=test_user.id,
                product_id=test_product.id,
                quantity=1
            )
            db.session.add(cart_item)
            db.session.commit()
            
        # Refresh to ensure it's bound to the session
        db.session.refresh(cart_item)
        assert cart_item.user_id == test_user.id
        assert cart_item.product_id == test_product.id
        return cart_item

# --- Fixtures de Mocking para APIs Externas ---

@pytest.fixture
def mock_google_oauth_success(mocker):
    # Esta fixture es correcta, la dejamos como está.
    class MockWebpayResponse:
        def __init__(self, token, url):
            self.token = token
            self.url = url
    mock_response = MockWebpayResponse('test_token_12345', 'https://webpay.test/checkout')
    return mocker.patch('transbank.webpay.webpay_plus.transaction.Transaction.create', return_value=mock_response)