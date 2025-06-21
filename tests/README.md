# 🧪 Suite de Pruebas - FERREMAS

## Descripción General
Este directorio contiene la suite completa de pruebas automatizadas para el sistema FERREMAS, incluyendo pruebas unitarias, de integración y funcionales. La suite está completamente estabilizada y moderna, compatible con SQLAlchemy 2.0+.

## 📁 Estructura de Archivos

```
tests/
├── __init__.py
├── conftest.py              # Configuración y fixtures de pytest
├── test_auth.py             # Pruebas de autenticación
├── test_currency_converter.py # Pruebas del conversor de moneda
├── test_models.py           # Pruebas de modelos de datos
├── test_routes.py           # Pruebas de rutas y endpoints
├── test_webpay.py           # Pruebas de integración con Webpay
├── TEST_DOCUMENTATION.md    # Documentación detallada de casos de prueba
├── README.md               # Este archivo
└── static/                 # Archivos estáticos para pruebas
    └── uploads/
```

## 🎯 Tipos de Pruebas

### Pruebas Unitarias
- **test_currency_converter.py**: Pruebas del conversor de moneda (4 pruebas)
- **test_models.py**: Pruebas de los modelos de datos (12 pruebas)
- **test_webpay.py**: Pruebas de la integración con Webpay Plus (5 pruebas)

### Pruebas de Integración
- **test_routes.py**: Pruebas de endpoints y flujos de usuario (18 pruebas)
- **test_auth.py**: Pruebas de autenticación y autorización (7 pruebas)

## 🚀 Ejecución de Pruebas

### Prerrequisitos
1. Activar el entorno virtual:
   ```bash
   venv\Scripts\activate
   ```

2. Instalar dependencias:
   ```bash
   pip install -r flask_app/requirements.txt
   ```

3. Configurar la base de datos:
   ```bash
   python init_database.py
   ```

### Comandos de Ejecución

#### Ejecutar toda la suite:
```bash
python -m pytest tests/ -v
```

#### Ejecutar por categoría:
```bash
# Solo pruebas unitarias
python -m pytest tests/test_models.py tests/test_currency_converter.py tests/test_webpay.py -v

# Solo pruebas de integración
python -m pytest tests/test_routes.py tests/test_auth.py -v
```

#### Ejecutar pruebas específicas:
```bash
# Prueba específica
python -m pytest tests/test_routes.py::test_add_to_cart -v

# Pruebas que contengan "cart" en el nombre
python -m pytest tests/ -k "cart" -v
```

#### Ejecutar con cobertura:
```bash
python -m pytest tests/ --cov=flask_app --cov-report=html
```

## 📊 Estado Actual

✅ **51 pruebas pasando**  
✅ **0 fallos**  
✅ **0 warnings de SQLAlchemy**  
✅ **100% compatibilidad con SQLAlchemy 2.0+**  
✅ **Suite completamente estabilizada**

### Métricas de Cobertura
- **Pruebas Unitarias**: 21 pruebas
- **Pruebas de Integración**: 25 pruebas
- **Pruebas Funcionales**: 5 pruebas
- **Total**: 51 pruebas

### Distribución por Archivo:
- `test_auth.py`: 7 pruebas
- `test_currency_converter.py`: 5 pruebas
- `test_models.py`: 12 pruebas
- `test_routes.py`: 18 pruebas
- `test_webpay.py`: 5 pruebas

## 🔧 Configuración

### Fixtures Disponibles
- `app`: Instancia de la aplicación Flask configurada para testing
- `client`: Cliente de pruebas de Flask
- `test_user`: Usuario de prueba
- `test_product`: Producto de prueba
- `test_category`: Categoría de prueba
- `test_order`: Orden de prueba

### Base de Datos de Pruebas
- Se utiliza SQLite en memoria para las pruebas
- Cada prueba se ejecuta en una transacción aislada
- Los datos se limpian automáticamente entre pruebas
- Compatible con SQLAlchemy 2.0+ (sin warnings legacy)

## 📋 Casos de Prueba Documentados

Para ver la documentación detallada de los casos de prueba más representativos, consulta:
**[TEST_DOCUMENTATION.md](TEST_DOCUMENTATION.md)**

### Casos Destacados:
- **UC-CC-01**: Conversión exitosa de moneda
- **UC-CC-02**: Manejo de moneda inválida
- **IT-RT-01**: Añadir producto al carrito
- **IT-RT-02**: Detalle de producto

## 🐛 Debugging

### Ejecutar con más información:
```bash
python -m pytest tests/ -v -s --tb=long
```

### Ejecutar pruebas fallidas:
```bash
python -m pytest tests/ --lf -v
```

### Ejecutar con pdb:
```bash
python -m pytest tests/ --pdb
```

### Ejecutar sin warnings:
```bash
python -m pytest tests/ -v --disable-warnings
```

## 📝 Mejores Prácticas Implementadas

1. **Nomenclatura**: Nombres descriptivos para todas las pruebas
2. **Aislamiento**: Cada prueba es completamente independiente
3. **Limpieza**: Fixtures para setup y teardown automático
4. **Documentación**: Casos de prueba complejos documentados
5. **Modernización**: Uso de SQLAlchemy 2.0+ sin métodos legacy
6. **Cobertura**: Alta cobertura de código crítico

## 🔄 CI/CD Ready

La suite de pruebas está completamente preparada para CI/CD:

### Workflow de CI/CD
1. ✅ Instalación de dependencias
2. ✅ Configuración de base de datos
3. ✅ Ejecución de pruebas (51/51 pasando)
4. ✅ Generación de reportes de cobertura
5. ✅ Notificación de resultados

### Integración con:
- GitHub Actions
- GitLab CI
- Jenkins
- Azure DevOps

## 🆕 Mejoras Recientes

### Estabilización de la Suite (Completada)
- ✅ Corregidos 8 tests que fallaban
- ✅ Eliminados todos los warnings de SQLAlchemy
- ✅ Modernizado código para SQLAlchemy 2.0+
- ✅ Documentación completa de casos de prueba

### Próximas Mejoras Sugeridas
1. Agregar tests de rendimiento
2. Implementar tests de seguridad
3. Agregar tests de accesibilidad
4. Expandir cobertura de edge cases
5. Implementar tests de carga

## 📞 Soporte

Si encuentras problemas con las pruebas:
1. Verifica que el entorno virtual esté activado
2. Asegúrate de que todas las dependencias estén instaladas
3. Revisa la configuración de la base de datos
4. Consulta los logs de pytest para más detalles
5. Revisa la documentación en `TEST_DOCUMENTATION.md`

---

**Última actualización**: Diciembre 2024  
**Versión**: 2.0.0  
**Estado**: ✅ Suite Completamente Estabilizada  
**Mantenido por**: Equipo de Desarrollo FERREMAS 