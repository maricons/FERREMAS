# 📋 Documentación de Casos de Prueba - FERREMAS

## Descripción General
Este documento contiene la documentación detallada de los casos de prueba más representativos del sistema FERREMAS, complementando el código de las pruebas automatizadas con descripciones legibles y estandarizadas.

---

## 🧪 Casos de Prueba Unitarios

### Caso 1: Conversión exitosa de moneda

**ID del Caso de Prueba:** UC-CC-01  
**Archivo:** `tests/test_currency_converter.py`  
**Método:** `test_convert_to_clp`  
**Nombre / Descripción:** Conversión de USD a CLP usando el conversor de moneda  

**Precondiciones:**  
- El sistema tiene acceso a la API de tasas de cambio
- El archivo `test_currency_converter.py` y la clase `CurrencyConverter` están correctamente implementados
- Las dependencias de la API están instaladas y configuradas

**Pasos a ejecutar:**  
1. Instanciar el objeto `CurrencyConverter`
2. Llamar al método `convert_to_clp` con el monto 10 y la moneda 'USD'
3. Verificar que el resultado es un número válido

**Resultado Esperado:**  
- El método retorna un valor numérico mayor a 0 (el monto convertido a CLP)
- No se lanzan excepciones durante la conversión

**Resultado Obtenido:**  
- ✅ El test pasa si el valor retornado es mayor a 0
- ✅ La conversión se ejecuta sin errores

---

### Caso 2: Manejo de moneda inválida

**ID del Caso de Prueba:** UC-CC-02  
**Archivo:** `tests/test_currency_converter.py`  
**Método:** `test_invalid_currency`  
**Nombre / Descripción:** Conversión con código de moneda inválido  

**Precondiciones:**  
- El sistema tiene acceso a la API de tasas de cambio
- El archivo `test_currency_converter.py` y la clase `CurrencyConverter` están correctamente implementados
- El manejo de errores está configurado correctamente

**Pasos a ejecutar:**  
1. Instanciar el objeto `CurrencyConverter`
2. Llamar al método `convert_to_clp` con el monto 10 y la moneda 'XXX' (no válida)
3. Capturar la excepción lanzada

**Resultado Esperado:**  
- El método lanza una excepción `ValueError` indicando que la moneda no es soportada
- El sistema maneja graciosamente el error sin fallar

**Resultado Obtenido:**  
- ✅ El test pasa si se lanza la excepción esperada
- ✅ El sistema no falla catastróficamente

---

## 🔗 Casos de Prueba de Integración

### Caso 3: Añadir producto al carrito

**ID del Caso de Prueba:** IT-RT-01  
**Archivo:** `tests/test_routes.py`  
**Método:** `test_add_to_cart`  
**Nombre / Descripción:** Añadir un producto al carrito de compras  

**Precondiciones:**  
- El usuario está autenticado en el sistema
- Existe al menos un producto en la base de datos
- La base de datos está configurada y accesible
- Las rutas de la API están correctamente registradas

**Pasos a ejecutar:**  
1. Realizar login con un usuario válido usando credenciales correctas
2. Realizar una petición POST a `/api/cart/add` con el `product_id` y `quantity` en formato JSON
3. Verificar la respuesta del servidor

**Resultado Esperado:**  
- La respuesta HTTP es 201 (Created)
- El JSON de respuesta contiene el `product_id` y la cantidad añadida
- El producto se almacena correctamente en la base de datos

**Resultado Obtenido:**  
- ✅ El test pasa si la respuesta cumple con lo esperado
- ✅ El producto se añade correctamente al carrito del usuario

---

### Caso 4: Detalle de producto

**ID del Caso de Prueba:** IT-RT-02  
**Archivo:** `tests/test_routes.py`  
**Método:** `test_product_detail`  
**Nombre / Descripción:** Visualización del detalle de un producto  

**Precondiciones:**  
- Existe al menos un producto en la base de datos
- Las rutas están correctamente configuradas
- Los templates están disponibles y funcionando

**Pasos a ejecutar:**  
1. Realizar una petición GET a `/product/<product_id>` donde `product_id` es un ID válido
2. Verificar el contenido de la respuesta HTML
3. Buscar elementos específicos del producto en la página

**Resultado Esperado:**  
- La respuesta HTTP es 200 (OK)
- El contenido de la página incluye el nombre del producto
- El contenido de la página incluye la descripción del producto
- La página se renderiza correctamente

**Resultado Obtenido:**  
- ✅ El test pasa si la respuesta contiene los datos esperados
- ✅ La página se muestra correctamente con toda la información del producto

---

## 📊 Métricas de Cobertura

| Tipo de Prueba | Total | Pasadas | Fallidas | Cobertura |
|----------------|-------|---------|----------|-----------|
| Unitarias      | 21    | 21      | 0        | 100%      |
| Integración    | 25    | 25      | 0        | 100%      |
| Funcionales    | 5     | 5       | 0        | 100%      |
| **Total**      | **51**| **51**  | **0**    | **100%**  |

### Distribución Detallada:
- **test_auth.py**: 7 pruebas (autenticación)
- **test_currency_converter.py**: 5 pruebas (conversor de moneda)
- **test_models.py**: 12 pruebas (modelos de datos)
- **test_routes.py**: 18 pruebas (rutas y endpoints)
- **test_webpay.py**: 5 pruebas (integración Webpay)
- **test_webpay.py**: 4 pruebas (funcionales)

---

## 🔧 Configuración de Ejecución

### Ejecutar todos los tests:
```bash
python -m pytest tests/ -v
```

### Ejecutar tests específicos:
```bash
# Solo tests unitarios
python -m pytest tests/test_currency_converter.py tests/test_models.py tests/test_webpay.py -v

# Solo tests de integración
python -m pytest tests/test_routes.py tests/test_auth.py -v

# Test específico
python -m pytest tests/test_routes.py::test_add_to_cart -v
```

### Ejecutar con cobertura:
```bash
python -m pytest tests/ --cov=flask_app --cov-report=html
```

### Ejecutar sin warnings:
```bash
python -m pytest tests/ -v --disable-warnings
```

---

## 📝 Notas de Mantenimiento

- **Última actualización:** Diciembre 2024
- **Versión de pytest:** 8.0.0
- **Versión de SQLAlchemy:** 2.0+
- **Estado:** ✅ Todos los tests pasando sin warnings
- **Suite:** ✅ Completamente estabilizada

### Mejoras Implementadas:
1. ✅ Eliminación de warnings legacy de SQLAlchemy
2. ✅ Modernización a SQLAlchemy 2.0+
3. ✅ Corrección de 8 tests que fallaban
4. ✅ Documentación completa de casos de prueba
5. ✅ Preparación para CI/CD

### Próximas mejoras sugeridas:
1. Agregar tests de rendimiento
2. Implementar tests de seguridad
3. Agregar tests de accesibilidad
4. Expandir cobertura de edge cases
5. Implementar tests de carga 