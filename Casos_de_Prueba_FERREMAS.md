# Casos de Prueba FERREMAS
## Documentación Detallada de Tests

---

## 1. Introducción

Este documento detalla todos los casos de prueba implementados en el sistema FERREMAS, basado en el análisis del código de testing existente. Cada caso de prueba corresponde a una función `test_*` específica en el código fuente.

**Convenciones de ID:**
- **TC-AUTH-XX:** Casos de autenticación (`test_auth.py`)
- **TC-MODEL-XX:** Casos de modelos (`test_models.py`)
- **TC-ROUTE-XX:** Casos de rutas/endpoints (`test_routes.py`)
- **TC-WEBPAY-XX:** Casos de integración Webpay (`test_webpay.py`)
- **TC-CURR-XX:** Casos de conversor de moneda (`test_currency_converter.py`)
- **TC-BASIC-XX:** Casos básicos de configuración (`test_basic.py`)

---

## 2. Casos de Prueba - Autenticación (`test_auth.py`)

### TC-AUTH-01: Carga de Página de Login

| Campo | Descripción |
|-------|-------------|
| **ID de Prueba** | TC-AUTH-01 |
| **Nombre de la Prueba** | test_login_page |
| **Componente/Funcionalidad** | Sistema de Autenticación - Interfaz de Login |
| **Precondiciones** | • Aplicación Flask iniciada<br>• Base de datos configurada |
| **Pasos de Ejecución** | 1. Realizar GET request a `/login`<br>2. Verificar status code de respuesta<br>3. Verificar contenido HTML renderizado |
| **Datos de Prueba** | • URL: `/login`<br>• Método: GET |
| **Resultado Esperado** | • Status code: 200<br>• Página contiene texto "iniciar sesion" (case-insensitive) |

### TC-AUTH-02: Login Exitoso con Credenciales Válidas

| Campo | Descripción |
|-------|-------------|
| **ID de Prueba** | TC-AUTH-02 |
| **Nombre de la Prueba** | test_login_success |
| **Componente/Funcionalidad** | Sistema de Autenticación - Proceso de Login |
| **Precondiciones** | • Usuario de prueba existente en BD<br>• Aplicación Flask iniciada<br>• Contexto de sesión activo |
| **Pasos de Ejecución** | 1. Enviar POST a `/login` con credenciales válidas<br>2. Seguir redirects automáticamente<br>3. Verificar status code final<br>4. Verificar que `user_id` está en session<br>5. Validar que `session["user_id"]` coincide con ID del usuario |
| **Datos de Prueba** | • Email: `test@test.com`<br>• Password: `password123`<br>• Método: POST con `follow_redirects=True` |
| **Resultado Esperado** | • Status code: 200<br>• `user_id` presente en session<br>• Session ID coincide con test_user.id |

### TC-AUTH-03: Login con Credenciales Inválidas

| Campo | Descripción |
|-------|-------------|
| **ID de Prueba** | TC-AUTH-03 |
| **Nombre de la Prueba** | test_login_invalid_credentials |
| **Componente/Funcionalidad** | Sistema de Autenticación - Validación de Credenciales |
| **Precondiciones** | • Aplicación Flask iniciada<br>• Base de datos configurada |
| **Pasos de Ejecución** | 1. Enviar POST a `/login` con credenciales incorrectas<br>2. Seguir redirects automáticamente<br>3. Verificar mensaje de error en respuesta |
| **Datos de Prueba** | • Email: `wrong@email.com`<br>• Password: `wrongpass`<br>• Método: POST con `follow_redirects=True` |
| **Resultado Esperado** | • Página contiene "credenciales inválidas" (case-insensitive)<br>• Usuario no autenticado |

### TC-AUTH-04: Carga de Página de Registro

| Campo | Descripción |
|-------|-------------|
| **ID de Prueba** | TC-AUTH-04 |
| **Nombre de la Prueba** | test_register_page |
| **Componente/Funcionalidad** | Sistema de Registro - Interfaz de Registro |
| **Precondiciones** | • Aplicación Flask iniciada<br>• Base de datos configurada |
| **Pasos de Ejecución** | 1. Realizar GET request a `/register`<br>2. Verificar status code de respuesta<br>3. Verificar contenido HTML renderizado |
| **Datos de Prueba** | • URL: `/register`<br>• Método: GET |
| **Resultado Esperado** | • Status code: 200<br>• Página contiene texto "registro" (case-insensitive) |

