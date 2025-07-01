#!/bin/bash

# 🚀 Script de Configuración Automática para EC2 - FERREMAS
# Configura completamente el servidor AWS EC2 para despliegue

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

# Verificar que se ejecuta como usuario ubuntu
if [ "$USER" != "ubuntu" ]; then
    print_error "Este script debe ejecutarse como usuario 'ubuntu'"
    print_info "Ejecutar: sudo su - ubuntu && ./setup_ec2.sh"
    exit 1
fi

print_header "CONFIGURACIÓN AUTOMÁTICA DE EC2 PARA FERREMAS"
echo "Servidor: $(hostname)"
echo "Usuario: $(whoami)"
echo "Fecha: $(date)"

# Variables configurables
GITHUB_REPO="https://github.com/TU_USUARIO/FERREMAS.git"  # Cambiar por tu repo
DB_NAME="ferremas_db"
DB_USER="ferremas"
DB_PASSWORD=$(openssl rand -base64 32 | tr -d '=+/' | cut -c1-20)  # Generar contraseña aleatoria
PROJECT_DIR="/home/ubuntu/FERREMAS"

print_warning "IMPORTANTE: Asegúrate de cambiar GITHUB_REPO por tu repositorio real"
print_info "Repositorio configurado: $GITHUB_REPO"
print_success "Contraseña de BD generada: $DB_PASSWORD"
print_warning "IMPORTANTE: Guarda esta contraseña en un lugar seguro"

# Solicitar confirmación
read -p "¿Continuar con la configuración? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_info "Configuración cancelada"
    exit 0
fi

# 1. Actualizar sistema
print_header "1. ACTUALIZANDO SISTEMA"
sudo apt update && sudo apt upgrade -y
print_success "Sistema actualizado"

# 2. Instalar dependencias del sistema
print_header "2. INSTALANDO DEPENDENCIAS DEL SISTEMA"
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    wget \
    nginx \
    postgresql \
    postgresql-contrib \
    redis-server \
    supervisor \
    htop \
    tree \
    unzip
print_success "Dependencias del sistema instaladas"

# 3. Configurar PostgreSQL
print_header "3. CONFIGURANDO POSTGRESQL"
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Crear usuario y base de datos
sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
sudo -u postgres psql -c "ALTER USER $DB_USER CREATEDB;"

print_success "PostgreSQL configurado"
print_info "Base de datos: $DB_NAME"
print_info "Usuario: $DB_USER"

# 4. Configurar Redis
print_header "4. CONFIGURANDO REDIS"
sudo systemctl start redis-server
sudo systemctl enable redis-server
print_success "Redis configurado"

# 5. Configurar Git (solicitar credenciales)
print_header "5. CONFIGURANDO GIT"
read -p "Ingresa tu nombre para Git: " git_name
read -p "Ingresa tu email para Git: " git_email

git config --global user.name "$git_name"
git config --global user.email "$git_email"
print_success "Git configurado"

# 6. Clonar repositorio
print_header "6. CLONANDO REPOSITORIO"
if [ -d "$PROJECT_DIR" ]; then
    print_warning "El directorio $PROJECT_DIR ya existe. Eliminando..."
    rm -rf "$PROJECT_DIR"
fi

# Solicitar URL del repositorio si no está configurada
if [[ "$GITHUB_REPO" == *"TU_USUARIO"* ]]; then
    read -p "Ingresa la URL completa de tu repositorio GitHub: " GITHUB_REPO
fi

git clone "$GITHUB_REPO" "$PROJECT_DIR"
cd "$PROJECT_DIR"
print_success "Repositorio clonado"

# 7. Crear entorno virtual
print_header "7. CONFIGURANDO ENTORNO VIRTUAL"
python3 -m venv venv
source venv/bin/activate

# Actualizar pip
pip install --upgrade pip
print_success "Entorno virtual creado"

# 8. Instalar dependencias de Python
print_header "8. INSTALANDO DEPENDENCIAS DE PYTHON"
cd flask-app

# Instalar desde requirements.txt si existe
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_success "Dependencias instaladas desde requirements.txt"
else
    print_warning "requirements.txt no encontrado. Instalando dependencias básicas..."
    pip install flask flask-sqlalchemy flask-migrate psycopg2-binary python-dotenv requests gunicorn
fi

# 9. Configurar variables de entorno
print_header "9. CONFIGURANDO VARIABLES DE ENTORNO"
cat > .env << EOF
# Configuración de producción FERREMAS
FLASK_APP=app.py
FLASK_ENV=production
DEBUG=false

# Base de datos
DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME

# Seguridad
SECRET_KEY=$(openssl rand -hex 32)

# Redis
REDIS_URL=redis://localhost:6379/0

# Email (configurar con tus credenciales)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=tu_email@gmail.com
MAIL_PASSWORD=tu_app_password

