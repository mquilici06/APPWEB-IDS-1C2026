import os
import mysql.connector


def get_env(nombre):
    value = os.getenv(nombre)

    if not value:
        raise ValueError("Alguna credencial no configurada")
    
    return value


def get_connection():
    return mysql.connector.connect(
        host=get_env("DB_HOST"),
        user=get_env("DB_USER"),
        password=get_env("DB_PASSWORD"),
        database=get_env("DB_NAME"),
    )