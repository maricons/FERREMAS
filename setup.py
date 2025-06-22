from setuptools import setup, find_packages

setup(
    name="flask_app",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "flask",
        "flask-sqlalchemy",
        "flask-migrate",
        "flask-mail",
        "psycopg2-binary",
        "python-dotenv",
        "flasgger",
        "marshmallow",
        "werkzeug",
    ],
)
