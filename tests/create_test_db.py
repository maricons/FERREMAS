# -*- coding: utf-8 -*-
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def create_test_database():
    try:
        # Conectar a PostgreSQL
        conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="postgres",
            host="localhost",
            port="5432",
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        # Intentar eliminar la base de datos si existe
        try:
            cur.execute("DROP DATABASE IF EXISTS ferremas_test")
            print("Base de datos anterior eliminada.")
        except Exception as e:
            print(f"No se pudo eliminar la base de datos: {e}")

        # Crear nueva base de datos con configuración regional de Spanish_Chile
        cur.execute(
            "CREATE DATABASE ferremas_test WITH ENCODING 'UTF8' "
            "LC_COLLATE 'Spanish_Chile.1252' LC_CTYPE 'Spanish_Chile.1252'"
        )
        print("Base de datos de prueba creada exitosamente!")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"Ocurrió un error: {e}")


if __name__ == "__main__":
    create_test_database()
