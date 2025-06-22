# FERREMAS CI/CD Pipeline

Este directorio contiene los workflows de GitHub Actions para el proyecto FERREMAS.

## Workflows Disponibles

### main.yml
Workflow principal de Integración Continua que se ejecuta automáticamente en:
- Push a la rama `neo`
- Pull requests a la rama `neo`

## Pasos del Workflow

### 1. Checkout
Descarga el código del repositorio con historial completo para mejor debugging.

### 2. Setup Python
Configura Python 3.12 con cache de pip para instalaciones más rápidas.

### 3. Dependencias del Sistema
Instala librerías necesarias para:
- `psycopg2-binary` (PostgreSQL)
- `pyodbc` (ODBC drivers)

### 4. Dependencias Python
Instala todas las librerías de `flask_app/requirements.txt` y coverage.

### 5. Debug - Información del Entorno
Muestra información útil para debugging:
- Versión de Python
- Lista de paquetes instalados
- Estructura de directorios

### 6. Ejecutar Tests
Ejecuta `pytest tests/` con:
- Variables de entorno desde GitHub Secrets
- Configuración específica para testing
- SQLite en memoria para tests
- Output verbose y manejo de errores

### 7. Reporte de Cobertura
Genera reporte de cobertura de código usando `coverage`.

### 8. Subir Artifacts
Sube el reporte de cobertura como artifact para descarga.

### 9. Linting (Opcional)
Job separado que verifica calidad del código con:
- `black` (formato)
- `isort` (imports)
- `flake8` (estilo)

## Variables de Entorno Requeridas

El workflow requiere las siguientes variables en GitHub Secrets:

### Base de Datos
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`
- `DB_NAME`

### WebPay
- `WEBPAY_API_KEY`
- `WEBPAY_COMMERCE_CODE`
- `WEBPAY_ENVIRONMENT`

### Email
- `MAIL_SERVER`
- `MAIL_PORT`
- `MAIL_USE_TLS`
- `MAIL_USERNAME`
- `MAIL_PASSWORD`

### General
- `SECRET_KEY`

## Configuración de Tests

Los tests están configurados para usar:
- SQLite en memoria (`sqlite:///:memory:`)
- Modo testing activado
- CSRF deshabilitado
- Variables de entorno desde secrets

## Troubleshooting

### Tests Fallando
1. Verificar que todos los secrets están configurados
2. Revisar los logs de debug en el paso 5
3. Verificar que los imports funcionan correctamente
4. Comprobar que la configuración de la app es correcta

### Reporte de Cobertura No Generado
1. Verificar que los tests se ejecutan correctamente
2. Comprobar que coverage está instalado
3. Revisar los logs del paso 7

### Problemas de Dependencias
1. Verificar que `requirements.txt` está actualizado
2. Comprobar que las dependencias del sistema están instaladas
3. Revisar conflictos de versiones

## Archivos de Configuración

- `pytest.ini`: Configuración de pytest
- `conftest.py`: Fixtures y configuración de tests
- `test_basic.py`: Tests básicos de verificación de entorno

## Próximos Pasos

1. Configurar deployment automático
2. Agregar tests de seguridad
3. Implementar análisis de código estático
4. Configurar notificaciones de Slack/Email 