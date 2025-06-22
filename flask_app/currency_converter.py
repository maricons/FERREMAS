import json
import logging
import os
from datetime import datetime, timedelta
from functools import lru_cache

import requests
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

# Configuración
BDE_EMAIL = os.getenv("BDE_EMAIL")
BDE_PASSWORD = os.getenv("BDE_PASSWORD")
BASE_URL = "https://si3.bcentral.cl/SieteRestWS/SieteRestWS.ashx"

# Códigos de series para diferentes monedas
CURRENCY_SERIES = {
    "USD": "F073.TCO.PRE.Z.D",  # Dólar observado
    "EUR": "F073.TCO.EUR.Z.D",  # Euro
    "UF": "F073.UF.PRE.Z.D",  # UF
    "UTM": "F073.UTM.PRE.Z.D",  # UTM
}


class CurrencyConverter:
    def __init__(self):
        try:
            self.session = requests.Session()
            if not BDE_EMAIL or not BDE_PASSWORD:
                logger.error("Credenciales de la API del Banco Central no configuradas")
                raise ValueError(
                    "Credenciales de la API del Banco Central no configuradas"
                )
            logger.info("CurrencyConverter inicializado correctamente")
        except Exception as _:
            logger.error("Error al inicializar CurrencyConverter")
            raise

    @lru_cache(maxsize=32)
    def get_exchange_rate(self, currency_code, date=None):
        """
            Obtiene la tasa de cambio para una moneda específica.

            Args:
                currency_code (str): Código de la moneda (USD, EUR, etc.)
                date (datetime,
        optional): Fecha específica. Por defecto,
        None (usa fecha actual)

            Returns:
                float: Tasa de cambio

            Raises:
                ValueError: Si la moneda no está soportada o hay un error en la API
        """
        try:
            logger.info("Obteniendo tasa de cambio para {currency_code}")

            if currency_code not in CURRENCY_SERIES:
                logger.error("Moneda no soportada: {currency_code}")
                raise ValueError("Moneda no soportada: {currency_code}")

            # Si no se especifica fecha, usar la fecha actual
            if date is None:
                date = datetime.now()

            # Formatear fechas para la API
            end_date = date.strftime("%Y-%m-%d")
            start_date = (date - timedelta(days=5)).strftime("%Y-%m-%d")

            # Construir los parámetros de la API
            params = {
                "user": BDE_EMAIL,
                "pass": BDE_PASSWORD,
                "function": "GetSeries",
                "timeseries": CURRENCY_SERIES[currency_code],
                "firstdate": start_date,
                "lastdate": end_date,
            }

            logger.info("Realizando petición a la API con parámetros: {params}")

            # Realizar la solicitud a la API
            response = self.session.get(BASE_URL, params=params, timeout=10)

            # Verificar errores de autenticación
            if response.status_code == 401:
                logger.error("Error de autenticación con la API del Banco Central")
                raise ValueError("Error de autenticación: Credenciales inválidas")

            response.raise_for_status()

            # Procesar la respuesta
            try:
                data = response.json()
            except json.JSONDecodeError as _:
                logger.error("Error al decodificar JSON de la respuesta")
                logger.error("Respuesta recibida: {response.text}")
                raise ValueError("Error al procesar la respuesta de la API")

            logger.info("Respuesta de la API: {data}")

            # Verificar si hay datos
            if not data or "Series" not in data or not data["Series"]:
                logger.error("No hay datos disponibles para {currency_code}")
                raise ValueError("No hay datos disponibles para {currency_code}")

            # Obtener el valor más reciente
            series = data["Series"]
            if not series["Obs"]:
                logger.error("No hay observaciones para {currency_code}")
                raise ValueError("No hay observaciones para {currency_code}")

            # Filtrar observaciones válidas (statusCode = 'OK')
            valid_observations = [
                obs for obs in series["Obs"] if obs["statusCode"] == "OK"
            ]

            if not valid_observations:
                logger.error("No hay observaciones válidas para {currency_code}")
                raise ValueError("No hay observaciones válidas para {currency_code}")

            # Tomar el valor más reciente
            try:
                latest_value = float(valid_observations[-1]["value"])
            except (KeyError, ValueError, IndexError) as _:
                logger.error("Error al obtener el valor más reciente")
                raise ValueError("Error al procesar el valor de la tasa de cambio")

            logger.info("Tasa de cambio obtenida para {currency_code}: {latest_value}")
            return latest_value

        except requests.RequestException as _:
            logger.error("Error de conexión con la API")
            raise ValueError("Error al conectar con la API del Banco Central")
        except Exception as _:
            logger.error("Error inesperado")
            raise ValueError("Error inesperado")

    def convert_to_clp(self, amount, from_currency):
        """
        Convierte un monto desde una moneda extranjera a CLP.

        Args:
            amount (float): Monto a convertir
            from_currency (str): Código de la moneda origen

        Returns:
            dict: Diccionario con el monto convertido y la tasa usada

        Raises:
            ValueError: Si hay un error en la conversión
        """
        try:
            logger.info("Iniciando conversión de {amount} {from_currency} a CLP")

            # Validar el monto
            try:
                amount = float(amount)
            except (TypeError, ValueError):
                logger.error("Error al convertir monto a float: {amount}")
                raise ValueError("El monto debe ser un número válido")

            if amount <= 0:
                logger.error("Monto inválido: {amount}")
                raise ValueError("El monto debe ser mayor que 0")

            # Obtener la tasa de cambio
            try:
                rate = self.get_exchange_rate(from_currency)
            except ValueError as _:
                logger.error("Error al obtener tasa de cambio")
                raise ValueError("Error al obtener tasa de cambio")

            # Realizar la conversión
            converted_amount = amount * rate

            result = {
                "amount_clp": round(converted_amount, 2),
                "rate": rate,
                "currency": from_currency,
                "original_amount": amount,
                "date": datetime.now().strftime("%Y-%m-%d"),
            }

            logger.info("Conversión exitosa: {result}")
            return result

        except ValueError as _:
            logger.error("Error en la conversión")
            raise ValueError("Error en la conversión")
        except Exception as _:
            logger.error("Error inesperado en la conversión")
            raise ValueError("Error inesperado")

    def get_available_currencies(self):
        """
        Retorna la lista de monedas disponibles para conversión.

        Returns:
            list: Lista de diccionarios con información de las monedas
        """
        return [
            {"code": "USD", "name": "Dólar Estadounidense"},
            {"code": "EUR", "name": "Euro"},
            {"code": "UF", "name": "Unidad de Fomento"},
            {"code": "UTM", "name": "Unidad Tributaria Mensual"},
        ]