### TC-AUTH-05: Registro Exitoso de Usuario Nuevo

| Campo | Descripción |
|-------|-------------|
| **ID de Prueba** | TC-AUTH-05 |
| **Nombre de la Prueba** | test_register_success |
| **Componente/Funcionalidad** | Sistema de Registro - Creación de Usuario |
| **Precondiciones** | • Aplicación Flask iniciada<br>• Base de datos limpia<br>• Email no registrado previamente |
| **Pasos de Ejecución** | 1. Enviar POST a `/register` con datos válidos<br>2. Seguir redirects automáticamente<br>3. Verificar status code y mensaje de éxito<br>4. Consultar BD para verificar creación de usuario<br>5. Validar datos del usuario creado |
| **Datos de Prueba** | • Username: `newuser`<br>• Email: `newuser@test.com`<br>• Password: `password123`<br>• Método: POST con `follow_redirects=True` |
| **Resultado Esperado** | • Status code: 200<br>• Página contiene "registro exitoso" (case-insensitive)<br>• Usuario creado en BD con username=`newuser` |

### TC-AUTH-06: Logout de Usuario Autenticado

| Campo | Descripción |
|-------|-------------|
| **ID de Prueba** | TC-AUTH-06 |
| **Nombre de la Prueba** | test_logout |
| **Componente/Funcionalidad** | Sistema de Autenticación - Cierre de Sesión |
| **Precondiciones** | • Usuario de prueba existente<br>• Usuario previamente autenticado<br>• Session activa con `user_id` |
| **Pasos de Ejecución** | 1. Realizar login previo con credenciales válidas<br>2. Enviar GET request a `/logout`<br>3. Seguir redirects automáticamente<br>4. Verificar mensaje de logout<br>5. Validar que session no contiene `user_id` |
| **Datos de Prueba** | • Usuario pre-autenticado: `test@test.com`<br>• URL: `/logout`<br>• Método: GET con `follow_redirects=True` |
| **Resultado Esperado** | • Status code: 200<br>• Página contiene "has cerrado sesión" (case-insensitive)<br>• `user_id` removido de session |

---

## 3. Casos de Prueba - Modelos de Datos (`test_models.py`)

### TC-MODEL-01: Creación de Usuario Válido

| Campo | Descripción |
|-------|-------------|
| **ID de Prueba** | TC-MODEL-01 |
| **Nombre de la Prueba** | test_user_creation |
| **Componente/Funcionalidad** | Modelo User - Creación y Persistencia |
| **Precondiciones** | • Aplicación Flask con contexto activo<br>• Base de datos iniciada<br>• SQLAlchemy configurado |
| **Pasos de Ejecución** | 1. Crear instancia de User con datos válidos<br>2. Agregar a session de BD<br>3. Realizar commit<br>4. Verificar todos los campos persistidos<br>5. Validar timestamps automáticos |
| **Datos de Prueba** | • Username: `testuser`<br>• Password: `hashedpassword`<br>• Email: `test@example.com`<br>• is_active: `True`<br>• is_admin: `False` |
| **Resultado Esperado** | • Usuario persistido correctamente<br>• Todos los campos coinciden<br>• `created_at` y `updated_at` generados automáticamente |

### TC-MODEL-02: Creación de Categoría

| Campo | Descripción |
|-------|-------------|
| **ID de Prueba** | TC-MODEL-02 |
| **Nombre de la Prueba** | test_category_creation |
| **Componente/Funcionalidad** | Modelo Category - Creación y Persistencia |
| **Precondiciones** | • Aplicación Flask con contexto activo<br>• Base de datos iniciada |
| **Pasos de Ejecución** | 1. Crear instancia de Category<br>2. Agregar a session y commit<br>3. Verificar campos persistidos<br>4. Validar timestamp de creación |
| **Datos de Prueba** | • Name: `Test Category`<br>• Description: `Test Description` |
| **Resultado Esperado** | • Categoría creada exitosamente<br>• Campos name y description correctos<br>• `created_at` generado automáticamente |

