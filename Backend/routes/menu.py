from flask import Blueprint, request, jsonify
from database.db import get_connection

menu_bp = Blueprint("menu", __name__)

@menu_bp.route("", methods = ["GET"])
def listar_usuarios():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
    except:
        return jsonify({"error": "Error de conexión"}), 500

    cursor.execute("SELECT COUNT(*) AS total FROM menu")
    total= cursor.fetchone()["total"]

    if not total
        return "",204

    cursor.execute("SELECT * FROM menu")
    menu = cursor.fetchall()

    cursor.close()
    conn.close()
    return jsonify({"Menu": menu}), 200