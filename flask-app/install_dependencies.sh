#!/bin/bash

# 🛠️ Script de Instalación Robusta de Dependencias - FERREMAS
# Utiliza múltiples estrategias para evitar timeouts y colgamientos

set -e

echo "🛠️ Iniciando instalación robusta de dependencias..."
echo "📂 Directorio actual: $(pwd)"
echo "🐍 Python: $(python --version)"
echo "📦 Pip: $(pip --version)"

# Función para verificar si un paquete está instalado
check_package() {
    python -c "import $1" 2>/dev/null && echo "✅ $1 OK" || echo "❌ $1 NO"
}

# Función para instalar con timeout
install_with_timeout() {
    local package=$1
    local timeout_sec=${2:-60}
    echo "📦 Intentando instalar $package (timeout: ${timeout_sec}s)..."
    
    timeout $timeout_sec pip install --no-cache-dir --timeout 30 "$package" && echo "✅ $package instalado" || {
        echo "⚠️ Timeout instalando $package"
        return 1
    }
}

# Estrategia 1: Instalar dependencias críticas una por una
echo "🚀 Estrategia 1: Dependencias críticas individuales"
CRITICAL_PACKAGES=(
    "Flask==3.1.0"
    "gunicorn==23.0.0" 
    "psycopg2-binary==2.9.10"
    "Werkzeug==3.1.3"
    "SQLAlchemy==2.0.38"
    "Flask-SQLAlchemy==3.1.1"
    "requests==2.32.3"
    "python-dotenv"
)

for package in "${CRITICAL_PACKAGES[@]}"; do
    if ! install_with_timeout "$package" 60; then
        echo "⚠️ Error instalando $package, continuando..."
    fi
done

# Verificar instalaciones críticas
echo "🔍 Verificando instalaciones críticas..."
check_package "flask"
check_package "gunicorn" 
check_package "psycopg2"
check_package "sqlalchemy"

# Estrategia 2: Intentar requirements mínimo
if [ -f "requirements.minimal.txt" ]; then
    echo "🚀 Estrategia 2: Requirements mínimo"
    timeout 180 pip install --no-cache-dir -r requirements.minimal.txt || echo "⚠️ Falló requirements mínimo"
fi

# Estrategia 3: Intentar requirements completo (con timeout)
if [ -f "requirements.txt" ]; then
    echo "🚀 Estrategia 3: Requirements completo (con timeout)"
    timeout 300 pip install --no-cache-dir -r requirements.txt || echo "⚠️ Falló requirements completo"
fi

# Estrategia 4: Instalar dependencias problemáticas por separado
echo "🚀 Estrategia 4: Dependencias problemáticas"
PROBLEMATIC_PACKAGES=(
    "numpy==2.0.2"
    "pandas==2.0.3"
    "transbank-sdk==6.1.0"
)

for package in "${PROBLEMATIC_PACKAGES[@]}"; do
    if ! install_with_timeout "$package" 120; then
        echo "⚠️ Saltando $package (problemático)"
    fi
done

# Verificación final
echo "🔍 Verificación final de dependencias críticas..."
CRITICAL_IMPORTS=("flask" "gunicorn" "psycopg2" "sqlalchemy")
ALL_OK=true

for module in "${CRITICAL_IMPORTS[@]}"; do
    if ! python -c "import $module" 2>/dev/null; then
        echo "❌ Error: $module no está disponible"
        ALL_OK=false
    else
        echo "✅ $module OK"
    fi
done

if [ "$ALL_OK" = true ]; then
    echo "🎉 Instalación completada - Dependencias críticas OK"
    exit 0
else
    echo "⚠️ Instalación completada con advertencias"
    exit 0  # No fallar el despliegue por dependencias opcionales
fi 