### TC-MODEL-03: Creación de Producto con Categoría

| Campo | Descripción |
|-------|-------------|
| **ID de Prueba** | TC-MODEL-03 |
| **Nombre de la Prueba** | test_product_creation |
| **Componente/Funcionalidad** | Modelo Product - Creación y Relación con Category |
| **Precondiciones** | • Aplicación Flask con contexto activo<br>• Categoría de prueba existente<br>• Fixture `test_category` disponible |
| **Pasos de Ejecución** | 1. Crear instancia de Product con category_id<br>2. Agregar a session y commit<br>3. Verificar todos los campos<br>4. Validar relación con categoría<br>5. Confirmar precisión de precio Decimal |
| **Datos de Prueba** | • Name: `Test Product`<br>• Description: `Test Description`<br>• Price: `Decimal("99.99")`<br>• Stock: `10`<br>• Category_id: `test_category.id` |
| **Resultado Esperado** | • Producto creado exitosamente<br>• Precio Decimal mantiene precisión<br>• Relación con categoría establecida<br>• `created_at` generado |

### TC-MODEL-04: Creación de Item en Carrito

| Campo | Descripción |
|-------|-------------|
| **ID de Prueba** | TC-MODEL-04 |
| **Nombre de la Prueba** | test_cart_item_creation |
| **Componente/Funcionalidad** | Modelo CartItem - Relaciones User-Product |
| **Precondiciones** | • Usuario de prueba existente<br>• Producto de prueba existente<br>• Fixtures `test_user` y `test_product` disponibles |
| **Pasos de Ejecución** | 1. Crear CartItem con user_id y product_id<br>2. Establecer cantidad<br>3. Agregar a session y commit<br>4. Verificar relaciones user y product<br>5. Validar acceso a objetos relacionados |
| **Datos de Prueba** | • User_id: `test_user.id`<br>• Product_id: `test_product.id`<br>• Quantity: `2` |
| **Resultado Esperado** | • CartItem creado exitosamente<br>• Relaciones user y product funcionan<br>• cart_item.user.id == test_user.id<br>• cart_item.product.id == test_product.id |

### TC-MODEL-05: Creación de Orden con Items

| Campo | Descripción |
|-------|-------------|
| **ID de Prueba** | TC-MODEL-05 |
| **Nombre de la Prueba** | test_order_creation |
| **Componente/Funcionalidad** | Modelo Order - Creación con OrderItems |
| **Precondiciones** | • Usuario de prueba existente<br>• Producto de prueba existente<br>• Fixtures disponibles |
| **Pasos de Ejecución** | 1. Crear Order con user_id y total_amount<br>2. Commit order<br>3. Crear OrderItem asociado<br>4. Commit order item<br>5. Verificar relación order.items<br>6. Validar campos de OrderItem |
| **Datos de Prueba** | • User_id: `test_user.id`<br>• Total_amount: `Decimal("1000.00")`<br>• Status: `pending`<br>• OrderItem quantity: `1`<br>• Price_at_time: `Decimal("1000.00")` |
| **Resultado Esperado** | • Order creado con status pending<br>• OrderItem asociado correctamente<br>• len(order.items) == 1<br>• Campos Decimal mantienen precisión<br>• Timestamps generados |

### TC-MODEL-06: Creación de Transacción Webpay

| Campo | Descripción |
|-------|-------------|
| **ID de Prueba** | TC-MODEL-06 |
| **Nombre de la Prueba** | test_webpay_transaction_creation |
| **Componente/Funcionalidad** | Modelo WebpayTransaction - Integración de Pagos |
| **Precondiciones** | • Orden de prueba existente<br>• Fixture `test_order` disponible |
| **Pasos de Ejecución** | 1. Crear WebpayTransaction con order_id<br>2. Establecer token_ws y datos iniciales<br>3. Commit transaction<br>4. Verificar campos persistidos<br>5. Validar status inicial |
| **Datos de Prueba** | • Order_id: `test_order.id`<br>• Token_ws: `test-token`<br>• Status: `pending`<br>• Buy_order: `OC-12345678`<br>• Amount: `Decimal("1000.00")` |
| **Resultado Esperado** | • Transacción creada exitosamente<br>• Todos los campos correctos<br>• Status inicial = pending<br>• `created_at` generado |

