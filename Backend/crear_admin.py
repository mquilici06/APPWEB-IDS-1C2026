import bcrypt
from database.db import get_connection

contrasena = "admin123"
hash = bcrypt.hashpw(contrasena.encode(), bcrypt.gensalt())

conn = get_connection()
cursor = conn.cursor()

cursor.execute("""
    INSERT INTO usuarios (nombre, email, celular, rol, contrasena)
    VALUES (%s, %s, %s, %s, %s)
""", ("Admin", "admin@altezza.com", "1111111111", "admin", hash.decode()))

conn.commit()
cursor.close()
conn.close()
print("Admin creado correctamente")