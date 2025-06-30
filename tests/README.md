# Plan de Pruebas FERREMAS

## 1. Propósito
Establecer la estrategia y procedimientos para validar la calidad, funcionalidad y robustez del sistema FERREMAS después de su migración a Azure App Services y Azure SQL Server. El plan busca asegurar que los componentes críticos funcionen correctamente en el nuevo entorno, minimizando riesgos y garantizando la continuidad operativa.

## 2. Alcance
Este plan abarca pruebas unitarias y de integración de los módulos backend (Python/Flask), frontend (HTML/JS/CSS), y la integración con servicios externos (Webpay, email, conversor de moneda), así como la interacción con Azure SQL Server.

## 3. Descripción del sistema
FERREMAS es una aplicación de e-commerce desarrollada con Flask, que permite la gestión de productos, usuarios, compras y pagos en línea. Tras la actualización, el backend corre en Azure App Services, y la base de datos se aloja en Azure SQL Server. Incluye autenticación segura, gestión de inventario, integración de pagos con Webpay, notificaciones por email y conversión de monedas.

## 4. Resumen de pruebas

- **Componentes a Probar**:
  - Gestión de usuarios y sesiones (registro, login, recuperación)
  - Catálogo y productos (visualización, búsqueda, stock)
  - Carrito de compras (añadir, eliminar, actualizar cantidades)
  - Proceso de pago y manejo de transacciones
  - Módulo de correos y notificaciones
  - Conversor de monedas
  - Integración con Azure SQL Server y Webpay

- **Objetivos de las Pruebas**:
  - Validar que cada componente funciona de manera aislada (unitarias)
  - Validar que los componentes se integran correctamente (integración)
  - Detectar errores de migración a Azure App Services y SQL Server
  - Comprobar seguridad y manejo de errores

- **Tipos de prueba**:
  - Pruebas unitarias automatizadas (pytest/unittest)
  - Pruebas de integración automatizadas y manuales
  - Pruebas de API (con Swagger/Flasgger)
  - Pruebas de interfaz de usuario (manuales/automatizadas)

- **Técnicas de prueba**:
  - Caja blanca (unitarias en Python)
  - Caja negra (integración y funcionales)
  - Mocking para servicios externos (correo, Webpay)
  - Uso de datos simulados y reales

- **Roles involucrados**:
  - Desarrolladores backend y frontend
  - QA/Testers
  - Líder técnico

## 5. Entorno y configuración de pruebas

- **Lenguaje backend**: Python 3.x (Flask)
- **Frontend**: HTML, CSS, JavaScript
- **Base de datos**: Azure SQL Server
- **Infraestructura**: Azure App Services
- **Frameworks de prueba**: pytest, unittest, Flasgger (Swagger)
- **Herramientas adicionales**: Docker (opcional para local), Postman, Azure Portal
- **Variables de entorno requeridas** (ejemplo):
  - `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME` (para Azure SQL Server)
  - `SECRET_KEY`, `WEBPAY_*`, `MAIL_*`, etc.
- **Comandos básicos**:
  - Instalar dependencias: `pip install -r flask-app/requirements.txt`
  - Ejecutar pruebas: `pytest tests/` o `python -m unittest discover tests/`

## 6. Calendarización de pruebas

| Actividad                  | Fecha de Inicio | Fecha de Fin | Responsable    |
|----------------------------|-----------------|--------------|---------------|
| Diseño de casos de prueba  | 28/06/2025      | 29/06/2025   | QA            |
| Ejecución pruebas unitarias| 29/06/2025      | 30/06/2025   | Dev/QA        |
| Ejecución pruebas integración | 30/06/2025      | 30/06/2025   | Dev/QA        |
| Pruebas en Azure           | 30/06/2025      | 30/06/2025   | QA            |
| Reporte de resultados      | 30/06/2025      | 01/07/2025   | QA            |
| Revisión y cierre          | 30/06/2025      | 01/07/2025   | Líder Técnico |

## 7. Resumen de riesgos (matriz de riesgos)

| Riesgo                             | Probabilidad | Impacto | Mitigación                                  |
|-------------------------------------|--------------|---------|---------------------------------------------|
| Fallos de conexión Azure SQL Server | Media        | Alto    | Pruebas de conectividad, fallback local     |
| Configuración incorrecta de variables de entorno | Media | Alto | Checklist de configuración, revisión por pares |
| Timeout en integración con Webpay   | Baja         | Media   | Mock de Webpay para pruebas automatizadas   |
| Errores de compatibilidad Python    | Baja         | Media   | Verificación de dependencias y versiones    |
| Lentitud por recursos limitados en Azure | Baja    | Media   | Pruebas de carga, monitoreo en Azure        |

