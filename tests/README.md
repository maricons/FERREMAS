# Documentación de Tests - FERREMAS

Esta documentación describe todos los archivos de tests del proyecto FERREMAS, incluyendo su propósito, estructura y cómo ejecutarlos.

## 📁 Estructura de Tests

```
tests/
├── __init__.py                 # Inicializador del paquete de tests
├── conftest.py                 # Configuración y fixtures compartidos
├── test_auth.py               # Tests de autenticación
├── test_models.py             # Tests de modelos de base de datos
├── test_routes.py             # Tests de rutas de la aplicación
├── test_webpay.py             # Tests de integración con Webpay
├── test_currency_converter.py # Tests del conversor de monedas
├── create_test_db.py          # Script para crear base de datos de prueba
├── templates/                 # Templates de prueba
└── static/                    # Archivos estáticos de prueba
```

## 🚀 Ejecución de Tests

### Ejecutar todos los tests
```bash
pytest
```

### Ejecutar tests específicos
```bash
# Tests de autenticación
pytest tests/test_auth.py -v

# Tests de modelos
pytest tests/test_models.py -v

# Tests de rutas
pytest tests/test_routes.py -v

# Tests de Webpay
pytest tests/test_webpay.py -v

# Tests del conversor de monedas
pytest tests/test_currency_converter.py -v
```

### Ejecutar con cobertura
```bash
pytest --cov=flask_app --cov-report=html
```

## 📋 Archivos de Test

### 1. conftest.py
**Propósito:** Configuración global y fixtures compartidos para todos los tests.

#### Fixtures Principales:
- **`app`**: Instancia de Flask configurada para testing
- **`client`**: Cliente de prueba para hacer requests HTTP
- **`test_user`**: Usuario de prueba con credenciales conocidas
- **`test_category`**: Categoría de productos de prueba
- **`test_product`**: Producto de prueba
- **`test_order`**: Orden de prueba
- **`test_cart_item`**: Item del carrito de prueba

#### Configuración:
- Base de datos SQLite en memoria para tests
- Configuración de testing activada
- CSRF deshabilitado para tests
- Variables de entorno configuradas

### 2. test_auth.py
**Propósito:** Tests de autenticación y autorización de usuarios.

#### Tests Incluidos:
- **`test_login_page`**: Verifica que la página de login se carga correctamente
- **`test_login_success`**: Prueba el login exitoso con credenciales válidas
- **`test_login_invalid_credentials`**: Prueba el login con credenciales inválidas
- **`test_register_page`**: Verifica que la página de registro se carga
- **`test_register_success`**: Prueba el registro exitoso de un nuevo usuario
- **`test_register_duplicate_email`**: Prueba el registro con email duplicado
- **`test_logout`**: Prueba la funcionalidad de logout

#### Características:
- Usa fixtures de `test_user` para pruebas de login
- Verifica mensajes flash en español
- Prueba redirecciones después de acciones
- Verifica creación de usuarios en la base de datos

### 3. test_models.py
**Propósito:** Tests de los modelos de base de datos y sus relaciones.

#### Tests Incluidos:
- **`test_user_creation`**: Prueba la creación de usuarios
- **`test_category_creation`**: Prueba la creación de categorías
- **`test_product_creation`**: Prueba la creación de productos
- **`test_cart_item_creation`**: Prueba la creación de items del carrito
- **`test_order_creation`**: Prueba la creación de órdenes con items
- **`test_webpay_transaction_creation`**: Prueba la creación de transacciones Webpay
- **`test_webpay_transaction_update_from_response`**: Prueba la actualización de transacciones
- **`test_relationships`**: Prueba las relaciones entre modelos
- **`test_product_stock_validation`**: Prueba validaciones de stock
- **`test_product_price_validation`**: Prueba validaciones de precio
- **`test_order_status_validation`**: Prueba validaciones de estado de orden
- **`test_user_orders_relationship`**: Prueba la relación usuario-órdenes

#### Características:
- Usa contexto de aplicación para todas las operaciones de BD
- Maneja comparaciones de tipos (float vs Decimal)
- Prueba relaciones entre modelos
- Verifica timestamps automáticos

### 4. test_routes.py
**Propósito:** Tests de las rutas y endpoints de la aplicación web.

#### Tests Incluidos:
- **`test_home_page`**: Prueba la página principal
- **`test_product_listing`**: Prueba el listado de productos por categoría
- **`test_product_detail`**: Prueba la página de detalle de producto
- **`test_category_products`**: Prueba la página de productos por categoría
- **`test_login_page`**: Prueba la página de login
- **`test_login_success`**: Prueba login exitoso
- **`test_login_invalid_credentials`**: Prueba login fallido
- **`test_register_page`**: Prueba la página de registro
- **`test_register_success`**: Prueba registro exitoso
- **`test_register_duplicate_email`**: Prueba registro con email duplicado
- **`test_logout`**: Prueba logout
- **`test_cart_page`**: Prueba la página del carrito
- **`test_add_to_cart`**: Prueba agregar productos al carrito
- **`test_update_cart`**: Prueba actualizar cantidades en el carrito
- **`test_remove_from_cart`**: Prueba remover items del carrito
- **`test_currency_converter_page`**: Prueba la página del conversor
- **`test_contact_page`**: Prueba la página de contacto
- **`test_send_contact_email`**: Prueba el envío de emails de contacto
- **`test_get_categories`**: Prueba la API de categorías
- **`test_webpay_payment_flow`**: Prueba el flujo completo de pago
- **`test_checkout_unauthorized`**: Prueba checkout sin autenticación
- **`test_checkout_empty_cart`**: Prueba checkout con carrito vacío

