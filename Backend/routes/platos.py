from flask import Blueprint, request, jsonify
from database.db import get_connection
from flask_jwt_extended import jwt_required
import base64

menu_bp = Blueprint("menu", __name__)

@menu_bp.route("", methods=["GET"])
def listar_menu():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
    except:
        return jsonify({"error": "Error de conexión"}), 500


    cursor.execute("SELECT COUNT(*) AS total FROM menu")
    total = cursor.fetchone()["total"]


    if not total:
        cursor.close()
        conn.close()
        return "", 204


    cursor.execute("SELECT * FROM menu")
    menu = cursor.fetchall()


    cursor.close()
    conn.close()
    return jsonify({"platos": menu}), 200


@menu_bp.route("", methods=["POST"])
@jwt_required()
def crear_plato():
    try:
        conn = get_connection()
        cursor = conn.cursor()
    except:
        return jsonify({"error": "Error de conexión con la BD"}), 500

    
    nombre = request.form.get("nombre")
    descripcion = request.form.get("descripcion")
    precio = request.form.get("precio")
    seccion = request.form.get("seccion")
    restricciones = request.form.get("restricciones")
    archivo = request.files.get("imagen_plato")
    print(f"DEBUG: Archivo recibido: {archivo}") 
    if archivo:
        print(f"DEBUG: Nombre del archivo: {archivo.filename}")
   

    if not nombre or not precio:
        cursor.close()
        conn.close()
        return jsonify({"error": "Faltan datos obligatorios (nombre o precio)"}), 400

    imagen_base64 = None
    
    if archivo:
        
        imagen_base64 = base64.b64encode(archivo.read()).decode('utf-8')

    try:
        query = """INSERT INTO menu (nombre_plato, desc_plato, precio, seccion, restricciones, imagen) 
                   VALUES (%s, %s, %s, %s, %s, %s)"""
        valores = (nombre, descripcion, precio, seccion, restricciones, imagen_base64)
        
        cursor.execute(query, valores)
        conn.commit()
        
        cursor.close()
        conn.close()
        return jsonify({"mensaje": "Plato creado exitosamente"}), 201
        
    except Exception as e:
        print("Error al insertar:", e)
        cursor.close()
        conn.close()
        return jsonify({"error": "Error al guardar el plato en la base de datos"}), 500


@menu_bp.route("/<int:id>", methods=["PUT"])
@jwt_required()
def editar_plato(id):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
    except:
        return jsonify({"error": "Error de conexión"}), 500
    
    
    cursor.execute("SELECT imagen FROM menu WHERE id_menu = %s", (id,))
    plato_actual = cursor.fetchone()
    
    if not plato_actual:
        cursor.close()
        conn.close()
        return jsonify({"error": "Plato no encontrado"}), 404

    
    nombre = request.form.get("nombre")
    descripcion = request.form.get("descripcion")
    precio = request.form.get("precio")
    seccion = request.form.get("seccion")
    restricciones = request.form.get("restricciones")
    archivo = request.files.get("imagen_plato")

    try:
        if archivo and archivo.filename != '':
            
            imagen_base64 = base64.b64encode(archivo.read()).decode('utf-8')
            query = """UPDATE menu SET nombre_plato = %s, desc_plato = %s, precio = %s, 
                       seccion = %s, restricciones = %s, imagen = %s WHERE id_menu = %s"""
            cursor.execute(query, (nombre, descripcion, precio, seccion, restricciones, imagen_base64, id))
        else:
            
            query = """UPDATE menu SET nombre_plato = %s, desc_plato = %s, precio = %s, 
                       seccion = %s, restricciones = %s WHERE id_menu = %s"""
            cursor.execute(query, (nombre, descripcion, precio, seccion, restricciones, id))
            
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"mensaje": "Plato actualizado exitosamente"}), 200
        
    except Exception as e:
        print("Error al actualizar:", e)
        cursor.close()
        conn.close()
        return jsonify({"error": "Error interno al actualizar"}), 500



@menu_bp.route("/<int:id>", methods=["DELETE"])
@jwt_required()
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




