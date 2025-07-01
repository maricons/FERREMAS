# 🚀 Guía Completa de CI/CD con GitHub Actions para FERREMAS

## 📋 Requisitos Previos

### 1. Servidor AWS EC2 Configurado
Asegúrate de tener tu instancia EC2 lista con:
- Ubuntu 22.04 LTS o superior
- Python 3.9+ instalado
- Git configurado
- Acceso SSH habilitado

### 2. Repositorio GitHub
- Proyecto FERREMAS subido a GitHub
- Permisos de administrador en el repositorio

## 🔧 Paso 0: Preparación del Servidor EC2

### Conectar a tu servidor EC2
```bash
# Conectar via SSH
ssh -i "tu-clave.pem" ubuntu@tu-ec2-ip

# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias del sistema
sudo apt install -y python3 python3-pip python3-venv git nginx postgresql postgresql-contrib
```

### Configurar directorio del proyecto
```bash
# Crear directorio del proyecto
cd /home/ubuntu
git clone https://github.com/TU_USUARIO/FERREMAS.git
cd FERREMAS

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
cd flask-app
pip install -r requirements.txt
```

### Crear servicio systemd (Opcional pero recomendado)
```bash
# Crear archivo de servicio
sudo nano /etc/systemd/system/ferremas.service
```

Contenido del archivo:
```ini
[Unit]
Description=FERREMAS Flask Application
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/FERREMAS/flask-app
Environment=PATH=/home/ubuntu/FERREMAS/venv/bin
ExecStart=/home/ubuntu/FERREMAS/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Habilitar y iniciar servicio
sudo systemctl daemon-reload
sudo systemctl enable ferremas.service
sudo systemctl start ferremas.service
sudo systemctl status ferremas.service
```

## 🔐 Paso 1: Configurar Secretos en GitHub

### 1.1 Generar clave SSH (si no la tienes)
```bash
# En tu máquina local
ssh-keygen -t rsa -b 4096 -C "github-actions@ferremas.com"
```

### 1.2 Copiar clave pública al servidor
```bash
# Copiar clave pública a EC2
ssh-copy-id -i ~/.ssh/tu_clave.pub ubuntu@tu-ec2-ip
```

### 1.3 Configurar secretos en GitHub
1. Ve a tu repositorio en GitHub
2. **Settings** → **Secrets and variables** → **Actions**
3. Crear los siguientes secretos:

| Nombre del Secreto | Descripción | Ejemplo |
|-------------------|-------------|---------|
| `AWS_HOST` | IP pública de tu EC2 | `54.123.456.789` |
| `AWS_USERNAME` | Usuario del servidor | `ubuntu` |
| `AWS_SSH_PRIVATE_KEY` | Contenido completo de tu clave privada | Contenido del archivo `.pem` |

#### Para AWS_SSH_PRIVATE_KEY:
```bash
# Mostrar contenido de la clave privada
cat ~/.ssh/tu_clave.pem
```
Copia todo el contenido (incluyendo `-----BEGIN RSA PRIVATE KEY-----` y `-----END RSA PRIVATE KEY-----`)

## 📁 Paso 2: Crear Estructura de Archivos

### 2.1 Crear directorio .github/workflows
```bash
# En tu proyecto local
mkdir -p .github/workflows
```

### 2.2 Crear archivo main.yml
El archivo ya está creado en `.github/workflows/main.yml` con el workflow completo.

### 2.3 Verificar estructura del proyecto
```
FERREMAS/
├── .github/
│   └── workflows/
│       └── main.yml
├── flask-app/
│   ├── app.py
│   ├── requirements.txt
│   └── ... (otros archivos)
├── tests/
│   ├── test_basic_refactored.py
│   ├── test_webpay_refactored.py
│   ├── test_currency_converter_refactored.py
│   └── test_config.env
├── requirements.txt
└── README.md
```

## 🚀 Paso 3: Desplegar el Workflow

### 3.1 Subir archivos a GitHub
```bash
# En tu proyecto local
git add .github/workflows/main.yml
git add requirements.txt
git add GITHUB_ACTIONS_SETUP.md
git commit -m "feat: Añadir CI/CD completo con GitHub Actions"
git push origin main
```

### 3.2 Verificar ejecución
1. Ve a la pestaña **Actions** en tu repositorio
2. Verás el workflow ejecutándose automáticamente
3. Haz clic en el workflow para ver el progreso en tiempo real

## 📊 Paso 4: Interpretar Resultados

### Estados del Workflow
- ✅ **Verde**: Todo exitoso
- ❌ **Rojo**: Hay errores - revisa los logs
- 🟡 **Amarillo**: En progreso
- ⚪ **Gris**: Cancelado o pendiente

### Estructura del Pipeline
1. **🧪 Tests & Quality Checks**: Ejecuta todos los tests refactorizados
2. **🚀 Deploy to AWS EC2**: Despliega solo si los tests pasan y es rama main
3. **📢 Notifications**: Envía resumen del pipeline