## 8. Condiciones para el cierre del proyecto

- Todos los casos de prueba ejecutados y aprobados
- No existen defectos críticos abiertos
- Documentación de resultados disponible
- Pruebas satisfactorias en entorno Azure
- Checklist de migración completado

## 9. Glosario de términos técnicos

- **Unit Test/Prueba Unitaria**: Evalúa una función, clase o módulo de forma aislada.
- **Prueba de Integración**: Evalúa el funcionamiento conjunto de varios módulos o servicios.
- **Mock**: Simulación de servicios externos para pruebas automáticas.
- **Azure App Services**: Plataforma de despliegue en la nube para aplicaciones web.
- **Swagger/Flasgger**: Herramientas para documentar y probar APIs REST.
- **Webpay**: Plataforma de pagos electrónicos.
- **CI/CD**: Integración y entrega continua de software.

---

# 2. Casos de Prueba

Cada caso de prueba se documenta usando la siguiente plantilla:

## Plantilla de Caso de Prueba

| Campo              | Descripción                                                 |
|--------------------|------------------------------------------------------------|
| ID                 | TC-[número]                                                |
| Nombre             | [Nombre del caso de prueba]                                |
| Objetivo           | [Qué se busca validar]                                     |
| Precondiciones     | [Estado previo necesario]                                  |
| Pasos              | [Lista numerada de pasos]                                  |
| Datos de entrada   | [Datos necesarios para la prueba]                          |
| Resultado Esperado | [Qué debe ocurrir si todo es correcto]                     |
| Tipo de prueba     | [Unitaria / Integración]                                   |
| Estado             | [Pendiente / En progreso / Completado]                     |

---

### Ejemplo de casos de prueba

#### TC-001 - Registro de usuario válido

| Campo              | Descripción                                                 |
|--------------------|------------------------------------------------------------|
| ID                 | TC-001                                                     |
| Nombre             | Registro de usuario con datos válidos                      |
| Objetivo           | Verificar que el sistema permite registrar usuarios nuevos  |
| Precondiciones     | No existe el correo en la base de datos                    |
| Pasos              | 1. Acceder al formulario de registro<br>2. Ingresar datos válidos<br>3. Enviar formulario |
| Datos de entrada   | Nombre, correo válido, contraseña segura                   |
| Resultado Esperado | Usuario creado y redirigido a página de bienvenida         |
| Tipo de prueba     | Integración                                                |
| Estado             | Completado                                                 |

#### TC-002 - Añadir producto al carrito

| Campo              | Descripción                                                 |
|--------------------|------------------------------------------------------------|
| ID                 | TC-002                                                     |
| Nombre             | Añadir producto al carrito                                  |
| Objetivo           | Verificar que un usuario puede añadir productos al carrito  |
| Precondiciones     | Usuario autenticado, producto disponible en stock           |
| Pasos              | 1. Iniciar sesión<br>2. Seleccionar producto<br>3. Hacer clic en “Añadir al carrito” |
| Datos de entrada   | ID producto, cantidad                                      |
| Resultado Esperado | Producto aparece en el carrito y contador se actualiza      |
| Tipo de prueba     | Integración                                                |
| Estado             | Completado                                                 |

#### TC-003 - Prueba unitaria: cálculo de subtotal del carrito

| Campo              | Descripción                                                 |
|--------------------|------------------------------------------------------------|
| ID                 | TC-003                                                     |
| Nombre             | Cálculo de subtotal del carrito                            |
| Objetivo           | Validar que la función calcula correctamente el subtotal    |
| Precondiciones     | Función importada                                           |
| Pasos              | 1. Llamar función con lista de productos y cantidades      |
| Datos de entrada   | [{producto: “martillo”, precio: 5000, cantidad: 2}]        |
| Resultado Esperado | Subtotal devuelto: 10.000                                  |
| Tipo de prueba     | Unitaria                                                   |
| Estado             | Completado                                                 |

#### TC-004 - Pago simulado con Webpay (mock)

| Campo              | Descripción                                                 |
|--------------------|------------------------------------------------------------|
| ID                 | TC-004                                                     |
| Nombre             | Pago simulado con Webpay                                   |
| Objetivo           | Verificar integración del flujo de pago con Webpay usando mock |
| Precondiciones     | Carrito con productos, usuario autenticado, mock activo    |
| Pasos              | 1. Iniciar compra<br>2. Seleccionar método de pago Webpay<br>3. Confirmar pago (mock) |
| Datos de entrada   | ID usuario, total carrito, datos mock                      |
| Resultado Esperado | Respuesta exitosa simulada y generación de comprobante     |
| Tipo de prueba     | Integración                                                |
| Estado             | Completado                                                 |
