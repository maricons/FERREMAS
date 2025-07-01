#!/bin/bash

# 🚨 Script de Emergencia para EC2 - FERREMAS
# Ejecutar este script en EC2 para resolver el problema de git y desplegar

set -e

echo "🚨 Script de Emergencia para EC2 - FERREMAS"
echo "⏰ Iniciado: $(date)"
echo "👤 Usuario: $(whoami)"
echo "📂 Directorio actual: $(pwd)"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Función para verificar si estamos en el directorio correcto
check_directory() {
    if [ ! -d "flask-app" ] || [ ! -f "README.md" ]; then
        print_error "No estás en el directorio correcto de FERREMAS"
        echo "Navegando a /home/ubuntu/FERREMAS..."
        cd /home/ubuntu/FERREMAS
        if [ ! -d "flask-app" ]; then
            print_error "Directorio FERREMAS no encontrado en /home/ubuntu/"
            exit 1
        fi
    fi
    print_status "Directorio correcto verificado"
}

# Función para backup
create_backup() {
    print_status "Creando backup de seguridad..."
    BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
    
    if [ -d "flask-app" ]; then
        cp -r flask-app "$BACKUP_DIR"
        print_status "Backup creado en: $BACKUP_DIR"
    else
        print_warning "No se encontró directorio flask-app para backup"
    fi
}

# Función para resolver problema de git
fix_git_divergence() {
    print_status "Resolviendo problema de git..."
    
    # Verificar estado del repositorio
    echo "🔍 Estado actual del repositorio:"
    git status
    
    # Guardar cambios locales
    print_status "Guardando cambios locales..."
    git stash push -m "Backup automático antes de sincronizar - $(date)"
    
    # Obtener últimos cambios
    print_status "Obteniendo últimos cambios..."
    git fetch origin
    
    # Resetear a la versión remota
    print_status "Sincronizando con origin/main..."
    git reset --hard origin/main
    
    print_status "Repositorio sincronizado exitosamente"
}

# Función para manejar entorno virtual
setup_venv() {
    print_status "Configurando entorno virtual..."
    
    if [ ! -d "venv" ]; then
        print_status "Creando entorno virtual..."
        python3 -m venv venv
    fi
    
    print_status "Activando entorno virtual..."
    source venv/bin/activate
    
    print_status "Actualizando pip..."
    python -m pip install --upgrade pip
}

# Función para instalar dependencias
install_dependencies() {
    print_status "Instalando dependencias con estrategia robusta..."
    
    cd flask-app
    
    # Usar script robusto si existe
    if [ -f "install_dependencies.sh" ]; then
        print_status "Usando script de instalación robusta..."
        chmod +x install_dependencies.sh
        ./install_dependencies.sh || print_warning "Script completado con advertencias"
    elif [ -f "requirements.minimal.txt" ]; then
        print_status "Usando requirements mínimo..."
        timeout 180 pip install --no-cache-dir -r requirements.minimal.txt || print_warning "Error en requirements mínimo"
    elif [ -f "requirements.txt" ]; then
        print_status "Instalando dependencias críticas primero..."
        # Instalar solo lo crítico
        pip install --no-cache-dir Flask==3.1.0 gunicorn==23.0.0 psycopg2-binary==2.9.10 || print_warning "Error en dependencias críticas"
        # Intentar el resto con timeout
        timeout 300 pip install --no-cache-dir -r requirements.txt || print_warning "Algunas dependencias no se instalaron"
    else
        print_warning "No se encontraron archivos de requirements"
    fi
    
    # Verificar que lo crítico esté instalado
    python -c "import flask, gunicorn, psycopg2; print('✅ Dependencias críticas verificadas')" || print_error "Dependencias críticas faltantes"
    
    cd ..
}

# Función para manejar servicios
manage_services() {
    print_status "Gestionando servicios..."
    
    # Verificar servicios disponibles
    if systemctl list-units --full -all | grep -q "ferremas.service"; then
        print_status "Reiniciando servicio ferremas..."
        sudo systemctl restart ferremas.service
        sudo systemctl status ferremas.service --no-pager -l
    elif systemctl list-units --type=service | grep -q gunicorn; then
        print_status "Reiniciando servicio gunicorn..."
        sudo systemctl restart gunicorn
        sudo systemctl status gunicorn --no-pager -l
    else
        print_warning "No se encontraron servicios systemd conocidos"
    fi
    
    # Reiniciar nginx si existe
    if systemctl is-active --quiet nginx; then
        print_status "Reiniciando nginx..."
        sudo systemctl reload nginx
    fi
    
    # Verificar procesos Python
    FLASK_PIDS=$(pgrep -f "python.*app.py\|gunicorn.*app\|flask run" || true)
    if [ ! -z "$FLASK_PIDS" ]; then
        print_status "Procesos Python encontrados: $FLASK_PIDS"
    fi
}

# Función para verificar salud de la aplicación
health_check() {
    print_status "Verificando salud de la aplicación..."
    sleep 10
    
    # Verificar servicios
    SERVICE_OK=false
    if systemctl is-active --quiet ferremas.service; then
        print_status "Servicio ferremas.service activo"
        SERVICE_OK=true
    elif systemctl is-active --quiet gunicorn; then
        print_status "Servicio gunicorn activo"  
        SERVICE_OK=true
    fi
    
    # Verificar conectividad
    APP_RESPONDING=false
    for port in 80 5000 8000 3000; do
        if curl -f -s -m 5 -o /dev/null "http://localhost:$port" 2>/dev/null; then
            print_status "Aplicación respondiendo en puerto $port"
            APP_RESPONDING=true
            break
        fi
    done
    
    # Resumen
    echo "📊 Resumen del estado:"
    echo "   - Servicios systemd: $($SERVICE_OK && echo '✅' || echo '⚠️')"
    echo "   - Conectividad HTTP: $($APP_RESPONDING && echo '✅' || echo '⚠️')"
    
    if [ "$SERVICE_OK" = true ] || [ "$APP_RESPONDING" = true ]; then
        print_status "Aplicación funcionando correctamente"
        return 0
    else
        print_warning "Aplicación puede no estar respondiendo correctamente"
        return 1
    fi
}

# Función principal
main() {
    echo "🚀 Iniciando proceso de reparación..."
    
    # Verificar directorio
    check_directory
    
    # Crear backup
    create_backup
    
    # Resolver problema de git
    fix_git_divergence
    
    # Configurar entorno virtual
    setup_venv
    
    # Instalar dependencias
    install_dependencies
    
    # Gestionar servicios
    manage_services
    
    # Verificar salud
    if health_check; then
        print_status "🎉 Despliegue manual completado exitosamente!"
    else
        print_warning "🔧 Despliegue completado con advertencias"
        echo "📋 Logs disponibles en:"
        echo "   - sudo journalctl -u ferremas.service -f"
        echo "   - sudo journalctl -u gunicorn -f"
        echo "   - tail -f /home/ubuntu/FERREMAS/flask-app/app.log"
    fi
    
    echo "⏰ Finalizado: $(date)"
    echo "📚 Para más información, consulta los logs del sistema"
}

# Ejecutar función principal
main "$@" 