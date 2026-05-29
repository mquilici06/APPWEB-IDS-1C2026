import mysql.connector
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE_DIR, "__init__.sql")) as f:
    sql = f.read()

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Root123!"
)

cursor = conn.cursor()
for statement in sql.split(";"):
    if statement.strip():
        cursor.execute(statement)
        conn.commit()
cursor.close()
conn.close()