### TC-MODEL-07: Actualización de Transacción desde Respuesta Webpay

| Campo | Descripción |
|-------|-------------|
| **ID de Prueba** | TC-MODEL-07 |
| **Nombre de la Prueba** | test_webpay_transaction_update_from_response |
| **Componente/Funcionalidad** | Modelo WebpayTransaction - Actualización desde API |
| **Precondiciones** | • Transacción Webpay existente con status pending<br>• Método update_from_response implementado |
| **Pasos de Ejecución** | 1. Crear transacción inicial<br>2. Preparar response_data simulado<br>3. Llamar update_from_response()<br>4. Commit cambios<br>5. Verificar status actualizado |
| **Datos de Prueba** | • Response_data: `{"status": "approved", "response_code": 0, "amount": 1000, "authorization_code": "test-auth", "payment_type_code": "VD", "installments_number": 0, "card_detail": {"card_number": "1234567890123456"}}` |
| **Resultado Esperado** | • Status actualizado a "completed"<br>• Response_code = 0<br>• Transacción marcada como exitosa |

### TC-MODEL-08: Validación de Relaciones entre Modelos

| Campo | Descripción |
|-------|-------------|
| **ID de Prueba** | TC-MODEL-08 |
| **Nombre de la Prueba** | test_relationships |
| **Componente/Funcionalidad** | Relaciones entre User, Product, Category, Order, CartItem |
| **Precondiciones** | • Todos los fixtures disponibles<br>• Base de datos con datos relacionados |
| **Pasos de Ejecución** | 1. Crear CartItem<br>2. Crear Order<br>3. Consultar objetos frescos de BD<br>4. Verificar user.cart_items<br>5. Verificar product.category<br>6. Verificar user.orders |
| **Datos de Prueba** | • Datos de fixtures existentes<br>• Relaciones establecidas previamente |
| **Resultado Esperado** | • user.cart_items[0].product.id == product.id<br>• product.category.id == category.id<br>• user.orders[0].id == order.id<br>• Todas las relaciones funcionan |

---

## 4. Casos de Prueba - Rutas y Endpoints (`test_routes.py`)

### TC-ROUTE-01: Página de Inicio

| Campo | Descripción |
|-------|-------------|
| **ID de Prueba** | TC-ROUTE-01 |
| **Nombre de la Prueba** | test_home_page |
| **Componente/Funcionalidad** | Ruta Principal - Homepage |
| **Precondiciones** | • Aplicación Flask iniciada<br>• Cliente de prueba configurado |
| **Pasos de Ejecución** | 1. Realizar GET request a `/`<br>2. Verificar status code<br>3. Verificar contenido de la página |
| **Datos de Prueba** | • URL: `/`<br>• Método: GET |
| **Resultado Esperado** | • Status code: 200<br>• Página contiene "Ferremas" |

### TC-ROUTE-02: Listado de Productos por Categoría

| Campo | Descripción |
|-------|-------------|
| **ID de Prueba** | TC-ROUTE-02 |
| **Nombre de la Prueba** | test_product_listing |
| **Componente/Funcionalidad** | Catálogo de Productos - Vista por Categoría |
| **Precondiciones** | • Producto de prueba existente<br>• Fixture `test_product` disponible |
| **Pasos de Ejecución** | 1. Realizar GET a `/categoria/{category_id}`<br>2. Verificar status code<br>3. Verificar que aparece nombre del producto<br>4. Verificar que aparece precio del producto |
| **Datos de Prueba** | • URL: `/categoria/{test_product.category_id}`<br>• Método: GET |
| **Resultado Esperado** | • Status code: 200<br>• Página contiene test_product.name<br>• Página contiene precio del producto |

### TC-ROUTE-03: Detalle de Producto

| Campo | Descripción |
|-------|-------------|
| **ID de Prueba** | TC-ROUTE-03 |
| **Nombre de la Prueba** | test_product_detail |
| **Componente/Funcionalidad** | Catálogo de Productos - Vista Detalle |
| **Precondiciones** | • Producto de prueba existente<br>• Fixture `test_product` disponible |
| **Pasos de Ejecución** | 1. Realizar GET a `/product/{product_id}`<br>2. Verificar status code<br>3. Verificar nombre del producto<br>4. Verificar descripción del producto |
| **Datos de Prueba** | • URL: `/product/{test_product.id}`<br>• Método: GET |
| **Resultado Esperado** | • Status code: 200<br>• Página contiene test_product.name<br>• Página contiene test_product.description |

