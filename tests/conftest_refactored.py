# tests/conftest_refactored.py

import codecs
import os
import sys
from decimal import Decimal
from pathlib import Path

import pytest
from werkzeug.security import generate_password_hash

from flask_app import CartItem, Category, Order, Product, User, db

# Add parent directory to Python path to find the flask-app package
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Force UTF-8 encoding for all string operations
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer)
sys.stdin = codecs.getreader("utf-8")(sys.stdin.buffer)

# Set environment variables for database
os.environ["PYTHONIOENCODING"] = "utf-8"


def get_test_config():
    """
    Get test configuration from environment variables or defaults.
    This makes the tests cloud-agnostic and configurable.
    """
    return {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": os.environ.get(
            "TEST_DATABASE_URL", 
            "sqlite:///:memory:"
        ),
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "SECRET_KEY": os.environ.get("TEST_SECRET_KEY", "test-secret-key"),
        "WTF_CSRF_ENABLED": False,
        
        # Generic cloud-agnostic configurations
        "DATABASE_CONNECTION_TIMEOUT": int(os.environ.get("DB_CONNECTION_TIMEOUT", "30")),
        "API_TIMEOUT": int(os.environ.get("API_TIMEOUT", "30")),
        "REDIS_URL": os.environ.get("CACHE_URL", None),  # For session storage if needed
        
        # External service configurations (cloud-agnostic)
        "WEBPAY_ENVIRONMENT": os.environ.get("PAYMENT_ENVIRONMENT", "sandbox"),
        "CURRENCY_API_TIMEOUT": int(os.environ.get("CURRENCY_API_TIMEOUT", "10")),
        "EMAIL_SERVICE_TIMEOUT": int(os.environ.get("EMAIL_SERVICE_TIMEOUT", "15")),
        
        # Logging and monitoring (works with CloudWatch, Azure Monitor, etc.)
        "LOG_LEVEL": os.environ.get("LOG_LEVEL", "INFO"),
        "MONITORING_ENABLED": os.environ.get("MONITORING_ENABLED", "false").lower() == "true",
    }


@pytest.fixture(scope="session")
def test_config():
    """Provide test configuration for all tests."""
    return get_test_config()


@pytest.fixture
def app(test_config):
    """Create application with cloud-agnostic configuration."""
    from flask_app.app import app as real_app
    from flask_app.app import db  # Asegúrate de importar db aquí

    # Update app config with test configuration
    real_app.config.update(test_config)
    
    with real_app.app_context():
        try:
            db.drop_all()      # <-- Limpia primero
            db.create_all()    # <-- Luego crea las tablas
            yield real_app
        finally:
            db.session.remove()
            db.drop_all()


@pytest.fixture
def client(app):
    """A test client for the app with cloud-agnostic configuration."""
    return app.test_client()


@pytest.fixture
def test_user(app):
    """Create a test user with environment-configurable data."""
    from flask_app import db

    with app.app_context():
        user = User(
            username=os.environ.get("TEST_USER_NAME", "testuser"),
            email=os.environ.get("TEST_USER_EMAIL", "test@test.com"),
            password=generate_password_hash(
                os.environ.get("TEST_USER_PASSWORD", "password123")
            ),
        )
        db.session.add(user)
        db.session.commit()

        # Refresh the user object to ensure it's bound to the session
        db.session.refresh(user)
        return user


@pytest.fixture(scope="function")
def test_category(app):
    """Get or create a test category with configurable data."""
    from flask_app import db

    with app.app_context():
        category = Category.query.first()
        if not category:
            category = Category(
                name=os.environ.get("TEST_CATEGORY_NAME", "Test Category"),
                description=os.environ.get("TEST_CATEGORY_DESC", "Test Description")
            )
            db.session.add(category)
            db.session.commit()

        # Refresh to ensure it's bound to the session
        db.session.refresh(category)
        return category


@pytest.fixture(scope="function")
def test_product(app, test_category):
    """Get or create a test product with configurable data."""
    from flask_app import db

    with app.app_context():
        product = Product.query.first()
        if not product:
            product = Product(
                name=os.environ.get("TEST_PRODUCT_NAME", "Test Product"),
                description=os.environ.get("TEST_PRODUCT_DESC", "Test Description"),
                price=Decimal(os.environ.get("TEST_PRODUCT_PRICE", "99.99")),
                stock=int(os.environ.get("TEST_PRODUCT_STOCK", "10")),
                category_id=test_category.id,
            )
            db.session.add(product)
            db.session.commit()

        # Refresh to ensure it's bound to the session
        db.session.refresh(product)
        assert float(product.price) == float(Decimal(os.environ.get("TEST_PRODUCT_PRICE", "99.99")))
        return product


@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()


@pytest.fixture
def test_order(app, test_user, test_product):
    """Create a test order with configurable amount."""
    from flask_app import db

    with app.app_context():
        order = Order(
            user_id=test_user.id, 
            total_amount=Decimal(os.environ.get("TEST_ORDER_AMOUNT", "1000.00")), 
            status=os.environ.get("TEST_ORDER_STATUS", "pending")
        )
        db.session.add(order)
        db.session.commit()

        # Refresh to ensure it's bound to the session
        db.session.refresh(order)
        return order


