# 🚨 Troubleshooting: Problema de Despliegue en AWS EC2

## 📋 **Problema Identificado**

### Error Original:
```bash
Your branch and 'origin/main' have diverged,
and have 9 and 21 different commits each, respectively.
fatal: Need to specify how to reconcile divergent branches.
```

### Causa Raíz:
- El repositorio en EC2 tiene cambios locales que no están en GitHub
- GitHub tiene commits nuevos que no están en EC2
- Las ramas han divergido y Git no sabe cómo reconciliarlas

## 🛠️ **Soluciones Implementadas**

### 1. **Corrección del Workflow CI/CD**

**Archivo modificado:** `.github/workflows/main.yml`

**Cambios principales:**
- Detección automática de ramas divergentes
- Respaldo automático de cambios locales con `git stash`
- Sincronización forzada con `git reset --hard origin/main`
- Manejo robusto de servicios (ferremas.service, gunicorn, nginx)
- Verificación mejorada de salud de la aplicación

### 2. **Script de Emergencia para EC2**

**Archivo creado:** `fix_ec2_deployment.sh`

**Funcionalidades:**
- Resolución automática del problema de Git
- Backup de seguridad antes de cambios
- Configuración de entorno virtual
- Gestión de servicios systemd
- Verificación de salud de la aplicación

## 🚀 **Solución Inmediata (Ejecutar en EC2)**

### Paso 1: Descargar y ejecutar el script de emergencia

```bash
# Conectar a EC2
ssh -i ~/.ssh/ferremas-key-flask.pem ubuntu@18.221.30.59

# Navegar al directorio del proyecto
cd /home/ubuntu/FERREMAS

# Descargar el script (si no está disponible, crearlo manualmente)
curl -o fix_ec2_deployment.sh https://raw.githubusercontent.com/maricons/FERREMAS/main/fix_ec2_deployment.sh

# Dar permisos de ejecución
chmod +x fix_ec2_deployment.sh

# Ejecutar el script
./fix_ec2_deployment.sh
```

### Paso 2: Solución manual alternativa

```bash
# 1. Navegar al directorio
cd /home/ubuntu/FERREMAS

# 2. Backup de seguridad
cp -r flask-app backup_manual_$(date +%Y%m%d_%H%M%S)

# 3. Resolver divergencia de Git
git fetch origin
git stash push -m "Backup antes de sincronizar - $(date)"
git reset --hard origin/main

# 4. Actualizar dependencias
cd flask-app
source ../venv/bin/activate || python3 -m venv ../venv && source ../venv/bin/activate
pip install -r requirements.txt

# 5. Reiniciar servicios
sudo systemctl restart gunicorn || sudo systemctl restart ferremas.service
sudo systemctl reload nginx

# 6. Verificar estado
systemctl status gunicorn
curl http://localhost
```

## 🔍 **Verificación Post-Despliegue**

### Comandos de diagnóstico:

```bash
# Verificar servicios
systemctl status gunicorn
systemctl status nginx
systemctl status ferremas.service

# Verificar procesos Python
ps aux | grep python
ps aux | grep gunicorn

# Verificar conectividad
curl -I http://localhost
curl -I http://18.221.30.59

# Verificar logs
sudo journalctl -u gunicorn -f
sudo journalctl -u nginx -f
tail -f /home/ubuntu/FERREMAS/flask-app/app.log
```

## 🎯 **Mejoras Implementadas en el Workflow**

### Antes:
- Fallo completo si hay divergencia de Git
- Manejo básico de servicios
- Verificación simple de salud

### Después:
- **Resolución automática** de divergencias de Git
- **Backup automático** de cambios locales
- **Detección inteligente** de servicios (ferremas.service, gunicorn, nginx)
- **Verificación robusta** de salud con múltiples criterios
- **Manejo de errores** mejorado sin fallos críticos

## 📊 **Configuración de Servicios Detectada**

Basado en el mensaje del usuario, la configuración actual en EC2 incluye:
- ✅ **Nginx** como servidor web/proxy reverso
- ✅ **Gunicorn** como servidor WSGI para Python
- ✅ **Systemd** para gestión de servicios
- ✅ **PostgreSQL** como base de datos

## 🔧 **Monitoreo Continuo**

### Comandos útiles para monitoreo:

```bash
# Estado de todos los servicios relacionados
systemctl status nginx gunicorn ferremas.service

# Logs en tiempo real
sudo journalctl -u gunicorn -u nginx -f

# Verificar puertos en uso
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :5000

# Verificar procesos Python
ps aux | grep -E "(python|gunicorn|flask)"
```

## 🎉 **Resultado Esperado**

Después de aplicar estas correcciones:

1. ✅ **Git** se sincroniza automáticamente
2. ✅ **Servicios** se reinician correctamente
3. ✅ **Aplicación** responde en el puerto correcto
4. ✅ **CI/CD** funciona sin intervención manual
5. ✅ **Backups** automáticos preservan cambios locales

## 📞 **Soporte Adicional**

Si el problema persiste:

1. **Verificar credenciales SSH** en GitHub Secrets
2. **Confirmar conectividad** a EC2
3. **Revisar logs** del servidor
4. **Ejecutar script de emergencia** manualmente
5. **Contactar** para troubleshooting avanzado

---

**Última actualización:** $(date)
**Versión del documento:** 1.0 