### TC-ROUTE-04: Añadir Producto al Carrito (API)

| Campo | Descripción |
|-------|-------------|
| **ID de Prueba** | TC-ROUTE-04 |
| **Nombre de la Prueba** | test_add_to_cart |
| **Componente/Funcionalidad** | API Carrito - Añadir Producto |
| **Precondiciones** | • Usuario autenticado<br>• Producto de prueba existente<br>• Login previo realizado |
| **Pasos de Ejecución** | 1. Realizar login con credenciales válidas<br>2. Enviar POST a `/api/cart/add` con JSON<br>3. Verificar status code de respuesta<br>4. Validar estructura de respuesta JSON<br>5. Confirmar product_id y quantity |
| **Datos de Prueba** | • JSON: `{"product_id": test_product.id, "quantity": 1}`<br>• Content-Type: application/json<br>• Usuario autenticado |
| **Resultado Esperado** | • Status code: 201<br>• Respuesta JSON con product_id correcto<br>• Quantity = 1 en respuesta |

### TC-ROUTE-05: Actualizar Cantidad en Carrito (API)

| Campo | Descripción |
|-------|-------------|
| **ID de Prueba** | TC-ROUTE-05 |
| **Nombre de la Prueba** | test_update_cart |
| **Componente/Funcionalidad** | API Carrito - Actualizar Cantidad |
| **Precondiciones** | • Usuario autenticado<br>• CartItem existente en BD<br>• Login previo realizado |
| **Pasos de Ejecución** | 1. Realizar login<br>2. Crear CartItem en BD<br>3. Enviar PUT a `/api/cart/update/{item_id}`<br>4. Verificar status code<br>5. Validar cantidad actualizada en respuesta |
| **Datos de Prueba** | • JSON: `{"quantity": 2}`<br>• URL: `/api/cart/update/{cart_item.id}`<br>• Método: PUT |
| **Resultado Esperado** | • Status code: 200<br>• Respuesta JSON con quantity = 2 |

### TC-ROUTE-06: Eliminar Producto del Carrito (API)

| Campo | Descripción |
|-------|-------------|
| **ID de Prueba** | TC-ROUTE-06 |
| **Nombre de la Prueba** | test_remove_from_cart |
| **Componente/Funcionalidad** | API Carrito - Eliminar Item |
| **Precondiciones** | • Usuario autenticado<br>• CartItem existente en BD<br>• Login previo realizado |
| **Pasos de Ejecución** | 1. Realizar login<br>2. Crear CartItem en BD<br>3. Enviar DELETE a `/api/cart/remove/{item_id}`<br>4. Verificar status code<br>5. Confirmar eliminación en BD |
| **Datos de Prueba** | • URL: `/api/cart/remove/{item_id}`<br>• Método: DELETE<br>• Item_id válido |
| **Resultado Esperado** | • Status code: 204<br>• CartItem eliminado de BD<br>• db.session.get(CartItem, item_id) == None |

### TC-ROUTE-07: Flujo Completo de Pago Webpay

| Campo | Descripción |
|-------|-------------|
| **ID de Prueba** | TC-ROUTE-07 |
| **Nombre de la Prueba** | test_webpay_payment_flow |
| **Componente/Funcionalidad** | Integración Webpay - Flujo de Pago Completo |
| **Precondiciones** | • Usuario autenticado<br>• CartItem existente<br>• Mock de Webpay configurado |
| **Pasos de Ejecución** | 1. Realizar login<br>2. Añadir item al carrito<br>3. Iniciar proceso de pago POST `/iniciar-pago`<br>4. Verificar respuesta con token y URL<br>5. Validar Order creado en BD<br>6. Confirmar WebpayTransaction creado |
| **Datos de Prueba** | • Usuario autenticado<br>• CartItem con cantidad 1<br>• Método: POST |
| **Resultado Esperado** | • Status code: 200<br>• JSON con "token" y "url"<br>• Order creado con status "pending"<br>• WebpayTransaction asociado |

