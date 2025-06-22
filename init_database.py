#!/usr/bin/env python3
"""
Script de inicialización completa de la base de datos de Ferremas
"""

import sys
import os

# Agregar el directorio flask_app al path
sys.path.append(os.path.join(os.path.dirname(__file__), "flask_app"))

from flask_app.app import app
from flask_app.extensions import db
from flask_app.models import Product, Category
from flask_app.init_categories import init_categories
from flask_app.init_products import init_products


def main():
    print("🚀 Inicializando base de datos de Ferremas...")

    with app.app_context():
        try:
            # 1. Crear todas las tablas
            print("📋 Creando tablas de la base de datos...")
            db.create_all()
            print("✅ Tablas creadas exitosamente")

            # 2. Eliminar productos y categorías existentes
            print("🧹 Eliminando productos existentes...")
            Product.query.delete()
            db.session.commit()
            print("🧹 Eliminando categorías existentes...")
            Category.query.delete()
            db.session.commit()
            print("✅ Productos y categorías eliminados")

            # 3. Inicializar categorías
            print("📂 Inicializando categorías...")
            init_categories()
            print("✅ Categorías inicializadas")

            # 4. Inicializar productos
            print("🛠️ Inicializando productos...")
            init_products()
            print("✅ Productos inicializados")

            print("\n🎉 ¡Base de datos inicializada completamente!")
            print("📊 Resumen:")
            print("   - Tablas creadas")
            print("   - 8 categorías agregadas")
            print("   - 16 productos agregados")
            print("\n🚀 Puedes ejecutar la aplicación con: python run.py")

        except Exception as e:
            print(f"❌ Error durante la inicialización: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
