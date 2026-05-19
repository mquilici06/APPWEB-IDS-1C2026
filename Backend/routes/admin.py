from flask import Blueprint,request,jsonify
from database.db import get_connection

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/menu/admin", methods=['POST'])
def agregar_plato():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
    except:
        return jsonify({"Error": "Error de conexion con la base de datos"}),500
    
    data = request.json

    datos_requeridos = ["nombre_plato","desc_plato","precio","restricciones","seccion"]
    secciones_validas = ["Pastas", "Salsas", "Bebidas", "Postres"]

    for campo in datos_requeridos:
        if campo not in data:
            cursor.close()
            conn.close()
            return jsonify({"Error": "Falta Completar algun campo"}), 400
    
    nombre_plato = data.get("nombre_plato")
    descripcion_plato = data.get("desc_plato")
    precio_plato = data.get("precio")
    restricciones_plato = data.get("restricciones")
    seccion_plato = data.get("seccion")

    cursor.execute("""
                   SELECT COUNT(*) AS total FROM menu WHERE nombre_plato = %s AND desc_plato = %s """,(nombre_plato,descripcion_plato))
    existente = cursor.fetchone()["total"]

    if existente > 0:
        cursor.close()
        conn.close()
        return jsonify({"Error": "Plato ya existente"}), 409
    

    if not isinstance(precio_plato,(int,float)) or precio_plato <= 0:
        cursor.close()
        conn.close()
        return jsonify({"Error": "Precio establecido invalido"}), 400


    if seccion_plato not in secciones_validas:
        cursor.close()
        conn.close()
        return jsonify({"Error": "Seccion del menu invalida"}), 400
    
    cursor.execute("""
                   INSERT INTO menu (nombre_plato, desc_plato, precio, restricciones, seccion)
                   VALUES (%s,%s,%s,%s,%s)
                   """,(nombre_plato, descripcion_plato, precio_plato, restricciones_plato, seccion_plato)
                   )
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"Mensaje": "Plato agregado correctamente"}), 201

@admin_bp.route("/admin/<int:eliminar_id>", methods=["DELETE"])
def eliminar_plato(eliminar_id):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
    except:
        return jsonify({"Error": "Error de conexion con la base de datos"}), 500

    cursor.execute("SELECT id FROM menu WHERE id = %s", (eliminar_id,))
    existe = cursor.fetchone()

    if not existe:
        cursor.close()
        conn.close()
        return jsonify({"Mensaje": "El ID no existe en el menu"}), 404


    cursor.execute("DELETE FROM menu WHERE id = %s", (eliminar_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"Mensaje": "Plato eliminado"}), 200