# Webpay (configurar con tus credenciales)
WEBPAY_ENVIRONMENT=production
WEBPAY_COMMERCE_CODE=tu_codigo_comercio
WEBPAY_API_KEY=tu_api_key

# Logging
LOG_LEVEL=INFO
EOF

chmod 600 .env
print_success "Variables de entorno configuradas"
print_warning "IMPORTANTE: Edita el archivo .env con tus credenciales reales"

# 10. Inicializar base de datos
print_header "10. INICIALIZANDO BASE DE DATOS"
export FLASK_APP=app.py
export DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME

# Intentar ejecutar migraciones si existen
if [ -d "migrations" ]; then
    flask db upgrade
    print_success "Migraciones ejecutadas"
else
    print_warning "No se encontraron migraciones. Inicializando base de datos..."
    flask db init
    flask db migrate -m "Initial migration"
    flask db upgrade
fi

# 11. Configurar servicio systemd
print_header "11. CONFIGURANDO SERVICIO SYSTEMD"
sudo tee /etc/systemd/system/ferremas.service > /dev/null << EOF
[Unit]
Description=FERREMAS - E-commerce Flask Application
After=network.target postgresql.service redis.service
Wants=postgresql.service redis.service

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=$PROJECT_DIR/flask-app
Environment=PATH=$PROJECT_DIR/venv/bin
Environment=FLASK_APP=app.py
Environment=FLASK_ENV=production

ExecStart=$PROJECT_DIR/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 3 --timeout 120 app:app
Restart=always
RestartSec=10

StandardOutput=journal
StandardError=journal
SyslogIdentifier=ferremas

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable ferremas.service
print_success "Servicio systemd configurado"

# 12. Configurar Nginx (opcional)
print_header "12. CONFIGURANDO NGINX"
sudo tee /etc/nginx/sites-available/ferremas > /dev/null << EOF
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    location /static {
        alias $PROJECT_DIR/flask-app/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/ferremas /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx
print_success "Nginx configurado"

# 13. Configurar firewall
print_header "13. CONFIGURANDO FIREWALL"
sudo ufw allow 22/tcp  # SSH
sudo ufw allow 80/tcp  # HTTP
sudo ufw allow 443/tcp # HTTPS
sudo ufw --force enable
print_success "Firewall configurado"

# 14. Iniciar servicios
print_header "14. INICIANDO SERVICIOS"
sudo systemctl start ferremas.service
sleep 5

# Verificar estado
if systemctl is-active --quiet ferremas.service; then
    print_success "Servicio FERREMAS iniciado correctamente"
else
    print_error "Error al iniciar servicio FERREMAS"
    print_info "Logs del servicio:"
    sudo journalctl -u ferremas.service -n 10 --no-pager
fi

# 15. Prueba de conectividad
print_header "15. VERIFICANDO CONECTIVIDAD"
sleep 10

if curl -f -s -m 10 http://localhost:5000 > /dev/null; then
    print_success "Aplicación responde correctamente"
else
    print_warning "La aplicación no responde. Verificando..."
    
    # Mostrar logs para debugging
    sudo journalctl -u ferremas.service -n 20 --no-pager
fi

# 16. Resumen final
print_header "CONFIGURACIÓN COMPLETADA"
echo ""
print_success "✅ Sistema actualizado"
print_success "✅ Dependencias instaladas"
print_success "✅ PostgreSQL configurado"
print_success "✅ Redis configurado"
print_success "✅ Repositorio clonado"
print_success "✅ Entorno virtual creado"
print_success "✅ Servicio systemd configurado"
print_success "✅ Nginx configurado"
print_success "✅ Firewall configurado"

echo ""
print_header "PRÓXIMOS PASOS"
echo "1. Editar archivo .env con tus credenciales reales:"
echo "   nano $PROJECT_DIR/flask-app/.env"
echo ""
echo "2. Configurar secretos en GitHub Actions:"
echo "   - AWS_HOST: $(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo 'IP_DE_TU_EC2')"
echo "   - AWS_USERNAME: ubuntu"
echo "   - AWS_SSH_PRIVATE_KEY: (contenido de tu clave .pem)"
echo ""
echo "3. Verificar servicios:"
echo "   sudo systemctl status ferremas.service"
echo "   sudo systemctl status nginx"
echo "   sudo systemctl status postgresql"
echo ""
echo "4. Ver logs en tiempo real:"
echo "   sudo journalctl -u ferremas.service -f"
echo ""
echo "5. Probar aplicación:"
echo "   curl http://localhost"
echo ""

print_header "INFORMACIÓN DEL SERVIDOR"
echo "IP pública: $(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo 'No disponible')"
echo "Directorio del proyecto: $PROJECT_DIR"
echo "Usuario de base de datos: $DB_USER"
echo "Base de datos: $DB_NAME"
echo ""

print_success "🎉 ¡Configuración de EC2 completada!"
print_info "Tu aplicación FERREMAS está lista para CI/CD con GitHub Actions" 