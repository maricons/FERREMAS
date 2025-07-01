"""
Test básico para verificar que el entorno de testing funciona
Refactorizado para ser cloud-agnostic y compatible con AWS/cualquier proveedor
"""

import os
import sys
from pathlib import Path

import pytest

# Add parent directory to Python path
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)


def test_environment_setup():
    """Test básico para verificar que el entorno está configurado"""
    assert True, "El entorno básico funciona"


def test_python_version():
    """Test para verificar la versión de Python"""
    min_version = tuple(map(int, os.environ.get("MIN_PYTHON_VERSION", "3.8").split(".")))
    assert sys.version_info >= min_version, (
        f"Python version {sys.version_info} es menor que la requerida {min_version}"
    )


def test_imports():
    """Test para verificar que los imports básicos funcionan"""
    try:
        import flask
        assert flask.__version__ is not None
    except ImportError as e:
        pytest.fail(f"No se pudo importar Flask: {e}")

    try:
        import pytest
        assert pytest.__version__ is not None
    except ImportError as e:
        pytest.fail(f"No se pudo importar pytest: {e}")


def test_flask_app_import(app):
    """
    Test para verificar que se puede importar la aplicación Flask
    Refactorizado para usar configuración dinámica de entorno
    """
    # Usar la app del fixture de conftest.py que ya maneja la importación correctamente
    assert app is not None
    assert app.config.get("TESTING") is True
    
    # Verify database configuration is set
    assert "SQLALCHEMY_DATABASE_URI" in app.config
    
    # Verify cloud-agnostic configurations
    if os.environ.get("TEST_DATABASE_URL"):
        assert app.config["SQLALCHEMY_DATABASE_URI"] == os.environ.get("TEST_DATABASE_URL")


def test_database_models(test_user, test_category, test_product):
    """Test para verificar que los modelos se pueden importar y usar"""
    # Usar fixtures del conftest.py que ya manejan la importación correctamente
    assert test_user is not None
    assert test_category is not None
    assert test_product is not None
    
    # Verificar que tienen los atributos esperados
    assert hasattr(test_user, 'id')
    assert hasattr(test_user, 'username') or hasattr(test_user, 'email')
    assert hasattr(test_category, 'id')
    assert hasattr(test_category, 'name')
    assert hasattr(test_product, 'id')
    assert hasattr(test_product, 'name')


def test_environment_variables():
    """
    Test para verificar variables de entorno críticas
    Refactorizado para ser más flexible con diferentes clouds
    """
    # Variables obligatorias
    assert os.environ.get("TESTING") == "true", "TESTING no está configurado como true"
    
    # Variables opcionales pero recomendadas para cloud deployment
    cloud_vars = {
        "DATABASE_URL": "URL de base de datos para producción",
        "CACHE_URL": "URL de cache (Redis/ElastiCache)",
        "LOG_LEVEL": "Nivel de logging",
        "MONITORING_ENABLED": "Habilitación de monitoreo"
    }
    
    warnings = []
    for var, description in cloud_vars.items():
        if not os.environ.get(var):
            warnings.append(f"Variable opcional {var} no configurada ({description})")
    
    if warnings:
        print("\nAdvertencias de configuración:")
        for warning in warnings:
            print(f"  - {warning}")


def test_database_connection_config():
    """
    Test para validar configuración de base de datos cloud-agnostic
    """
    db_url = os.environ.get("TEST_DATABASE_URL", "sqlite:///:memory:")
    
    # Validate supported database URLs
    supported_prefixes = ["sqlite://", "postgresql://", "mysql://"]
    assert any(db_url.startswith(prefix) for prefix in supported_prefixes), (
        f"URL de base de datos no soportada: {db_url}. "
        f"Soportadas: {supported_prefixes}"
    )
    
    # For cloud databases, validate additional parameters
    if not db_url.startswith("sqlite://"):
        timeout = os.environ.get("DB_CONNECTION_TIMEOUT", "30")
        assert timeout.isdigit(), "DB_CONNECTION_TIMEOUT debe ser numérico"
        assert int(timeout) > 0, "DB_CONNECTION_TIMEOUT debe ser positivo"


