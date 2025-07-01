#!/bin/bash

# 🔍 Script de Verificación de Despliegue FERREMAS
# Diagnostica problemas comunes en el servidor EC2

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funciones de utilidad
print_header() {
    echo -e "\n${BLUE}=== $1 ===${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Variables
PROJECT_DIR="/home/ubuntu/FERREMAS"
FLASK_APP_DIR="$PROJECT_DIR/flask-app"
VENV_DIR="$PROJECT_DIR/venv"
SERVICE_NAME="ferremas.service"

print_header "VERIFICACIÓN DE DESPLIEGUE FERREMAS"
echo "Servidor: $(hostname)"
echo "Usuario: $(whoami)"
echo "Fecha: $(date)"
echo "Directorio del proyecto: $PROJECT_DIR"

# 1. Verificar estructura de directorios
print_header "1. ESTRUCTURA DE DIRECTORIOS"
if [ -d "$PROJECT_DIR" ]; then
    print_success "Directorio del proyecto existe"
    ls -la "$PROJECT_DIR"
else
    print_error "Directorio del proyecto no existe: $PROJECT_DIR"
    exit 1
fi

if [ -d "$FLASK_APP_DIR" ]; then
    print_success "Directorio flask-app existe"
else
    print_error "Directorio flask-app no existe: $FLASK_APP_DIR"
    exit 1
fi

# 2. Verificar entorno virtual
print_header "2. ENTORNO VIRTUAL"
if [ -d "$VENV_DIR" ]; then
    print_success "Entorno virtual existe"
    
    # Activar entorno virtual
    source "$VENV_DIR/bin/activate"
    
    # Verificar Python
    python_version=$(python --version 2>&1)
    print_info "Versión de Python: $python_version"
    
    # Verificar pip
    pip_version=$(pip --version 2>&1)
    print_info "Versión de pip: $pip_version"
    
    # Verificar Flask
    if python -c "import flask" 2>/dev/null; then
        flask_version=$(python -c "import flask; print(flask.__version__)" 2>/dev/null)
        print_success "Flask instalado: $flask_version"
    else
        print_error "Flask no está instalado"
    fi
    
else
    print_error "Entorno virtual no existe: $VENV_DIR"
    print_info "Para crear: python3 -m venv $VENV_DIR"
fi

# 3. Verificar dependencias
print_header "3. DEPENDENCIAS"
cd "$FLASK_APP_DIR"

if [ -f "requirements.txt" ]; then
    print_success "requirements.txt encontrado"
    print_info "Verificando dependencias instaladas..."
    
    # Verificar algunas dependencias críticas
    dependencies=("flask" "psycopg2-binary" "requests" "python-dotenv")
    
    for dep in "${dependencies[@]}"; do
        if python -c "import $dep" 2>/dev/null; then
            print_success "$dep instalado"
        else
            print_error "$dep NO instalado"
        fi
    done
else
    print_error "requirements.txt no encontrado"
fi

# 4. Verificar archivos de aplicación
print_header "4. ARCHIVOS DE APLICACIÓN"
files=("app.py" "models.py" "auth.py")

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        print_success "$file existe"
    else
        print_warning "$file no encontrado"
    fi
done

# 5. Verificar base de datos
print_header "5. BASE DE DATOS"
if command -v psql &> /dev/null; then
    print_success "PostgreSQL client instalado"
    
    # Intentar conectar a la base de datos
    if PGPASSWORD=ferremas123 psql -h localhost -U ferremas -d ferremas_db -c "\q" 2>/dev/null; then
        print_success "Conexión a base de datos exitosa"
        
        # Verificar tablas
        tables=$(PGPASSWORD=ferremas123 psql -h localhost -U ferremas -d ferremas_db -t -c "SELECT tablename FROM pg_tables WHERE schemaname = 'public';" 2>/dev/null | wc -l)
        print_info "Número de tablas: $tables"
    else
        print_error "No se puede conectar a la base de datos"
        print_info "Verificar: usuario=ferremas, password=ferremas123, db=ferremas_db"
    fi
else
    print_warning "PostgreSQL client no instalado"
fi

# 6. Verificar servicio systemd
print_header "6. SERVICIO SYSTEMD"
if systemctl list-units --full -all | grep -Fq "$SERVICE_NAME"; then
    print_success "Servicio $SERVICE_NAME existe"
    
    # Estado del servicio
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        print_success "Servicio está ACTIVO"
    else
        print_error "Servicio está INACTIVO"
        print_info "Para iniciar: sudo systemctl start $SERVICE_NAME"
    fi
    
    # Estado de habilitación
    if systemctl is-enabled --quiet "$SERVICE_NAME"; then
        print_success "Servicio está HABILITADO"
    else
        print_warning "Servicio NO está habilitado"
        print_info "Para habilitar: sudo systemctl enable $SERVICE_NAME"
    fi
    
    # Últimos logs
    print_info "Últimos logs del servicio:"
    sudo journalctl -u "$SERVICE_NAME" -n 5 --no-pager
    
else
    print_error "Servicio $SERVICE_NAME no existe"
    print_info "Crear servicio con: sudo cp ferremas.service.example /etc/systemd/system/$SERVICE_NAME"
fi

# 7. Verificar conectividad de red
print_header "7. CONECTIVIDAD DE RED"
ports=(5000 80 443 5432)

for port in "${ports[@]}"; do
    if netstat -tuln | grep ":$port " > /dev/null 2>&1; then
        print_success "Puerto $port está en uso"
    else
        print_warning "Puerto $port NO está en uso"
    fi
done

# 8. Verificar aplicación Flask
print_header "8. APLICACIÓN FLASK"
test_ports=(5000 8000 3000)

for port in "${test_ports[@]}"; do
    if curl -f -s -m 5 "http://localhost:$port" > /dev/null 2>&1; then
        print_success "Aplicación responde en puerto $port"
        response_code=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:$port")
        print_info "Código de respuesta: $response_code"
        break
    else
        print_warning "Aplicación NO responde en puerto $port"
    fi
done

# 9. Verificar logs
print_header "9. LOGS DE APLICACIÓN"
log_files=("../app.log" "app.log" "/var/log/ferremas.log")

for log_file in "${log_files[@]}"; do
    if [ -f "$log_file" ]; then
        print_success "Log encontrado: $log_file"
        print_info "Últimas 3 líneas:"
        tail -n 3 "$log_file"
        break
    fi
done

# 10. Verificar Git
print_header "10. REPOSITORIO GIT"
cd "$PROJECT_DIR"

if [ -d ".git" ]; then
    print_success "Repositorio Git inicializado"
    
    # Branch actual
    current_branch=$(git branch --show-current)
    print_info "Branch actual: $current_branch"
    
    # Último commit
    last_commit=$(git log -1 --pretty=format:"%h - %s (%cr)")
    print_info "Último commit: $last_commit"
    
    # Estado del repositorio
    if git diff --quiet; then
        print_success "Repositorio limpio (sin cambios)"
    else
        print_warning "Hay cambios sin commit"
    fi
else
    print_error "No es un repositorio Git"
fi

# 11. Verificar variables de entorno
print_header "11. VARIABLES DE ENTORNO"
env_vars=("FLASK_APP" "FLASK_ENV" "DATABASE_URL" "SECRET_KEY")

for var in "${env_vars[@]}"; do
    if [ -n "${!var}" ]; then
        print_success "$var está definida"
    else
        print_warning "$var NO está definida"
    fi
done

# 12. Verificar espacio en disco
print_header "12. ESPACIO EN DISCO"
df_output=$(df -h / | tail -1)
print_info "Espacio en disco: $df_output"

used_percent=$(echo "$df_output" | awk '{print $5}' | sed 's/%//')
if [ "$used_percent" -lt 80 ]; then
    print_success "Espacio en disco suficiente ($used_percent% usado)"
else
    print_warning "Espacio en disco limitado ($used_percent% usado)"
fi

# 13. Verificar memoria
print_header "13. MEMORIA"
memory_info=$(free -h | grep ^Mem)
print_info "Memoria: $memory_info"

# 14. Procesos Python
print_header "14. PROCESOS PYTHON"
python_processes=$(ps aux | grep python | grep -v grep | wc -l)
print_info "Procesos Python ejecutándose: $python_processes"

if [ "$python_processes" -gt 0 ]; then
    print_info "Procesos Python:"
    ps aux | grep python | grep -v grep | head -5
fi

# Resumen final
print_header "RESUMEN DE VERIFICACIÓN"
echo "✅ Elementos verificados exitosamente"
echo "⚠️  Elementos con advertencias"
echo "❌ Elementos con errores"
echo ""
print_info "Para más detalles, revisa cada sección arriba"
print_info "Para logs detallados: sudo journalctl -u $SERVICE_NAME -f"
print_info "Para reiniciar servicio: sudo systemctl restart $SERVICE_NAME"

echo ""
echo "🎯 Verificación completada - $(date)" 