@pytest.fixture
def test_cart_item(app, test_user, test_product):
    """Create a test cart item with configurable quantity."""
    from flask_app import db

    with app.app_context():
        cart_item = CartItem.query.filter_by(
            user_id=test_user.id, product_id=test_product.id
        ).first()

        if not cart_item:
            cart_item = CartItem(
                user_id=test_user.id, 
                product_id=test_product.id, 
                quantity=int(os.environ.get("TEST_CART_QUANTITY", "1"))
            )
            db.session.add(cart_item)
            db.session.commit()

        # Refresh to ensure it's bound to the session
        db.session.refresh(cart_item)
        assert cart_item.user_id == test_user.id
        assert cart_item.product_id == test_product.id
        return cart_item


# --- Enhanced Fixtures for External API Mocking ---

@pytest.fixture
def mock_webpay_success(mocker):
    """
    Enhanced mock for Webpay API with cloud-agnostic configuration.
    Works regardless of deployment environment.
    """
    class MockWebpayResponse:
        def __init__(self, token, url):
            self.token = token
            self.url = url

    # Use environment variables for mock responses
    mock_token = os.environ.get("MOCK_WEBPAY_TOKEN", "test_token_12345")
    mock_url = os.environ.get("MOCK_WEBPAY_URL", "https://webpay.test/checkout")
    
    mock_response = MockWebpayResponse(mock_token, mock_url)
    
    return mocker.patch(
        "transbank.webpay.webpay_plus.transaction.Transaction.create",
        return_value=mock_response,
    )


@pytest.fixture
def mock_currency_api_success(mocker):
    """
    Mock for currency converter API with configurable responses.
    Cloud-agnostic and environment independent.
    """
    mock_rate = float(os.environ.get("MOCK_EXCHANGE_RATE", "950.5"))
    mock_response_data = {
        "Series": {
            "Obs": [
                {
                    "statusCode": "OK",
                    "value": str(mock_rate),
                    "timeperiod": "2024-01-01",
                }
            ]
        }
    }

    mock_response = mocker.Mock()
    mock_response.json.return_value = mock_response_data
    mock_response.status_code = 200

    return mocker.patch("requests.Session.get", return_value=mock_response)


@pytest.fixture
def mock_email_service(mocker):
    """
    Mock for email service (works with SES, SendGrid, Azure Communication Services, etc.)
    """
    mock_response = {
        "message_id": os.environ.get("MOCK_EMAIL_ID", "test-email-123"),
        "status": "sent"
    }
    
    return mocker.patch("flask_mail.Mail.send", return_value=mock_response)


@pytest.fixture
def cloud_config():
    """
    Provide cloud-specific configuration that works across providers.
    """
    return {
        # Database configuration (works with RDS, Azure SQL, Cloud SQL)
        "database_url": os.environ.get("DATABASE_URL"),
        "database_pool_size": int(os.environ.get("DB_POOL_SIZE", "5")),
        "database_max_overflow": int(os.environ.get("DB_MAX_OVERFLOW", "10")),
        
        # Cache configuration (works with ElastiCache, Azure Cache for Redis, Cloud Memorystore)
        "cache_url": os.environ.get("CACHE_URL"),
        "cache_timeout": int(os.environ.get("CACHE_TIMEOUT", "300")),
        
        # Storage configuration (works with S3, Azure Blob Storage, Cloud Storage)
        "storage_url": os.environ.get("STORAGE_URL"),
        "storage_bucket": os.environ.get("STORAGE_BUCKET"),
        
        # API endpoints (generic URLs that work anywhere)
        "payment_api_url": os.environ.get("PAYMENT_API_URL", "https://sandbox.webpay.cl"),
        "currency_api_url": os.environ.get("CURRENCY_API_URL", "https://si3.bcentral.cl/SieteRestWS/SieteRestWS.ashx"),
        "notification_api_url": os.environ.get("NOTIFICATION_API_URL"),
        
        # Monitoring and logging (works with CloudWatch, Azure Monitor, Cloud Logging)
        "monitoring_endpoint": os.environ.get("MONITORING_ENDPOINT"),
        "log_group": os.environ.get("LOG_GROUP", "ferremas-tests"),
        "metrics_enabled": os.environ.get("METRICS_ENABLED", "false").lower() == "true",
    }


# Environment validation fixture
@pytest.fixture(scope="session", autouse=True)
def validate_test_environment():
    """
    Validate that the test environment is properly configured.
    Runs automatically for all tests.
    """
    required_env_vars = ["TESTING"]
    missing_vars = [var for var in required_env_vars if not os.environ.get(var)]
    
    if missing_vars:
        pytest.fail(f"Missing required environment variables: {missing_vars}")
    
    # Validate database URL format if provided
    db_url = os.environ.get("TEST_DATABASE_URL")
    if db_url and not any(db_url.startswith(prefix) for prefix in ["sqlite://", "postgresql://", "mysql://"]):
        pytest.fail(f"Invalid TEST_DATABASE_URL format: {db_url}")
    
    return True 