def test_api_configuration():
    """
    Test para validar configuración de APIs externas
    """
    # Webpay/Payment API
    payment_env = os.environ.get("PAYMENT_ENVIRONMENT", "sandbox")
    assert payment_env in ["sandbox", "production"], (
        f"PAYMENT_ENVIRONMENT inválido: {payment_env}. Debe ser 'sandbox' o 'production'"
    )
    
    # Currency API timeout
    currency_timeout = os.environ.get("CURRENCY_API_TIMEOUT", "10")
    assert currency_timeout.isdigit(), "CURRENCY_API_TIMEOUT debe ser numérico"
    assert int(currency_timeout) > 0, "CURRENCY_API_TIMEOUT debe ser positivo"
    
    # Email service timeout
    email_timeout = os.environ.get("EMAIL_SERVICE_TIMEOUT", "15")
    assert email_timeout.isdigit(), "EMAIL_SERVICE_TIMEOUT debe ser numérico"
    assert int(email_timeout) > 0, "EMAIL_SERVICE_TIMEOUT debe ser positivo"


def test_cloud_provider_agnostic_config():
    """
    Test para verificar que la configuración es agnóstica del proveedor cloud
    """
    # Test que las URLs no contengan referencias específicas a proveedores
    database_url = os.environ.get("DATABASE_URL", "")
    cache_url = os.environ.get("CACHE_URL", "")
    storage_url = os.environ.get("STORAGE_URL", "")
    
    # No debe contener referencias específicas a Azure
    azure_keywords = ["azure", "windows", "cloudapp"]
    for url in [database_url, cache_url, storage_url]:
        if url:
            url_lower = url.lower()
            for keyword in azure_keywords:
                if keyword in url_lower:
                    pytest.fail(
                        f"URL contiene referencia específica a Azure ({keyword}): {url}. "
                        f"Usa URLs genéricas para compatibilidad multi-cloud."
                    )


def test_monitoring_configuration():
    """
    Test para validar configuración de monitoreo cloud-agnostic
    """
    monitoring_enabled = os.environ.get("MONITORING_ENABLED", "false").lower()
    assert monitoring_enabled in ["true", "false"], (
        "MONITORING_ENABLED debe ser 'true' o 'false'"
    )
    
    if monitoring_enabled == "true":
        # Verificar que hay endpoint de monitoreo configurado
        monitoring_endpoint = os.environ.get("MONITORING_ENDPOINT")
        if monitoring_endpoint:
            assert monitoring_endpoint.startswith(("http://", "https://")), (
                "MONITORING_ENDPOINT debe ser una URL válida"
            )
        
        # Verificar log group
        log_group = os.environ.get("LOG_GROUP", "ferremas-tests")
        assert len(log_group) > 0, "LOG_GROUP no puede estar vacío"


def test_secrets_configuration():
    """
    Test para verificar que los secretos están configurados correctamente
    """
    secret_key = os.environ.get("TEST_SECRET_KEY", "test-secret-key")
    
    # En producción, el secret key debe ser suficientemente complejo
    if os.environ.get("FLASK_ENV") == "production":
        assert len(secret_key) >= 32, (
            "SECRET_KEY debe tener al menos 32 caracteres en producción"
        )
        assert secret_key != "test-secret-key", (
            "No usar SECRET_KEY por defecto en producción"
        )
    
    # Verificar que no hay claves hardcodeadas en el código
    hardcoded_secrets = [
        "azure_connection_string",
        "DefaultEndpointsProtocol=https",
        "AccountName=",
        "AccountKey=",
        "database.windows.net"
    ]
    
    # Este test validaría que no hay secretos hardcodeados en variables de entorno
    for env_var, value in os.environ.items():
        if any(secret.lower() in value.lower() for secret in hardcoded_secrets):
            pytest.fail(
                f"Posible secreto hardcodeado detectado en {env_var}. "
                f"Usa variables de entorno o servicios de secretos del cloud provider."
            ) 