## 🛠️ Paso 5: Troubleshooting

### Error común: SSH Connection Failed
```bash
# Verificar conectividad SSH
ssh -i "tu-clave.pem" ubuntu@tu-ec2-ip

# Verificar formato de clave en GitHub
# Debe incluir header y footer completos
```

### Error común: Service not found
```bash
# En el servidor EC2, verificar servicios
systemctl list-units --type=service | grep ferremas

# Si no existe, el workflow intentará iniciar manualmente
```

### Error común: Permission denied
```bash
# Verificar permisos en el servidor
sudo chown -R ubuntu:ubuntu /home/ubuntu/FERREMAS
chmod +x /home/ubuntu/FERREMAS/flask-app/app.py
```

### Error común: Tests failing
```bash
# Ejecutar tests localmente primero
cd tests
python -m pytest test_basic_refactored.py -v
python -m pytest test_webpay_refactored.py -v
python -m pytest test_currency_converter_refactored.py -v
```

## 🔄 Paso 6: Flujo de Trabajo Diario

### Para desarrollar nueva funcionalidad:
```bash
# 1. Crear nueva rama
git checkout -b feature/nueva-funcionalidad

# 2. Hacer cambios y commit
git add .
git commit -m "feat: nueva funcionalidad"

# 3. Push a la rama
git push origin feature/nueva-funcionalidad

# 4. Crear Pull Request en GitHub
# El workflow ejecutará tests automáticamente

# 5. Si tests pasan, hacer merge a main
# Esto activará el despliegue automático
```

### Para hotfixes urgentes:
```bash
# 1. Cambios directos en main (solo para emergencias)
git checkout main
git pull origin main

# 2. Hacer cambios mínimos
git add .
git commit -m "fix: corrección urgente"

# 3. Push directo a main
git push origin main

# Esto activará testing y despliegue inmediato
```

## 📈 Paso 7: Métricas y Monitoreo

### Métricas disponibles en GitHub Actions:
- ⏱️ Tiempo de ejecución de tests
- 📊 Coverage de código
- 🚀 Tiempo de despliegue
- 📉 Tasa de éxito/fallo

### Logs útiles:
- **Test logs**: Ver detalles de tests que fallan
- **Deployment logs**: Verificar estado del despliegue
- **SSH logs**: Troubleshoot conexión a EC2

## 🔒 Paso 8: Seguridad y Buenas Prácticas

### Variables de entorno sensibles:
```bash
# En el servidor EC2, crear archivo .env para producción
sudo nano /home/ubuntu/FERREMAS/flask-app/.env
```

Contenido del .env de producción:
```bash
FLASK_ENV=production
DEBUG=false
SECRET_KEY=tu_secret_key_super_seguro_aqui
DATABASE_URL=postgresql://usuario:password@host:5432/db
WEBPAY_COMMERCE_CODE=tu_codigo_real
WEBPAY_API_KEY=tu_api_key_real
WEBPAY_ENVIRONMENT=production
```

### Proteger archivos sensibles:
```bash
# Establecer permisos restrictivos
chmod 600 /home/ubuntu/FERREMAS/flask-app/.env
sudo chown ubuntu:ubuntu /home/ubuntu/FERREMAS/flask-app/.env
```

## 🎯 Paso 9: Validación Final

### Checklist de verificación:
- [ ] Workflow ejecuta exitosamente
- [ ] Tests pasan al 100%
- [ ] Despliegue completa sin errores
- [ ] Aplicación responde en el servidor
- [ ] SSL/HTTPS configurado (opcional)
- [ ] Logs de aplicación funcionando
- [ ] Base de datos accesible
- [ ] Backups configurados (recomendado)

### Comandos de verificación:
```bash
# En el servidor EC2
curl http://localhost:5000  # Verificar aplicación local
systemctl status ferremas.service  # Estado del servicio
tail -f /var/log/nginx/access.log  # Logs de Nginx (si aplica)
```

## 🆘 Soporte y Ayuda

### Recursos útiles:
- [Documentación GitHub Actions](https://docs.github.com/en/actions)
- [AWS EC2 User Guide](https://docs.aws.amazon.com/ec2/)
- [Flask Deployment Guide](https://flask.palletsprojects.com/en/3.0.x/deploying/)

### Contacto:
Si tienes problemas, revisa:
1. Logs del workflow en GitHub Actions
2. Logs del servidor en EC2
3. Estado de los servicios systemd
4. Conectividad de red y SSH

---

## 🎉 ¡Felicitaciones!

Si has llegado hasta aquí, tienes un pipeline de CI/CD completamente funcional que:
- ✅ Ejecuta tests automáticamente
- ✅ Despliega solo código que pasa tests
- ✅ Mantiene tu aplicación actualizada
- ✅ Proporciona feedback inmediato
- ✅ Es escalable y mantenible

**¡Tu proyecto FERREMAS ahora tiene un sistema de despliegue profesional!** 🚀 