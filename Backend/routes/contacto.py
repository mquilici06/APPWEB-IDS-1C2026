from flask import Blueprint, request, jsonify
from database.db import get_connection

contacto_bp = Blueprint("contacto", __name__)

@contacto_bp.route("", methods=["POST"])
def recibir_contacto():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
    except Exception:
        return jsonify({"Error": "Error de conexión"}), 500

    data = request.json
    
    if not data or not data.get("nombre") or not data.get("email") or not data.get("mensaje"):
        cursor.close()
        conn.close()
        return jsonify({"Error": "faltan nombre, email o mensaje"}), 400
    
    nombre = data["nombre"]
    email = data["email"]
    mensaje = data["mensaje"]

    try:
        cursor.execute("""
            INSERT INTO mensajes_contacto (nombre, email, mensaje) 
            VALUES (%s, %s, %s)
        """, (nombre, email, mensaje))
        
        conn.commit()
    except Exception:
        cursor.close()
        conn.close()
        return jsonify({"Error": "No se guardo el mensaje"}), 500
    
    cursor.close()
    conn.close()

    return jsonify({"Mensaje": "Mensaje de contacto enviado correctamente"}), 201