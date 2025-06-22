#!/usr/bin/env python3
"""
Script para arreglar automáticamente errores de linting en el proyecto FERREMAS
"""
import os
import re
import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Ejecuta un comando y maneja errores"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completado exitosamente")
            return result.stdout
        else:
            print(f"❌ Error en {description}:")
            print(result.stderr)
            return None
    except Exception as e:
        print(f"❌ Error ejecutando {description}: {e}")
        return None

def fix_imports(file_path):
    """Arregla imports no utilizados y ordena imports"""
    print(f"🔧 Arreglando imports en {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Lista de imports no utilizados detectados
        unused_imports = [
            "from flask_sqlalchemy import SQLAlchemy",
            "from .default import *",
            "from .models import CartItem, Order, OrderItem, Product, User, WebpayTransaction",
            "import json",
            "from flask_mail import Message",
            "from werkzeug.security import check_password_hash, generate_password_hash",
            "from .currency_converter import CurrencyConverter",
            "from .models import User",
            "import os",
            "from datetime import datetime",
            "from datetime import datetime",
            "import pytest",
            "from flask import get_flashed_messages, url_for",
            "from werkzeug.security import check_password_hash, generate_password_hash",
            "from flask_app.auth import auth_bp",
            "from datetime import datetime",
            "import pytest",
            "import pytest",
            "from decimal import Decimal",
            "from flask import url_for",
            "from werkzeug.security import generate_password_hash",
            "from flask_app import Category, Product",
        ]
        
        # Remover imports no utilizados
        for unused_import in unused_imports:
            if unused_import in content:
                # Remover línea completa si es un import simple
                lines = content.split('\n')
                new_lines = []
                for line in lines:
                    if unused_import not in line or not line.strip().startswith(('import ', 'from ')):
                        new_lines.append(line)
                content = '\n'.join(new_lines)
        
        # Escribir archivo corregido
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Imports arreglados en {file_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error arreglando imports en {file_path}: {e}")
        return False

def fix_long_lines(file_path):
    """Arregla líneas demasiado largas"""
    print(f"🔧 Arreglando líneas largas en {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        new_lines = []
        
        for line in lines:
            if len(line) > 88:
                # Intentar romper líneas largas de manera inteligente
                if '=' in line and len(line) > 88:
                    # Para asignaciones
                    parts = line.split('=', 1)
                    if len(parts) == 2:
                        new_line = f"{parts[0].rstrip()}\n    = {parts[1].lstrip()}"
                        new_lines.append(new_line)
                        continue
                elif '(' in line and ')' in line and len(line) > 88:
                    # Para llamadas de función
                    # Simplificar: solo agregar un salto de línea después de la coma
                    new_line = line.replace(', ', ',\n    ')
                    new_lines.append(new_line)
                    continue
                else:
                    # Para otros casos, simplemente agregar un salto de línea
                    new_line = line[:88] + '\n    ' + line[88:]
                    new_lines.append(new_line)
                    continue
            
            new_lines.append(line)
        
        # Escribir archivo corregido
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
        
        print(f"✅ Líneas largas arregladas en {file_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error arreglando líneas largas en {file_path}: {e}")
        return False

def fix_f_strings(file_path):
    """Arregla f-strings sin placeholders"""
    print(f"🔧 Arreglando f-strings en {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Buscar f-strings sin placeholders y convertirlos a strings normales
        # Patrón: f"texto" o f'texto' sin {}
        pattern = r'f["\']([^"\']*)["\']'
        
        def replace_f_string(match):
            content_str = match.group(1)
            quote = match.group(0)[1]  # " o '
            return f'{quote}{content_str}{quote}'
        
        new_content = re.sub(pattern, replace_f_string, content)
        
        # Escribir archivo corregido
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ F-strings arregladas en {file_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error arreglando f-strings en {file_path}: {e}")
        return False

def fix_unused_variables(file_path):
    """Arregla variables no utilizadas"""
    print(f"🔧 Arreglando variables no utilizadas en {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        new_lines = []
        
        for line in lines:
            # Buscar patrones de variables no utilizadas
            if 'local variable' in line and 'is assigned to but never used' in line:
                # Comentar la línea o removerla
                if line.strip().startswith('e ='):
                    # Para excepciones, usar _e
                    new_line = line.replace('e =', '_e =')
                    new_lines.append(new_line)
                elif 'category_name_map' in line:
                    # Comentar la línea
                    new_lines.append(f"# {line}")
                else:
                    # Para otros casos, usar _
                    new_line = re.sub(r'(\w+) =', r'_\1 =', line)
                    new_lines.append(new_line)
            else:
                new_lines.append(line)
        
        # Escribir archivo corregido
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
        
        print(f"✅ Variables no utilizadas arregladas en {file_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error arreglando variables no utilizadas en {file_path}: {e}")
        return False

def main():
    """Función principal del script de corrección de linting"""
    print("🔧 FERREMAS - Corrección Automática de Linting")
    print("=" * 50)
    
    # Archivos que necesitan corrección basado en los errores de flake8
    files_to_fix = [
        "flask_app/__init__.py",
        "flask_app/app.py",
        "flask_app/config/__init__.py",
        "flask_app/currency_converter.py",
        "flask_app/init_products.py",
        "flask_app/reset_db.py",
        "flask_app/routes.py",
        "flask_app/webpay_plus.py",
        "tests/conftest.py",
        "tests/create_test_db.py",
        "tests/test_auth.py",
        "tests/test_currency_converter.py",
        "tests/test_models.py",
        "tests/test_routes.py",
        "tests/test_webpay.py"
    ]
    
    print(f"📁 Arreglando {len(files_to_fix)} archivos...")
    
    for file_path in files_to_fix:
        if os.path.exists(file_path):
            print(f"\n📄 Procesando {file_path}...")
            
            # Aplicar todas las correcciones
            fix_imports(file_path)
            fix_long_lines(file_path)
            fix_f_strings(file_path)
            fix_unused_variables(file_path)
        else:
            print(f"⚠️ Archivo no encontrado: {file_path}")
    
    print("\n🔄 Re-aplicando formateo...")
    
    # Re-aplicar formateo después de las correcciones
    run_command("isort flask_app/ tests/", "Re-ordenando imports")
    run_command("black flask_app/ tests/", "Re-formateando código")
    
    print("\n🔍 Verificando correcciones...")
    
    # Verificar que las correcciones funcionaron
    flake8_output = run_command("flake8 flask_app/ tests/ --max-line-length=88 --extend-ignore=E203,W503", "Verificando con flake8")
    
    if flake8_output:
        error_count = flake8_output.count('\n')
        if error_count == 0:
            print("🎉 ¡Todas las correcciones aplicadas exitosamente!")
            print("✅ El código ahora cumple con todos los estándares de linting")
        else:
            print(f"⚠️ Aún quedan {error_count} errores de linting")
            print("📋 Errores restantes:")
            print(flake8_output)
    else:
        print("❌ Error ejecutando flake8")
    
    print("\n📋 Próximos pasos:")
    print("1. Revisa los archivos modificados")
    print("2. Haz commit de los cambios")
    print("3. Ejecuta el workflow de CI/CD")
    print("4. Si quedan errores, corrígelos manualmente")

if __name__ == "__main__":
    main() 