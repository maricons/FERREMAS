# FERREMAS - E-Commerce para Ferretería

Un proyecto universitario de e-commerce para una ferretería desarrollado con Flask, implementando las mejores prácticas de desarrollo web, seguridad y testing automatizado.

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
- **Suite completa de pruebas automatizadas (51 tests)**

## 🛠️ Tecnologías Utilizadas

- **Backend**: Python 3.12, Flask
- **Base de Datos**: SQLite (desarrollo) / PostgreSQL (producción) con SQLAlchemy 2.0+
- **Frontend**: HTML5, CSS3, JavaScript
- **Autenticación**: Flask-Login, JWT, OAuth2
- **Email**: Flask-Mail
- **Documentación**: Flasgger (Swagger)
- **Pagos**: Webpay Plus
- **Migraciones**: Flask-Migrate (Alembic)
- **Testing**: pytest, Flask-Testing
- **CI/CD**: GitHub Actions (preparado)

## 📁 Estructura del Proyecto

```
FERREMAS/
├── flask_app/              # Aplicación principal
│   ├── __init__.py
│   ├── app.py              # Configuración de la aplicación
│   ├── auth.py             # Módulo de autenticación
│   ├── routes.py           # Rutas principales
│   ├── models.py           # Modelos de base de datos
│   ├── extensions.py       # Extensiones de Flask
│   ├── webpay_plus.py      # Integración con Webpay
│   ├── currency_converter.py # Conversor de monedas
│   ├── config/             # Configuraciones
│   │   ├── __init__.py
│   │   └── default.py
│   ├── migrations/         # Migraciones de base de datos
│   ├── static/            # Archivos estáticos
│   │   ├── css/          # Estilos
│   │   ├── js/           # Scripts
│   │   ├── images/       # Imágenes
│   │   └── uploads/      # Archivos subidos
│   ├── templates/         # Plantillas HTML
│   │   ├── email/        # Plantillas de correo
│   │   └── ...
│   └── instance/         # Configuración local
├── tests/                # Suite de pruebas
│   ├── __init__.py
│   ├── conftest.py       # Configuración de pytest
│   ├── test_auth.py      # Pruebas de autenticación
│   ├── test_currency_converter.py # Pruebas del conversor
│   ├── test_models.py    # Pruebas de modelos
│   ├── test_routes.py    # Pruebas de rutas
│   ├── test_webpay.py    # Pruebas de Webpay
│   ├── README.md         # Documentación de pruebas
│   └── TEST_DOCUMENTATION.md # Casos de prueba documentados
├── venv/                 # Entorno virtual
├── run.py               # Script de ejecución
├── init_database.py     # Inicialización de BD
├── setup.py            # Configuración del proyecto
├── requirements.txt    # Dependencias
├── SETUP_LOCAL.md      # Guía de configuración local
└── README.md           # Este archivo
```

## ⚙️ Configuración del Entorno

### Opción 1: Configuración Rápida (Recomendada)

1. **Clonar el Repositorio**
   ```bash
   git clone https://github.com/maricons/ferremas.git
   cd ferremas
   ```

2. **Configurar Entorno Virtual**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Instalar Dependencias**
   ```bash
   pip install -r flask_app/requirements.txt
   ```

4. **Inicializar Base de Datos**
   ```bash
   python init_database.py
   ```

5. **Ejecutar Pruebas (Opcional)**
   ```bash
   python -m pytest tests/ -v
   ```

6. **Iniciar la Aplicación**
   ```bash
   python run.py
   ```

### Opción 2: Configuración Completa

Seguir la guía detallada en [SETUP_LOCAL.md](SETUP_LOCAL.md)

## 🚀 Ejecución del Proyecto

### Desarrollo Local
```bash
# Activar entorno virtual
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Ejecutar aplicación
python run.py
```

### Acceso a la Aplicación
- **URL Principal**: `http://localhost:5000`
- **Documentación API**: `http://localhost:5000/apidocs`
- **Conversor de Monedas**: `http://localhost:5000/conversor-moneda`
- **Contacto**: `http://localhost:5000/contacto`

## 🧪 Testing

### Ejecutar Suite Completa
```bash
python -m pytest tests/ -v
```

### Ejecutar Pruebas Específicas
```bash
# Solo pruebas unitarias
python -m pytest tests/test_models.py tests/test_currency_converter.py -v

# Solo pruebas de integración
python -m pytest tests/test_routes.py tests/test_auth.py -v

# Prueba específica
python -m pytest tests/test_routes.py::test_add_to_cart -v
```

### Estado de las Pruebas
- ✅ **51 pruebas pasando**
- ✅ **0 fallos**
- ✅ **0 warnings de SQLAlchemy**
- ✅ **100% compatibilidad con SQLAlchemy 2.0+**

Para más información sobre las pruebas, consulta [tests/README.md](tests/README.md)

## 📝 Documentación de la API

La API está documentada con Swagger y puede accederse en `/apidocs`. Incluye:

