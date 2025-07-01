# ⚡ Inicio Rápido - CI/CD para FERREMAS

## 🎯 Comandos para Ejecutar

### 1. En tu computadora local (Windows):
```bash
# Confirmar que tienes los archivos del CI/CD
git status

# Subir el workflow a GitHub
git add .github/workflows/main.yml
git add requirements.txt
git add *.sh *.md ferremas.service.example
git commit -m "feat: Añadir CI/CD completo con GitHub Actions"
git push origin main
```

### 2. En tu servidor EC2 (conectar via SSH):
```bash
# Conectar al servidor EC2
ssh -i "ferremas-key2.pem" ubuntu@TU_IP_PUBLICA_EC2

# Descargar script de configuración
wget https://raw.githubusercontent.com/f-orellana/FERREMAS/main/setup_ec2.sh
chmod +x setup_ec2.sh

# Ejecutar configuración automática
./setup_ec2.sh
```

### 3. En GitHub (navegador web):
```
1. Ve a tu repositorio: https://github.com/TU_USUARIO/FERREMAS
2. Settings → Secrets and variables → Actions
3. Crear estos 3 secretos:
   
   AWS_HOST = "TU_IP_PUBLICA_EC2"
   AWS_USERNAME = "ubuntu"  
   AWS_SSH_PRIVATE_KEY = [contenido completo de ferremas-key2.pem]
```

### 4. Probar el pipeline:
```bash
# Hacer un cambio pequeño y push
echo "# Test CI/CD" >> README.md
git add README.md
git commit -m "test: Probar pipeline CI/CD"
git push origin main
```

### 5. Verificar que funciona:
```
1. Ve a GitHub → pestaña Actions
2. Verás tu workflow ejecutándose
3. Si todo es verde ✅ = ¡Éxito!
```

## 📋 Archivos Creados

✅ `.github/workflows/main.yml` - Workflow principal
✅ `requirements.txt` - Dependencias actualizadas  
✅ `setup_ec2.sh` - Script de configuración del servidor
✅ `verify_deployment.sh` - Script de verificación
✅ `ferremas.service.example` - Servicio systemd
✅ `GITHUB_ACTIONS_SETUP.md` - Guía completa
✅ `CI_CD_README.md` - Documentación completa

## 🎉 ¡Listo!

Una vez completados estos pasos:
- ✅ Cada push a `main` ejecutará tests automáticamente
- ✅ Si tests pasan, desplegará automáticamente a EC2
- ✅ Recibirás notificaciones del estado del deployment
- ✅ Tu aplicación se mantendrá siempre actualizada

## 🆘 Si algo falla:

1. **Tests fallan**: Revisa los logs en GitHub Actions
2. **SSH falla**: Verifica IP y clave privada en secretos
3. **App no responde**: Ejecuta `./verify_deployment.sh` en EC2
4. **Más ayuda**: Lee `GITHUB_ACTIONS_SETUP.md` 