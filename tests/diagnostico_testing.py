#!/usr/bin/env python
"""
Script de diagnóstico para verificar la configuración de testing de FERREMAS
"""

import os
import sys
from pathlib import Path

def test_python_environment():
    """Verificar entorno Python"""
    print("🔍 DIAGNÓSTICO DEL ENTORNO PYTHON")
    print(f"✅ Python version: {sys.version}")
    print(f"✅ Python executable: {sys.executable}")
    print(f"✅ Current working directory: {os.getcwd()}")
    print()

def test_directory_structure():
    """Verificar estructura de directorios"""
    print("🔍 DIAGNÓSTICO DE ESTRUCTURA DE DIRECTORIOS")
    current_dir = Path.cwd()
    print(f"✅ Directorio actual: {current_dir}")
    
    # Verificar directorios clave
    directories_to_check = [
        "flask-app",
        "tests",
        "flask-app/static",
        "flask-app/templates"
    ]
    
    for dir_name in directories_to_check:
        dir_path = current_dir / dir_name
        if dir_path.exists():
            print(f"✅ {dir_name}: Existe")
        else:
            print(f"❌ {dir_name}: No existe")
    
    # Verificar archivos clave
    files_to_check = [
        "flask-app/app.py",
        "flask-app/__init__.py", 
        "flask-app/models.py",
        "tests/conftest.py",
        "tests/test_config.env"
    ]
    
    for file_name in files_to_check:
        file_path = current_dir / file_name
        if file_path.exists():
            print(f"✅ {file_name}: Existe")
        else:
            print(f"❌ {file_name}: No existe")
    print()

def test_python_path():
    """Verificar PYTHONPATH"""
    print("🔍 DIAGNÓSTICO DE PYTHON PATH")
    print("Python paths actuales:")
    for i, path in enumerate(sys.path):
        print(f"  {i}: {path}")
    
    # Agregar paths necesarios
    project_root = str(Path(__file__).parent.parent)
    flask_app_path = str(Path(__file__).parent.parent / "flask-app")
    
    print(f"\n📁 Project root calculado: {project_root}")
    print(f"📁 Flask-app path calculado: {flask_app_path}")
    
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
        print(f"✅ Agregado project_root al PYTHONPATH")
    
    if flask_app_path not in sys.path:
        sys.path.insert(0, flask_app_path)
        print(f"✅ Agregado flask_app_path al PYTHONPATH")
    print()

def test_environment_variables():
    """Verificar variables de entorno"""
    print("🔍 DIAGNÓSTICO DE VARIABLES DE ENTORNO")
    
    # Cargar variables desde test_config.env
    try:
        from dotenv import load_dotenv
        env_path = Path(__file__).parent / "test_config.env"
        if env_path.exists():
            load_dotenv(env_path)
            print(f"✅ Variables cargadas desde {env_path}")
        else:
            print(f"❌ No se encontró {env_path}")
    except ImportError:
        print("⚠️ python-dotenv no instalado")
    
    # Verificar variables críticas
    critical_vars = [
        "TESTING",
        "DATABASE_URL",
        "SECRET_KEY",
        "WEBPAY_COMMERCE_CODE"
    ]
    
    for var in critical_vars:
        value = os.environ.get(var)
        if value:
            # Ocultar valores sensibles
            if any(keyword in var.lower() for keyword in ['key', 'password', 'secret']):
                display_value = f"{value[:8]}..." if len(value) > 8 else "***"
            else:
                display_value = value
            print(f"✅ {var}: {display_value}")
        else:
            print(f"❌ {var}: No configurada")
    print()