---

## 5. Casos de Prueba - Integración Webpay (`test_webpay.py`)

### TC-WEBPAY-01: Inicialización del Servicio Webpay

| Campo | Descripción |
|-------|-------------|
| **ID de Prueba** | TC-WEBPAY-01 |
| **Nombre de la Prueba** | test_webpay_initialization |
| **Componente/Funcionalidad** | WebpayPlus - Inicialización de Servicio |
| **Precondiciones** | • Clase WebpayPlus disponible<br>• Configuración de credenciales |
| **Pasos de Ejecución** | 1. Crear instancia de WebpayPlus()<br>2. Verificar que la instancia existe<br>3. Validar atributos commerce_code<br>4. Validar atributos api_key<br>5. Confirmar integration_type |
| **Datos de Prueba** | • Configuración por defecto de WebpayPlus |
| **Resultado Esperado** | • Instancia creada exitosamente<br>• Atributos commerce_code, api_key, integration_type presentes |

### TC-WEBPAY-02: Generación de Buy Order

| Campo | Descripción |
|-------|-------------|
| **ID de Prueba** | TC-WEBPAY-02 |
| **Nombre de la Prueba** | test_generate_buy_order |
| **Componente/Funcionalidad** | WebpayPlus - Generación de ID de Orden |
| **Precondiciones** | • Instancia WebpayPlus inicializada |
| **Pasos de Ejecución** | 1. Llamar método generate_buy_order()<br>2. Verificar que retorna string<br>3. Validar que string no está vacío<br>4. Confirmar que inicia con "OC-" |
| **Datos de Prueba** | • Método sin parámetros |
| **Resultado Esperado** | • Retorna string no vacío<br>• Formato: "OC-{timestamp}" |

### TC-WEBPAY-03: Creación de Transacción (Sin Mock)

| Campo | Descripción |
|-------|-------------|
| **ID de Prueba** | TC-WEBPAY-03 |
| **Nombre de la Prueba** | test_create_transaction |
| **Componente/Funcionalidad** | WebpayPlus - Creación de Transacción Real |
| **Precondiciones** | • Instancia WebpayPlus inicializada<br>• Conexión a internet disponible |
| **Pasos de Ejecución** | 1. Llamar create_transaction() con parámetros<br>2. Manejar tanto éxito como error<br>3. Si exitoso: verificar dict response<br>4. Si error: verificar que es Exception |
| **Datos de Prueba** | • Amount: 1000<br>• Buy_order: "TEST-123"<br>• Session_id: "test-session"<br>• Return_url: "http://localhost/return" |
| **Resultado Esperado** | • Éxito: dict con datos de transacción<br>• Error: Exception manejada correctamente |

### TC-WEBPAY-04: Creación de Transacción Exitosa (Con Mock)

| Campo | Descripción |
|-------|-------------|
| **ID de Prueba** | TC-WEBPAY-04 |
| **Nombre de la Prueba** | test_create_transaction_success |
| **Componente/Funcionalidad** | WebpayPlus - Transacción Exitosa Simulada |
| **Precondiciones** | • Mock configurado para respuesta exitosa<br>• Fixture mock_webpay_success activo |
| **Pasos de Ejecución** | 1. Activar mock de respuesta exitosa<br>2. Llamar create_transaction()<br>3. Verificar que retorna dict<br>4. Validar presencia de "token"<br>5. Validar presencia de "url" |
| **Datos de Prueba** | • Amount: 1000<br>• Buy_order: "TEST-123"<br>• Session_id: user_id<br>• Return_url: "http://localhost/return" |
| **Resultado Esperado** | • Dict response<br>• "token" presente en respuesta<br>• "url" presente en respuesta |

---

## 6. Casos de Prueba - Conversor de Monedas (`test_currency_converter.py`)

### TC-CURR-01: Inicialización del Conversor

