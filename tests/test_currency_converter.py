import sys
from datetime import datetime
from pathlib import Path

import pytest
import requests

from flask_app.currency_converter import CurrencyConverter

# Add parent directory to Python path to find the flask-app package
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)


@pytest.fixture
def currency_converter():
    """Fixture that provides a CurrencyConverter instance"""
    return CurrencyConverter()


@pytest.fixture
def mock_exchange_rate_success(monkeypatch):
    """Mock successful exchange rate API response"""

    def mock_get(*args, **kwargs):
        response = requests.Response()
        response.status_code = 200
        response._content = b"""
        {
            "Series": {
                "Obs": [
                    {
                        "value": "850.50",
                        "statusCode": "OK",
                        "timeperiod": "2024-01-01"
                    }
                ]
            }
        }
        """
        return response

    monkeypatch.setattr(requests.Session, "get", mock_get)


def test_get_exchange_rate_success(currency_converter, mocker):
    """Test successful API call for exchange rate"""
    # Mock response data
    mock_response = {
        "Series": {
            "Obs": [
                {
                    "statusCode": "OK",
                    "value": "950.5",
                    "timeperiod": datetime.now().strftime("%Y-%m-%d"),
                }
            ]
        }
    }

    # Mock the session's get method
    mock_get = mocker.patch.object(currency_converter.session, "get", autospec=True)

    # Configure the mock to return our fake response
    mock_response_obj = mocker.Mock()
    mock_response_obj.json.return_value = mock_response
    mock_response_obj.status_code = 200
    mock_get.return_value = mock_response_obj

    # Call the method and verify the result
    result = currency_converter.get_exchange_rate("USD")
    assert result == 950.5

    # Verify the API was called with correct parameters
    mock_get.assert_called_once()
    args, kwargs = mock_get.call_args
    assert "timeseries" in kwargs["params"]
    assert kwargs["params"]["timeseries"] == "F073.TCO.PRE.Z.D"  # USD series code


def test_get_exchange_rate_api_error(currency_converter, mocker):
    """Test handling of API error"""
    # Mock the session's get method to raise an exception
    mock_get = mocker.patch.object(
        currency_converter.session,
        "get",
        autospec=True,
        side_effect=requests.RequestException("API connection error"),
    )

    # Verify that the method raises ValueError with appropriate message
    with pytest.raises(ValueError) as exc_info:
        currency_converter.get_exchange_rate("USD")

    assert "Error al conectar con la API del Banco Central" in str(exc_info.value)

    # Verify the API was attempted to be called
    mock_get.assert_called_once()


def test_currency_converter_initialization():
    """Test currency converter initialization"""
    converter = CurrencyConverter()
    assert converter is not None


def test_convert_to_clp(mock_exchange_rate_success):
    """Test converting USD to CLP"""
    converter = CurrencyConverter()
    result = converter.convert_to_clp(100, "USD")
    assert isinstance(result, dict)
    assert "amount_clp" in result
    assert isinstance(result["amount_clp"], float)
    assert result["amount_clp"] > 0


def test_invalid_currency():
    """Test converting invalid currency to CLP"""
    converter = CurrencyConverter()
    with pytest.raises(ValueError):
        converter.convert_to_clp(100, "INVALID")