def test_imports():
    """Verificar importaciones"""
    print("🔍 DIAGNÓSTICO DE IMPORTACIONES")
    
    # Cambiar al directorio flask-app temporalmente
    original_cwd = os.getcwd()
    flask_app_dir = Path(__file__).parent.parent / "flask-app"
    
    try:
        # Importaciones básicas
        try:
            import flask
            print(f"✅ Flask {flask.__version__} importado correctamente")
        except ImportError as e:
            print(f"❌ Error importando Flask: {e}")
        
        try:
            import pytest
            print(f"✅ Pytest {pytest.__version__} importado correctamente")
        except ImportError as e:
            print(f"❌ Error importando pytest: {e}")
        
        # Intentar importar flask_app
        print("\n🔄 Intentando importar flask_app...")
        
        # Estrategia 1: Importación directa
        try:
            os.chdir(flask_app_dir)
            from flask_app import models
            print("✅ flask_app.models importado correctamente (estrategia 1)")
            return True
        except ImportError as e1:
            print(f"⚠️ Estrategia 1 falló: {e1}")
        
        # Estrategia 2: Importación específica
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "flask_app", 
                flask_app_dir / "__init__.py"
            )
            if spec and spec.loader:
                flask_app_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(flask_app_module)
                print("✅ flask_app importado correctamente (estrategia 2)")
                return True
        except Exception as e2:
            print(f"⚠️ Estrategia 2 falló: {e2}")
        
        print("❌ No se pudo importar flask_app con ninguna estrategia")
        return False
        
    finally:
        os.chdir(original_cwd)

def test_database_connection():
    """Verificar conexión a base de datos"""
    print("🔍 DIAGNÓSTICO DE BASE DE DATOS")
    
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL no configurada")
        return False
    
    print(f"📁 Database URL: {database_url}")
    
    # Verificar tipo de BD
    if database_url.startswith("postgresql://"):
        print("🐘 PostgreSQL detectado")
        try:
            import psycopg2
            print("✅ psycopg2 disponible")
            
            # Intentar conexión básica
            import urllib.parse
            url = urllib.parse.urlparse(database_url)
            try:
                conn = psycopg2.connect(
                    database=url.path[1:],
                    user=url.username,
                    password=url.password,
                    host=url.hostname,
                    port=url.port
                )
                conn.close()
                print("✅ Conexión PostgreSQL exitosa")
                return True
            except Exception as e:
                print(f"❌ Error conectando a PostgreSQL: {e}")
                return False
                
        except ImportError:
            print("❌ psycopg2 no instalado")
            return False
    
    elif database_url.startswith("sqlite://"):
        print("💾 SQLite detectado")
        try:
            import sqlite3
            print("✅ sqlite3 disponible")
            return True
        except ImportError:
            print("❌ sqlite3 no disponible")
            return False
    
    else:
        print(f"⚠️ Tipo de BD no reconocido: {database_url}")
        return False

def run_sample_test():
    """Ejecutar un test de muestra"""
    print("🔍 EJECUTANDO TEST DE MUESTRA")
    
    try:
        import subprocess
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/test_basic_refactored.py::test_environment_setup", 
            "-v", "--tb=short"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        
        print("STDOUT:")
        print(result.stdout)
        print("\nSTDERR:")
        print(result.stderr)
        print(f"\nReturn code: {result.returncode}")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error ejecutando test: {e}")
        return False

def main():
    """Ejecutar diagnóstico completo"""
    print("=" * 60)
    print("🔧 DIAGNÓSTICO COMPLETO DE TESTING FERREMAS")
    print("=" * 60)
    
    test_python_environment()
    test_directory_structure()
    test_python_path()
    test_environment_variables()
    
    imports_ok = test_imports()
    db_ok = test_database_connection()
    
    print("=" * 60)
    print("📊 RESUMEN DEL DIAGNÓSTICO")
    print("=" * 60)
    
    if imports_ok and db_ok:
        print("✅ Configuración básica correcta")
        print("🚀 Procediendo con test de muestra...")
        test_ok = run_sample_test()
        if test_ok:
            print("\n🎉 ¡DIAGNÓSTICO EXITOSO! Los tests deberían funcionar.")
        else:
            print("\n⚠️ Configuración correcta pero test falló. Revisar logs.")
    else:
        print("❌ Hay problemas en la configuración que requieren atención.")
        
        print("\n🔧 SOLUCIONES SUGERIDAS:")
        if not imports_ok:
            print("  1. Verificar que estás en el directorio raíz del proyecto")
            print("  2. Verificar que flask-app/__init__.py existe")
            print("  3. Intentar: cd flask-app && python -c 'import flask_app'")
        
        if not db_ok:
            print("  4. Verificar credenciales de PostgreSQL")
            print("  5. Crear base de datos 'ferremas_test'")
            print("  6. O usar SQLite: cambiar DATABASE_URL en test_config.env")

if __name__ == "__main__":
    main() 