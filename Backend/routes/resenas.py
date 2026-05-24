from flask import Blueprint, request, jsonify
from database.db import get_connection

resenas_bp = Blueprint("resenas", __name__)
# Aca esta el GET que se usara para los clientes y para el admin.
@resenas_bp.route("", methods=["GET"])
def listar_resenas():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
    except:
        return jsonify({"error": "Error de conexion con la base de datos"}), 500

    cursor.execute("SELECT COUNT(*) AS total FROM resenas")
    total_resenas = cursor.fetchone()["total"] 
    if total_resenas == 0:
        cursor.close()
        conn.close()
        return jsonify({"mensaje": "No hay resenas registradas"}), 200

    cursor.execute("SELECT * FROM resenas")
    lista_resenas = cursor.fetchall()

    resenas_armadas = []

    for resena in lista_resenas:

        cursor.execute(
            "SELECT nombre FROM clientes WHERE id = %s",
            (resena["id_cliente"],)
        )
        cliente = cursor.fetchone()
        if cliente:
            resena_completa = {
            "id_resena": resena["id_resena"],
            "nombre_cliente": cliente["nombre"],
            "mensaje": resena["mensaje"],
            "puntuacion": resena["puntuacion"]
            }
            resenas_armadas.append(resena_completa)

    cursor.close()
    conn.close()
    return jsonify({"resenas": resenas_armadas}), 200