### Endpoints Principales
- **GET** `/` - Página principal
- **GET** `/categoria/<id>` - Productos por categoría
- **GET** `/product/<id>` - Detalle de producto
- **GET** `/carrito` - Carrito de compras
- **GET** `/conversor-moneda` - Conversor de monedas
- **GET** `/contacto` - Página de contacto

### API REST
- **POST** `/api/cart/add` - Añadir al carrito
- **PUT** `/api/cart/update/<id>` - Actualizar carrito
- **DELETE** `/api/cart/remove/<id>` - Remover del carrito
- **POST** `/api/convert` - Convertir moneda
- **POST** `/api/contact` - Enviar mensaje de contacto
- **GET** `/api/categories` - Obtener categorías
- **POST** `/iniciar-pago` - Iniciar proceso de pago

## 🔒 Seguridad Implementada

- Hash seguro de contraseñas con PBKDF2
- Protección CSRF en formularios
- Validación de datos de entrada
- Sanitización de archivos subidos
- Manejo seguro de sesiones
- Protección de rutas sensibles
- SQLAlchemy 2.0+ con protección contra inyección SQL

## 📧 Sistema de Correos

- Comprobantes de pago automáticos
- Notificaciones de contacto
- Plantillas HTML responsivas
- Configuración SMTP segura

## 💱 Conversor de Monedas

- Soporte para múltiples monedas
- Actualización en tiempo real
- API REST para conversiones
- Interfaz intuitiva
- Integración con Banco Central de Chile

## 🛍️ Proceso de Compra

1. **Navegación**: Explorar productos por categorías
2. **Selección**: Añadir productos al carrito
3. **Gestión**: Actualizar cantidades y remover items
4. **Autenticación**: Inicio de sesión/registro
5. **Pago**: Integración con Webpay Plus
6. **Confirmación**: Procesamiento de transacción
7. **Comprobante**: Generación y envío por email

## 🐛 Debugging y Logging

- Sistema de logging configurado
- Archivo de log en `app.log`
- Mensajes detallados de error
- Trazas de depuración
- Suite de pruebas para debugging

## 📊 Base de Datos

- Modelos relacionales optimizados
- Migraciones automáticas con Alembic
- Índices optimizados
- Relaciones bien definidas
- Compatible con SQLAlchemy 2.0+

### Modelos Principales
- **User**: Usuarios del sistema
- **Category**: Categorías de productos
- **Product**: Productos del catálogo
- **CartItem**: Items del carrito
- **Order**: Órdenes de compra
- **WebpayTransaction**: Transacciones de pago

## 🎨 Frontend

- Diseño responsivo y moderno
- CSS3 con animaciones
- JavaScript interactivo
- Optimización de imágenes
- Experiencia de usuario mejorada
- Compatible con dispositivos móviles

## 📱 Características Móviles

- Diseño adaptativo
- Menú hamburguesa
- Imágenes optimizadas
- Touch-friendly
- PWA ready

## 📈 Optimizaciones

- Caché de consultas
- Compresión de assets
- Lazy loading de imágenes
- Minificación de CSS/JS
- Base de datos optimizada

## 🔍 Monitoreo

- Logging de errores
- Tracking de transacciones
- Monitoreo de rendimiento
- Alertas de sistema
- Suite de pruebas automatizadas

## 🚀 CI/CD

El proyecto está preparado para integración continua:

### GitHub Actions (Preparado)
- Ejecución automática de pruebas
- Validación de código
- Generación de reportes
- Deployment automático

### Workflow
1. ✅ Instalación de dependencias
2. ✅ Configuración de base de datos
3. ✅ Ejecución de pruebas (51/51)
4. ✅ Generación de reportes
5. ✅ Notificación de resultados

## 📚 Recursos Adicionales

- [Documentación de Flask](https://flask.palletsprojects.com/)
- [Documentación de SQLAlchemy 2.0](https://docs.sqlalchemy.org/)
- [Documentación de Webpay](https://www.transbankdevelopers.cl/)
- [Guía de Estilo Python](https://www.python.org/dev/peps/pep-0008/)
- [Documentación de pytest](https://docs.pytest.org/)

## 👥 Contribución

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Crear Pull Request

### Estándares de Código
- Seguir PEP 8
- Documentar funciones y clases
- Escribir pruebas para nuevas funcionalidades
- Mantener cobertura de código alta

## 📄 Licencia

Este proyecto es para fines educativos y de evaluación.

## 🏆 Logros del Proyecto

### ✅ Completado
- E-commerce funcional completo
- Integración con Webpay Plus
- Sistema de autenticación seguro
- Conversor de monedas
- Suite de pruebas automatizadas (51 tests)
- Documentación completa
- Preparado para CI/CD
- Compatible con SQLAlchemy 2.0+

### 🎯 Características Técnicas
1. **Arquitectura**: Patrón MVC, código modular
2. **Seguridad**: Mejores prácticas implementadas
3. **Base de Datos**: Diseño optimizado con migraciones
4. **Frontend**: Diseño responsivo y moderno
5. **Testing**: Suite completa y estabilizada
6. **Integración**: Webpay, email, conversor de monedas

El código está documentado, probado y sigue las mejores prácticas de desarrollo en Python y Flask. 🚀 