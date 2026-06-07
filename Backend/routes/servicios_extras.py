from flask import Blueprint, request, jsonify
from database.db import get_connection

servicios_extras_bp = Blueprint("servicios_extras", __name__)

@servicios_extras_bp.route("/", methods=["GET"])
def mostrar_servicios_extras():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM servicios_extras")
        servicios = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({"servicios_extras": servicios}), 200
    except:
        return jsonify({"Mensaje": "Error con la base de daatos"}), 500