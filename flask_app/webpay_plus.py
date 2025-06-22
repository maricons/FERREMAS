from transbank.webpay.webpay_plus.transaction import Transaction, WebpayOptions
from transbank.common.integration_type import IntegrationType
import logging
import os
from dotenv import load_dotenv
from datetime import datetime
import uuid
import json

# Cargar variables de entorno
load_dotenv()

logger = logging.getLogger(__name__)


class WebpayPlus:
    def __init__(self):
        """Inicializa la configuración de Webpay Plus"""
        print("\n=== CONFIGURACIÓN DE WEBPAY ===")
        print("Tipo de integración: IntegrationType.TEST")
        print("Código de comercio: 597055555532")
        print("API Key: 579B532A74...42D0A36B1C")

        # Configurar Webpay Plus para ambiente de pruebas
        self.commerce_code = "597055555532"
        self.api_key = (
            "579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C"
        )
        self.integration_type = IntegrationType.TEST

        # Inicializar la instancia de Transaction con WebpayOptions
        options = WebpayOptions(
            commerce_code=self.commerce_code,
            api_key=self.api_key,
            integration_type=self.integration_type,
        )
        self.tx = Transaction(options)

    def generate_buy_order(self):
        """Genera un número de orden de compra único"""
        return f"OC-{str(uuid.uuid4())[:8]}"

    def create_transaction(self, amount, buy_order, session_id, return_url):
        """Crea una transacción en Webpay Plus"""
        try:
            print("\n=== CREANDO TRANSACCIÓN EN WEBPAY ===")
            print("Datos de entrada:")
            print(f"- Monto: {amount}")
            print(f"- Orden de compra: {buy_order}")
            print(f"- ID de sesión: {session_id}")
            print(f"- URL de retorno: {return_url}")

            # Crear la transacción usando la instancia de Transaction
            response = self.tx.create(
                buy_order=buy_order,
                session_id=session_id,
                amount=amount,
                return_url=return_url,
            )

            print("\n=== RESPUESTA DE WEBPAY ===")
            print(f"Token: {response['token']}")
            print(f"URL: {response['url']}")

            return {"token": response["token"], "url": response["url"]}

        except Exception as e:
            print("\n=== ERROR AL CREAR TRANSACCIÓN ===")
            print(f"Error: {str(e)}")
            print(f"Tipo de error: {type(e)}")
            import traceback

            print("Traceback completo:")
            print(traceback.format_exc())
            raise e

    def confirm_transaction(self, token):
        """Confirma una transacción en Webpay Plus"""
        try:
            print("\n=== CONFIRMANDO TRANSACCIÓN EN WEBPAY ===")
            print(f"Token: {token}")

            # Confirmar la transacción
            response = self.tx.commit(token=token)

            print("\n=== RESPUESTA DE CONFIRMACIÓN ===")
            print(f"Código de respuesta: {response['response_code']}")
            print(f"Estado: {response['status']}")
            print(f"Monto: {response['amount']}")
            print(f"Orden de compra: {response['buy_order']}")

            return {
                "response_code": response["response_code"],
                "status": response["status"],
                "amount": response["amount"],
                "buy_order": response["buy_order"],
                "session_id": response["session_id"],
            }

        except Exception as e:
            print("\n=== ERROR AL CONFIRMAR TRANSACCIÓN ===")
            print(f"Error: {str(e)}")
            print(f"Tipo de error: {type(e)}")
            import traceback

            print("Traceback completo:")
            print(traceback.format_exc())
            raise e

    def status(self, token):
        """Consulta el estado de una transacción"""
        try:
            print(f"\n=== CONSULTANDO ESTADO DE TRANSACCIÓN ===")
            print(f"Token: {token}")

            response = self.tx.status(token=token)

            print("\nRespuesta de status:")
            print(json.dumps(response, indent=2))
            return response

        except Exception as e:
            print("\n=== ERROR AL CONSULTAR ESTADO ===")
            print(f"Error: {str(e)}")
            raise

    def refund(self, token, amount):
        """Realiza la devolución de una transacción"""
        try:
            print(f"\n=== INICIANDO DEVOLUCIÓN ===")
            print(f"Token: {token}")
            print(f"Monto: {amount}")

            response = self.tx.refund(token=token, amount=amount)

            print("\nRespuesta de refund:")
            print(json.dumps(response, indent=2))
            return response

        except Exception as e:
            print("\n=== ERROR AL REALIZAR DEVOLUCIÓN ===")
            print(f"Error: {str(e)}")
            raise
