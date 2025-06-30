# FERREMAS - E-Commerce para Ferretería

Un proyecto universitario de e-commerce para una ferretería desarrollado con Flask, implementando las mejores prácticas de desarrollo web, seguridad y actualmente desplegado en Azure App Services con base de datos en Azure SQL Server.

---

## 🚀 Características Principales

### Gestión de Usuarios
- Registro de usuarios con validación de datos
- Inicio de sesión seguro con hash de contraseñas
- Gestión de sesiones con Flask-Session
- Protección de rutas para usuarios autenticados

### Catálogo y Productos
- Catálogo completo de productos con imágenes
- Categorización de productos
- Productos destacados y en promoción
- Búsqueda y filtrado por categorías
- Detalles completos de productos con imágenes y descripciones

### Carrito de Compras
- Gestión completa del carrito de compras
- Actualización en tiempo real de cantidades
- Cálculo automático de subtotales y totales
- Persistencia del carrito en la base de datos
- Validación de stock disponible

### Sistema de Pagos
- Integración con Webpay Plus
- Proceso de pago seguro
- Generación de comprobantes de pago
- Envío de comprobantes por correo electrónico
- Gestión de transacciones y estados de pago

### Características Adicionales
- Conversor de monedas integrado
- Sistema de contacto con envío de correos
- Interfaz responsiva y moderna
- Documentación API con Swagger
- Sistema de logging para debugging

---

## 🛠️ Tecnologías Utilizadas

- **Backend**: Python 3.x, Flask
- **Base de Datos**: Azure SQL Server (anteriormente PostgreSQL), SQLAlchemy ORM
- **Frontend**: HTML5, CSS3, JavaScript
- **Autenticación**: Flask-Login, JWT, OAuth2
- **Email**: Flask-Mail
- **Documentación**: Flasgger (Swagger)
- **Pagos**: Webpay Plus
- **Migraciones**: Flask-Migrate (Alembic)
- **Infraestructura**: Azure App Services

---

## 📁 Estructura del Proyecto

```
flask-app/
├── app.py                  # Aplicación principal
├── auth.py                 # Módulo de autenticación
├── models.py               # Modelos de base de datos
├── extensions.py           # Extensiones de Flask
├── webpay_plus.py          # Integración con Webpay
├── currency_converter.py   # Conversor de monedas
├── migrations/             # Migraciones de base de datos
├── static/                 # Archivos estáticos
│   ├── css/                # Estilos
│   ├── js/                 # Scripts
│   └── images/             # Imágenes
├── templates/              # Plantillas HTML
│   ├── email/              # Plantillas de correo
│   └── ...
├── instance/               # Configuración local
├── tests/                  # Pruebas unitarias y de integración
└── ...
```

---

## ⚙️ Configuración del Entorno

### 1. Requisitos Previos

- Python 3.x
- Azure CLI (opcional para despliegue)
- Git

### 2. Clonar el Repositorio

```bash
git clone https://github.com/maricons/ferremas.git
cd ferremas/flask-app
```

### 3. Configurar Entorno Virtual

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 4. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 5. Configurar Variables de Entorno

Crear archivo `.env` con:
```
SECRET_KEY=tu_clave_secreta
GOOGLE_CLIENT_ID=tu_clave_google
GOOGLE_CLIENT_SECRET=tu_clave_google
DB_USER=usuario_sql_azure
DB_PASSWORD=clave_sql_azure
DB_HOST=servidor_sql_azure.database.windows.net
DB_PORT=1433
DB_NAME=ferremas
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=tu_email
MAIL_PASSWORD=tu_password_email
MAIL_DEFAULT_SENDER=tu_email
BASE_URL=https://ferremas.azurewebsites.net
WEBPAY_COMMERCE_CODE=cod_webpay
WEBPAY_API_KEY=api_webpay
WEBPAY_INTEGRATION_TYPE=PROD
BDE_EMAIL=cuenta_banco_central
BDE_PASSWORD=cuenta_banco_central
```

