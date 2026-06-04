from flask import Blueprint, request, jsonify
from database.db import get_connection

menu_bp = Blueprint("menu", __name__)

@menu_bp.route("", methods = ["GET"])
def listar_menu():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
    except:
        return jsonify({"error": "Error de conexión"}), 500

    cursor.execute("SELECT COUNT(*) AS total FROM menu")
    total= cursor.fetchone()["total"]

    if not total:
        return "",204

    cursor.execute("SELECT * FROM menu")
    menu = cursor.fetchall()

    cursor.close()
    conn.close()
    return jsonify({"platos": menu}), 200

@menu_bp.route("", methods=["POST"])
def crear_plato():
    try:
        conn = get_connection()
        cursor = conn.cursor()
    except:
        return jsonify({"error": "Error de conexión con la BD"}), 500
    data = request.get_json(silent=True)
    if not data:
        cursor.close()
        conn.close()
        return jsonify({"error": "Body de la petición vacío"}), 400
    nombre = data.get("nombre")
    descripcion = data.get("descripcion")
    precio = data.get("precio")
    seccion = data.get("seccion")
    restricciones = data.get("restricciones")

    if not nombre or not precio:
        cursor.close()
        conn.close()
        return jsonify({"error": "Faltan datos obligatorios (nombre o precio)"}), 400

    try:
        query = """INSERT INTO menu (nombre_plato, desc_plato, precio, seccion, restricciones) 
                   VALUES (%s, %s, %s, %s, %s)"""
        valores = (nombre, descripcion, precio, seccion, restricciones)
        
        cursor.execute(query, valores)
        conn.commit()
        
        cursor.close()
        conn.close()
        return jsonify({"mensaje": "Plato creado exitosamente"}), 201
        
    except Exception as e:
        print("Error al insertar:", e)
        cursor.close()
        conn.close()
        return jsonify({"error": "Error al guardar el plato en la base de datos"}), 5004

@menu_bp.route("/<int:id>", methods=["PUT"])
def editar_plato(id):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
    
        cursor.execute("SELECT * FROM menu WHERE id_menu = %s", (id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"error": "Plato no encontrado"}), 404

        data = request.get_json(silent=True)
        if not data:
            cursor.close()
            conn.close()
            return jsonify({"error": "Cuerpo vacío"}), 400

        nombre = data.get("nombre")
        descripcion = data.get("descripcion")
        precio = data.get("precio")
        seccion = data.get("seccion")
        restricciones = data.get("restricciones")
        query = """UPDATE menu 
                   SET nombre_plato = %s, desc_plato = %s, precio = %s, seccion = %s, restricciones = %s 
                   WHERE id_menu = %s"""
        cursor.execute(query, (nombre, descripcion, precio, seccion, restricciones, id))
        conn.commit()
        
        cursor.close()
        conn.close()
        return jsonify({"mensaje": "Plato actualizado exitosamente"}), 200
    except Exception as e:
        print("Error al actualizar:", e)
        return jsonify({"error": "Error interno al actualizar"}), 500

@menu_bp.route("/<int:id>", methods=["DELETE"])
def borrar_plato(id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = "DELETE FROM menu WHERE id_menu = %s"
        cursor.execute(query, (id,))
        conn.commit()
        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            return jsonify({"error": "Plato no encontrado"}), 404
            
        cursor.close()
        conn.close()
        return jsonify({"mensaje": "Plato eliminado exitosamente"}), 200
        
    except Exception as e:
        print("Error al eliminar:", e)
        return jsonify({"error": "Error interno al eliminar el plato"}), 500