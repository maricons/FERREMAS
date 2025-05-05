# FerreMas - E-Commerce para Ferretería

Un proyecto universitario de e-commerce para una ferretería desarrollado con Flask.

## Características

- Catálogo de productos
- Detalle de productos
- Carrito de compras
- Gestión de usuarios (registro e inicio de sesión)
- Panel de administración para gestionar productos

## Estructura del Proyecto

- `app.py`: Aplicación principal de Flask
- `auth.py`: Módulo de autenticación
- `templates/`: Plantillas HTML
- `static/`: Archivos estáticos (CSS, JS, imágenes)
- `instance/`: Base de datos SQLite

## Configuración del Entorno

1. Crea un entorno virtual:
   ```
   python -m venv venv
   ```

2. Activa el entorno virtual:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

3. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```

4. Crea un archivo `.env` con la siguiente información:
   ```
   SECRET_KEY=tu_clave_secreta
   GOOGLE_CLIENT_ID=tu_client_id (opcional para OAuth)
   GOOGLE_CLIENT_SECRET=tu_client_secret (opcional para OAuth)
   ```

## Ejecución del Proyecto

1. Ejecuta la aplicación:
   ```
   python app.py
   ```

2. Abre un navegador y visita `http://localhost:5000`

## API del Carrito de Compras

### Obtener carrito
```
GET /api/cart
```
Retorna los items en el carrito del usuario actual.

### Añadir al carrito
```
POST /api/cart/add
Content-Type: application/json

{
  "product_id": 1,
  "quantity": 2
}
```
Añade un producto al carrito o incrementa su cantidad si ya existe.

### Actualizar cantidad
```
PUT /api/cart/update/:item_id
Content-Type: application/json

{
  "quantity": 3
}
```
Actualiza la cantidad de un item en el carrito.

### Eliminar del carrito
```
DELETE /api/cart/remove/:item_id
```
Elimina un item específico del carrito.

### Vaciar carrito
```
DELETE /api/cart/clear
```
Elimina todos los items del carrito del usuario actual.

## Uso del Carrito de Compras

1. **Ver catálogo**: En la página principal se muestran todos los productos disponibles.

2. **Ver detalles**: Haz clic en "Ver Detalles" para ver más información de un producto.

3. **Añadir al carrito**: En la página de detalles, establece la cantidad deseada y haz clic en "Añadir al Carrito".

4. **Ver carrito**: Accede al carrito haciendo clic en el enlace "Carrito" en la barra de navegación o visita la ruta `/carrito`.

5. **Gestionar carrito**: En la página del carrito puedes:
   - Cambiar cantidades
   - Eliminar productos
   - Ver el subtotal, impuestos y total

## Notas

Este proyecto es solo para fines educativos y no incluye un sistema de pagos real. La funcionalidad de "Proceder al Pago" muestra un mensaje informativo. 