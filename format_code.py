#!/usr/bin/env python3
"""
Script para formatear automáticamente el código del proyecto FERREMAS
"""
import subprocess
import sys
import os

def run_command(command, description):
    """Ejecuta un comando y maneja errores"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completado exitosamente")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print(f"❌ Error en {description}:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error ejecutando {description}: {e}")
        return False

def main():
    """Función principal del script de formateo"""
    print("🎨 FERREMAS - Formateo Automático de Código")
    print("=" * 50)
    
    # Verificar que las herramientas estén instaladas
    print("🔍 Verificando herramientas de formateo...")
    
    # Verificar isort
    isort_check = subprocess.run("isort --version", shell=True, capture_output=True)
    if isort_check.returncode != 0:
        print("❌ isort no está instalado. Instalando...")
        if not run_command("pip install isort", "Instalando isort"):
            print("❌ No se pudo instalar isort")
            return False
    else:
        print("✅ isort ya está instalado")
    
    # Verificar black
    black_check = subprocess.run("black --version", shell=True, capture_output=True)
    if black_check.returncode != 0:
        print("❌ black no está instalado. Instalando...")
        if not run_command("pip install black", "Instalando black"):
            print("❌ No se pudo instalar black")
            return False
    else:
        print("✅ black ya está instalado")
    
    print("\n🚀 Iniciando formateo de código...")
    
    # Paso 1: Ordenar imports con isort
    if not run_command("isort flask_app/ tests/", "Ordenando imports con isort"):
        print("❌ Falló el ordenamiento de imports")
        return False
    
    # Paso 2: Formatear código con black
    if not run_command("black flask_app/ tests/", "Formateando código con black"):
        print("❌ Falló el formateo de código")
        return False
    
    # Paso 3: Verificar que todo esté correcto
    print("\n🔍 Verificando que el formateo sea correcto...")
    
    # Verificar black
    if not run_command("black --check flask_app/ tests/", "Verificando formato con black"):
        print("❌ El código no cumple con el formato de black")
        return False
    
    # Verificar isort
    if not run_command("isort --check-only flask_app/ tests/", "Verificando imports con isort"):
        print("❌ Los imports no están correctamente ordenados")
        return False
    
    print("\n🎉 ¡Formateo completado exitosamente!")
    print("✅ Todo el código cumple con los estándares de formato")
    print("✅ Puedes hacer commit y push de los cambios")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 