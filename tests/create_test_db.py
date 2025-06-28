# -*- coding: utf-8 -*-
import pyodbc
import os


def create_test_database():
    server = os.environ.get('DB_SERVER')
    user = os.environ.get('DB_USER')
    password = os.environ.get('DB_PASSWORD')
    port = os.environ.get('DB_PORT')
    db_name = os.environ.get('DB_NAME')

    conn_str = (
        f'DRIVER={{ODBC Driver 18 for SQL Server}};'
        f'SERVER={server},{port};'
        f'UID={user};PWD={password};'
        'Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
    )

    try:
        # Conectar al servidor (sin especificar base de datos)
        conn = pyodbc.connect(conn_str, autocommit=True)
        cur = conn.cursor()

        # Intentar eliminar la base de datos si existe
        try:
            cur.execute(f"DROP DATABASE IF EXISTS {db_name}")
            print("Base de datos anterior eliminada.")
        except Exception as e:
            print(f"No se pudo eliminar la base de datos: {e}")

        # Crear nueva base de datos
        cur.execute(f"CREATE DATABASE {db_name}")
        print("Base de datos de prueba creada exitosamente!")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"Ocurrió un error: {e}")


if __name__ == "__main__":
    create_test_database()