| Campo | Descripción |
|-------|-------------|
| **ID de Prueba** | TC-CURR-01 |
| **Nombre de la Prueba** | test_currency_converter_initialization |
| **Componente/Funcionalidad** | CurrencyConverter - Inicialización |
| **Precondiciones** | • Clase CurrencyConverter disponible |
| **Pasos de Ejecución** | 1. Crear instancia de CurrencyConverter()<br>2. Verificar que se crea exitosamente |
| **Datos de Prueba** | • Constructor sin parámetros |
| **Resultado Esperado** | • Instancia no es None<br>• Objeto inicializado correctamente |

### TC-CURR-02: Obtener Tasa de Cambio Exitosa (Con Mock)

| Campo | Descripción |
|-------|-------------|
| **ID de Prueba** | TC-CURR-02 |
| **Nombre de la Prueba** | test_get_exchange_rate_success |
| **Componente/Funcionalidad** | CurrencyConverter - API Banco Central |
| **Precondiciones** | • Mock configurado para respuesta exitosa<br>• Session.get mockeado |
| **Pasos de Ejecución** | 1. Configurar mock con respuesta simulada<br>2. Llamar get_exchange_rate("USD")<br>3. Verificar resultado numérico<br>4. Validar llamada a API con parámetros correctos |
| **Datos de Prueba** | • Currency: "USD"<br>• Mock response: {"Series": {"Obs": [{"statusCode": "OK", "value": "950.5"}]}} |
| **Resultado Esperado** | • Retorna 950.5<br>• API llamada con series code correcto |

### TC-CURR-03: Error de Conexión con API

| Campo | Descripción |
|-------|-------------|
| **ID de Prueba** | TC-CURR-03 |
| **Nombre de la Prueba** | test_get_exchange_rate_api_error |
| **Componente/Funcionalidad** | CurrencyConverter - Manejo de Errores |
| **Precondiciones** | • Mock configurado para simular error<br>• RequestException simulada |
| **Pasos de Ejecución** | 1. Configurar mock para lanzar RequestException<br>2. Llamar get_exchange_rate("USD")<br>3. Verificar que se lanza ValueError<br>4. Validar mensaje de error específico |
| **Datos de Prueba** | • Currency: "USD"<br>• Mock: RequestException("API connection error") |
| **Resultado Esperado** | • ValueError lanzado<br>• Mensaje contiene "Error al conectar con la API del Banco Central" |

---

## 7. Casos de Prueba - Configuración Básica (`test_basic.py`)

### TC-BASIC-01: Validación del Entorno

| Campo | Descripción |
|-------|-------------|
| **ID de Prueba** | TC-BASIC-01 |
| **Nombre de la Prueba** | test_environment_setup |
| **Componente/Funcionalidad** | Configuración - Entorno Básico |
| **Precondiciones** | • Python ejecutándose<br>• Tests configurados |
| **Pasos de Ejecución** | 1. Ejecutar assert básico<br>2. Verificar que el entorno responde |
| **Datos de Prueba** | • Assert True |
| **Resultado Esperado** | • Test pasa<br>• Mensaje: "El entorno básico funciona" |

### TC-BASIC-02: Validación de Versión Python

| Campo | Descripción |
|-------|-------------|
| **ID de Prueba** | TC-BASIC-02 |
| **Nombre de la Prueba** | test_python_version |
| **Componente/Funcionalidad** | Configuración - Requisitos de Python |
| **Precondiciones** | • Python instalado<br>• sys.version_info disponible |
| **Pasos de Ejecución** | 1. Obtener sys.version_info<br>2. Verificar que es >= (3, 8)<br>3. Mostrar versión si falla |
| **Datos de Prueba** | • Versión mínima requerida: Python 3.8 |
| **Resultado Esperado** | • Python version >= 3.8<br>• Test pasa sin errores |

### TC-BASIC-03: Validación de Imports Críticos

| Campo | Descripción |
|-------|-------------|
| **ID de Prueba** | TC-BASIC-03 |
| **Nombre de la Prueba** | test_imports |
| **Componente/Funcionalidad** | Configuración - Dependencias Críticas |
| **Precondiciones** | • Flask instalado<br>• pytest instalado |
| **Pasos de Ejecución** | 1. Intentar import flask<br>2. Verificar flask.__version__<br>3. Intentar import pytest<br>4. Verificar pytest.__version__<br>5. Manejar ImportError si ocurre |
| **Datos de Prueba** | • Packages: flask, pytest |
| **Resultado Esperado** | • Imports exitosos<br>• Versiones no None<br>• No ImportError |

