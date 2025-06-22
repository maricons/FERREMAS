"""
Test básico para verificar que el entorno de testing funciona
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
    assert sys.version_info >= (
        3,
        8,
    ), f"Python version {sys.version_info} es muy antigua"


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


def test_flask_app_import():
    """Test para verificar que se puede importar la aplicación Flask"""
    try:
        from flask_app import create_app

        app = create_app(
            {
                "TESTING": True,
                "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
                "SQLALCHEMY_TRACK_MODIFICATIONS": False,
                "SECRET_KEY": "test",
                "WTF_CSRF_ENABLED": False,
            }
        )
        assert app is not None
        assert app.config["TESTING"] is True
    except Exception as e:
        pytest.fail(f"No se pudo crear la aplicación Flask: {e}")


def test_database_models():
    """Test para verificar que los modelos se pueden importar"""
    try:
        from flask_app.models import Category, Product, User

        assert User is not None
        assert Product is not None
        assert Category is not None
    except Exception as e:
        pytest.fail(f"No se pudieron importar los modelos: {e}")


def test_environment_variables():
    """Test para verificar variables de entorno críticas"""
    # Verificar que las variables de entorno están configuradas
    assert os.environ.get("PYTHONPATH") is not None, "PYTHONPATH no está configurado"
    assert os.environ.get("TESTING") == "true", "TESTING no está configurado como true"
