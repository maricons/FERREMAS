# Guía de Instalación y Ejecución Local de FERREMAS

Esta guía te permitirá instalar, inicializar y ejecutar el proyecto FERREMAS desde cualquier terminal o computadora.

---

## 1. Clonar el repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd FERREMAS
```

---

## 2. Crear y activar el entorno virtual

### Windows
```bash
python -m venv venv
venv\Scripts\activate
```

### Mac/Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Instalar dependencias

```bash
pip install -r flask_app/requirements.txt
```

---

## 4. Configurar variables de entorno

Crea un archivo `.env` en `flask_app/` con tus credenciales y configuración de base de datos. Ejemplo:

```
SECRET_KEY=tu_clave_secreta
DB_USER=usuario_db
DB_PASSWORD=clave_db
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ferremas
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=tu_email@gmail.com
MAIL_PASSWORD=tu_password
MAIL_DEFAULT_SENDER=tu_email@gmail.com
BASE_URL=http://localhost:5000
```

---

## 5. Inicializar la base de datos

```bash
python init_database.py
```

Esto creará las tablas, categorías y productos de ejemplo.

---

## 6. Ejecutar la aplicación

```bash
python run.py
```

La aplicación estará disponible en: [http://localhost:5000](http://localhost:5000)

---

## 7. (Opcional) Ejecutar pruebas

```bash
pytest tests/
```

---

## Notas
- Si cambias la estructura de la base de datos, recuerda volver a ejecutar `python init_database.py`.
- Si tienes problemas con dependencias, asegúrate de estar usando el entorno virtual correcto.
- Para producción, ajusta las variables de entorno y configura un servidor adecuado.

---

¡Listo! Ahora puedes trabajar con FERREMAS en cualquier entorno local siguiendo estos pasos. 