### TC-BASIC-04: Creación de App Flask

| Campo | Descripción |
|-------|-------------|
| **ID de Prueba** | TC-BASIC-04 |
| **Nombre de la Prueba** | test_flask_app_import |
| **Componente/Funcionalidad** | Configuración - Aplicación Flask |
| **Precondiciones** | • Módulo flask_app disponible<br>• create_app function disponible |
| **Pasos de Ejecución** | 1. Import create_app from flask_app<br>2. Crear app con configuración de testing<br>3. Verificar que app no es None<br>4. Confirmar app.config["TESTING"] = True |
| **Datos de Prueba** | • Config: {"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:", "SECRET_KEY": "test", "WTF_CSRF_ENABLED": False} |
| **Resultado Esperado** | • App creada exitosamente<br>• config["TESTING"] es True |

### TC-BASIC-05: Importación de Modelos

| Campo | Descripción |
|-------|-------------|
| **ID de Prueba** | TC-BASIC-05 |
| **Nombre de la Prueba** | test_database_models |
| **Componente/Funcionalidad** | Configuración - Modelos de Base de Datos |
| **Precondiciones** | • Módulo flask_app.models disponible |
| **Pasos de Ejecución** | 1. Import Category, Product, User from flask_app.models<br>2. Verificar que User no es None<br>3. Verificar que Product no es None<br>4. Verificar que Category no es None |
| **Datos de Prueba** | • Modelos: User, Product, Category |
| **Resultado Esperado** | • Todos los imports exitosos<br>• Modelos no son None |

### TC-BASIC-06: Variables de Entorno

| Campo | Descripción |
|-------|-------------|
| **ID de Prueba** | TC-BASIC-06 |
| **Nombre de la Prueba** | test_environment_variables |
| **Componente/Funcionalidad** | Configuración - Variables de Entorno |
| **Precondiciones** | • Variable TESTING configurada |
| **Pasos de Ejecución** | 1. Verificar os.environ.get("TESTING")<br>2. Confirmar que es "true"<br>3. Validar configuración crítica |
| **Datos de Prueba** | • TESTING=true |
| **Resultado Esperado** | • TESTING configurado como "true" |

---

## 8. Resumen de Casos de Prueba

### 8.1 Distribución por Componente

| Componente | Cantidad de Casos | IDs |
|------------|-------------------|-----|
| **Autenticación** | 6 casos | TC-AUTH-01 a TC-AUTH-06 |
| **Modelos de Datos** | 8 casos | TC-MODEL-01 a TC-MODEL-08 |
| **Rutas/Endpoints** | 7 casos | TC-ROUTE-01 a TC-ROUTE-07 |
| **Integración Webpay** | 4 casos | TC-WEBPAY-01 a TC-WEBPAY-04 |
| **Conversor Monedas** | 3 casos | TC-CURR-01 a TC-CURR-03 |
| **Configuración Básica** | 6 casos | TC-BASIC-01 a TC-BASIC-06 |

**Total:** **34 Casos de Prueba Documentados**

### 8.2 Casos Críticos por Prioridad

#### **Prioridad ALTA (Casos Críticos):**
- TC-AUTH-02: Login exitoso
- TC-MODEL-03: Creación de productos con precios Decimal
- TC-ROUTE-07: Flujo completo de pago Webpay
- TC-WEBPAY-04: Transacción exitosa
- TC-BASIC-04: Creación de app Flask

#### **Prioridad MEDIA (Casos Importantes):**
- TC-AUTH-03: Validación de credenciales inválidas
- TC-MODEL-08: Relaciones entre modelos
- TC-ROUTE-04,05,06: APIs de carrito
- TC-CURR-02,03: Conversión de monedas con manejo de errores

#### **Prioridad BAJA (Casos de Configuración):**
- TC-BASIC-01,02,03,05,06: Validaciones de entorno
- TC-AUTH-01,04: Carga de páginas
- TC-WEBPAY-01,02: Inicialización de servicios

---

**Documento generado:** Diciembre 2024  
**Versión:** 1.0  
**Estado:** COMPLETO - Basado en código de pruebas real  
**Total de casos:** 34 casos documentados 