from flask import Blueprint, request, jsonify
from database.db import get_connection

servicios_extras_bp = Blueprint("servicios_extras", __name__)

@servicios_extras_bp.route("/", methods=["GET"])
def mostrar_servicios_extras():
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM servicios_extras")
        servicios = cursor.fetchall()
        
        return jsonify({"servicios_extras": servicios}), 200
        
    except Exception as e:
        return jsonify({"Mensaje": "Error con la base de datos"}), 500    

    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()