**Nota:** Actualiza los valores según tu entorno de Azure.

### 6. Inicializar Base de Datos

```bash
flask db upgrade
python init_db.py
python init_categories.py
python init_products.py
```

---

## 🚀 Despliegue en Azure App Services

1. Crear un recurso App Service y configurar entorno Python 3.x.
2. Configurar variables de entorno en Azure Portal (Deployment Center > Configuration).
3. Desplegar código (por GitHub Actions, FTP, o Azure CLI).
4. Asegurarse de que `requirements.txt` y los archivos de migración estén incluidos.
5. Verificar acceso a Azure SQL Server desde el App Service (firewall, cadenas de conexión).

---

## 🧪 Pruebas

- Las pruebas unitarias y de integración se encuentran en el directorio `/tests`.
- Consultar el archivo [`tests/README.md`](tests/README.md) para el plan y casos de prueba detallados.
- Ejecutar pruebas localmente con:

```bash
pytest tests/
# o
python -m unittest discover tests/
```

---

## 📝 Documentación de la API

La API está documentada con Swagger y puede accederse en `/apidocs`. Incluye:

- Gestión de productos
- Gestión del carrito
- Autenticación de usuarios
- Conversión de monedas
- Sistema de contacto

---

## 🔒 Seguridad Implementada

- Hash seguro de contraseñas con PBKDF2
- Protección CSRF en formularios
- Validación y sanitización de datos de entrada
- Manejo seguro de sesiones
- Protección de rutas sensibles

---

## 📧 Sistema de Correos

- Comprobantes de pago automáticos
- Notificaciones de contacto
- Plantillas HTML responsivas
- Configuración SMTP segura

---

## 💱 Conversor de Monedas

- Soporte para múltiples monedas
- Actualización en tiempo real
- API REST para conversiones

---

## 🛍️ Proceso de Compra

1. Selección de productos
2. Gestión del carrito
3. Inicio de sesión/registro
4. Integración con Webpay
5. Confirmación de pago
6. Generación de comprobante
7. Envío de correo de confirmación

---

## 🐛 Debugging y Logging

- Sistema de logging configurado
- Archivo de log en `app.log`
- Mensajes detallados de error

---

## 📊 Base de Datos

- Modelos relacionales optimizados
- Migraciones automáticas
- Índices y relaciones bien definidas
- Ahora en Azure SQL Server

---

## 🎨 Frontend

- Diseño responsivo y moderno
- JavaScript interactivo
- Optimización de imágenes y assets

---

## 📱 Características Móviles

- Diseño adaptativo
- Imágenes optimizadas
- Experiencia touch-friendly

---

## 📈 Optimizaciones y Monitoreo

- Caché de consultas
- Compresión y minificación de assets
- Logging y alertas de sistema
- Monitoreo de rendimiento en Azure

---

## 📚 Recursos Adicionales

- [Documentación de Flask](https://flask.palletsprojects.com/)
- [Documentación de SQLAlchemy](https://docs.sqlalchemy.org/)
- [Documentación de Webpay](https://www.transbankdevelopers.cl/)
- [Guía de Estilo Python](https://www.python.org/dev/peps/pep-0008/)
- [Documentación oficial de Azure App Service](https://learn.microsoft.com/es-es/azure/app-service/)

---

## 👥 Contribución

1. Haz fork del proyecto.
2. Crea una rama feature.
3. Realiza tus cambios y haz commit.
4. Haz push a tu rama.
5. Crea un Pull Request.

---

## 📄 Licencia

Este proyecto es para fines educativos y de evaluación.

---

## 📝 Notas

- El despliegue y pruebas deben realizarse principalmente en el entorno Azure.
- Consulta el plan de pruebas en `/tests/README.md` para asegurar calidad tras la migración.
- El sistema está en mejora continua; reporta cualquier bug o sugerencia mediante issues o pull requests.