#### Características:
- Prueba endpoints HTTP (GET, POST, PUT, DELETE)
- Verifica respuestas JSON
- Prueba autenticación requerida
- Verifica redirecciones
- Prueba manejo de errores

### 5. test_webpay.py
**Propósito:** Tests de la integración con Webpay Plus.

#### Tests Incluidos:
- **`test_webpay_initialization`**: Prueba la inicialización de WebpayPlus
- **`test_generate_buy_order`**: Prueba la generación de órdenes de compra
- **`test_create_transaction`**: Prueba la creación de transacciones
- **`test_create_transaction_success`**: Prueba transacción exitosa (mock)
- **`test_create_transaction_error`**: Prueba transacción fallida (mock)

#### Fixtures de Mock:
- **`mock_webpay_success`**: Mock de respuesta exitosa de Webpay
- **`mock_webpay_error`**: Mock de respuesta de error de Webpay

#### Características:
- Usa mocks para simular respuestas de la API de Webpay
- Prueba manejo de errores de red
- Verifica formato de órdenes de compra
- Prueba configuración de ambiente de testing

### 6. test_currency_converter.py
**Propósito:** Tests del conversor de monedas.

#### Tests Incluidos:
- **`test_currency_converter_page`**: Prueba la página del conversor
- **`test_convert_currency_success`**: Prueba conversión exitosa
- **`test_convert_currency_invalid_amount`**: Prueba conversión con monto inválido
- **`test_convert_currency_api_error`**: Prueba manejo de errores de API

#### Características:
- Prueba integración con API externa de monedas
- Verifica cálculos de conversión
- Prueba manejo de errores de API
- Verifica validación de entrada

## 🔧 Configuración de Testing

### Variables de Entorno Requeridas:
```bash
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=ferremas
PYTHONIOENCODING=utf-8
```

### Dependencias de Testing:
- `pytest`: Framework de testing
- `pytest-flask`: Soporte para testing de Flask
- `pytest-mock`: Soporte para mocking
- `requests`: Para tests de APIs externas

## 📊 Métricas de Testing

### Cobertura Actual:
- **test_auth.py**: 7 tests
- **test_models.py**: 12 tests
- **test_routes.py**: 22 tests
- **test_webpay.py**: 5 tests
- **test_currency_converter.py**: 4 tests

**Total:** 50+ tests

### Estado de los Tests:
- ✅ **test_auth.py**: Todos los tests pasando
- ✅ **test_webpay.py**: Todos los tests pasando
- ⚠️ **test_models.py**: 8 tests pasando, 4 fallando
- ⚠️ **test_routes.py**: Algunos tests pueden fallar
- ⚠️ **test_currency_converter.py**: Algunos tests pueden fallar

## 🐛 Troubleshooting

### Problemas Comunes:

1. **DetachedInstanceError**:
   - Asegúrate de usar `db.session.refresh()` antes de acceder a relaciones
   - Mantén los objetos dentro del contexto de aplicación

2. **Comparaciones de Tipos**:
   - Para precios/montos, usa `float()` en ambos lados de la comparación
   - Los valores se almacenan como `float` en la base de datos

3. **Fixtures No Encontrados**:
   - Verifica que los fixtures estén definidos en `conftest.py`
   - Asegúrate de que las dependencias entre fixtures sean correctas

4. **Errores de Importación**:
   - Verifica que el path de Python incluya el directorio padre
   - Asegúrate de que las importaciones sean correctas

### Comandos Útiles:
```bash
# Ver fixtures disponibles
pytest --fixtures

# Ejecutar tests con más información
pytest -v -s

# Ejecutar tests específicos con debug
pytest tests/test_models.py::test_user_creation -v -s

# Ver cobertura de código
pytest --cov=flask_app --cov-report=term-missing
```

## 📝 Notas de Desarrollo

### Convenciones de Testing:
- Usa nombres descriptivos para los tests
- Agrupa tests relacionados en clases o módulos
- Usa fixtures para datos de prueba reutilizables
- Mantén los tests independientes entre sí

### Mejores Prácticas:
- Limpia la base de datos entre tests
- Usa mocks para APIs externas
- Verifica tanto casos exitosos como de error
- Documenta casos edge y comportamientos especiales

### Próximos Pasos:
1. Arreglar los tests fallando en `test_models.py`
2. Mejorar cobertura de código
3. Agregar tests de integración
4. Implementar tests de rendimiento 