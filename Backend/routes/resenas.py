from flask import Blueprint, request, jsonify
from database.db import get_connection

resenas_bp = Blueprint("resenas", __name__)

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
            "SELECT nombre FROM usuarios WHERE id = %s",
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

@resenas_bp.route("", methods=["POST"])
def crear_resena():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
    except:
        return jsonify({"error": "Error de conexion con la base de datos"}), 500

    data = request.get_json(silent=True)
    if not data:
        cursor.close()
        conn.close()
        return jsonify({"error": "Body vacio"}), 400

    nombre = data.get("nombre")
    mensaje = data.get("mensaje")
    puntuacion = data.get("puntuacion")

    if not nombre:
        cursor.close()
        conn.close()
        return jsonify({"error": "El campo 'nombre' es obligatorio"}), 400
    if not mensaje:
        cursor.close()
        conn.close()
        return jsonify({"error": "El campo 'mensaje' es obligatorio"}), 400
    puntuacion = int(puntuacion)
    if puntuacion is None:
        cursor.close()
        conn.close()
        return jsonify({"error": "El campo 'puntuacion' es obligatorio"}), 400
    if puntuacion < 1 or puntuacion > 5:
        cursor.close()
        conn.close()
        return jsonify({"error": "La puntuacion debe ser entre 1 y 5"}), 400
    if len(mensaje) > 500:
        cursor.close()
        conn.close()
        return jsonify({"error": "El mensaje no puede superar los 500 caracteres"}), 400

    cursor.execute("SELECT id FROM usuarios WHERE nombre = %s", (nombre,))
    cliente = cursor.fetchone()
    if not cliente:
        cursor.close()
        conn.close()
        return jsonify({"error": "Nombre de cliente invalido"}), 404
    id_cliente = cliente["id"]
    
    cursor.execute(
        "INSERT INTO resenas (id_cliente, mensaje, puntuacion) VALUES (%s, %s, %s)",
        (id_cliente, mensaje, puntuacion)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"mensaje": "Reseña enviada correctamente"}), 201

@resenas_bp.route("/<int:id>", methods=["DELETE"])
def eliminar_resena(id):
    if id < 1:
        return jsonify({"error": "Ingresar id valido, id > 0"}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
    except:
        return jsonify({"error": "Error de conexion con la base de datos"}), 500

    cursor.execute("SELECT * FROM resenas WHERE id_resena = %s", (id,))
    resena = cursor.fetchone()
    if not resena:
        cursor.close()
        conn.close()
        return jsonify({"error": "Reseña no encontrada"}), 404

    
    cursor.execute("DELETE FROM resenas WHERE id_resena = %s", (id,))

    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({"mensaje": "Reseña eliminada"}), 200