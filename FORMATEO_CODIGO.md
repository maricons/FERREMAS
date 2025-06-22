# 🎨 Formateo de Código - FERREMAS

Este documento explica cómo formatear automáticamente el código del proyecto FERREMAS.

## 🚀 Formateo Automático

### Opción 1: Script Automático (Recomendado)

Ejecuta el script de formateo automático:

```bash
python format_code.py
```

Este script:
- ✅ Verifica que las herramientas estén instaladas
- ✅ Ordena los imports con `isort`
- ✅ Formatea el código con `black`
- ✅ Verifica que todo esté correcto
- ✅ Muestra el progreso con emojis

### Opción 2: Comandos Manuales

Si prefieres ejecutar los comandos manualmente:

```bash
# 1. Ordenar imports
isort flask_app/ tests/

# 2. Formatear código
black flask_app/ tests/

# 3. Verificar que todo esté correcto
black --check flask_app/ tests/
isort --check-only flask_app/ tests/
```

## 🛠️ Herramientas Utilizadas

### Black
- **Propósito**: Formateador de código Python
- **Configuración**: 88 caracteres por línea
- **Archivo de config**: `pyproject.toml`

### isort
- **Propósito**: Ordenador de imports
- **Configuración**: Compatible con Black
- **Archivo de config**: `pyproject.toml`

## 📁 Archivos de Configuración

### `pyproject.toml`
Contiene la configuración para ambas herramientas:
- Longitud de línea: 88 caracteres
- Perfil de isort compatible con Black
- Secciones de imports organizadas

### `format_code.py`
Script automatizado que:
- Instala herramientas si no están disponibles
- Ejecuta el formateo completo
- Verifica el resultado
- Proporciona feedback visual

## 🔄 Flujo de Trabajo Recomendado

1. **Desarrollo**: Escribe tu código normalmente
2. **Antes de commit**: Ejecuta `python format_code.py`
3. **Verificación**: El script te dirá si todo está correcto
4. **Commit**: Haz commit de los cambios formateados

## 🚨 Solución de Problemas

### Error de Python 3.12.5
Si ves este error:
```
Python 3.12.5 has a memory safety issue that can cause Black's AST safety checks to fail
```

**Solución**: Actualiza a Python 3.12.6 o usa Python 3.12.4

### Herramientas no instaladas
El script las instalará automáticamente, pero puedes instalarlas manualmente:
```bash
pip install black isort
```

### Verificación manual
Para verificar que el código esté formateado:
```bash
# Verificar formato
black --check flask_app/ tests/

# Verificar imports
isort --check-only flask_app/ tests/
```

## 📋 Comandos Útiles

### Formateo rápido
```bash
python format_code.py
```

### Solo verificar (sin cambiar)
```bash
black --check flask_app/ tests/
isort --check-only flask_app/ tests/
```

### Formateo específico
```bash
# Solo un archivo
black flask_app/models.py
isort flask_app/models.py

# Solo una carpeta
black flask_app/
isort flask_app/
```

## 🎯 Beneficios

- ✅ **Consistencia**: Todo el código sigue el mismo formato
- ✅ **Legibilidad**: Código más fácil de leer y mantener
- ✅ **CI/CD**: El pipeline de GitHub Actions pasará sin problemas
- ✅ **Colaboración**: Todos los desarrolladores usan el mismo estilo
- ✅ **Automático**: No necesitas recordar comandos complejos

## 🔗 Integración con CI/CD

El workflow de GitHub Actions incluye verificación de formato:
- ✅ Black verifica el formato
- ✅ isort verifica el orden de imports
- ✅ Si falla, el pipeline se detiene

Esto asegura que todo el código en el repositorio esté correctamente formateado. 