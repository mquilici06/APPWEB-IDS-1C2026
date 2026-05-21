from flask import Blueprint,request,jsonify
from database.db import get_connection

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/menu", methods=['POST'])
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


@admin_bp.route("/menu/<int:id_plato>", methods=["PUT"])
def editar_plato(id_plato):

    if id_plato < 1:
        return jsonify({"Error": "Ingrese un id valido, id>0"}),400
    
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
    except:
        return jsonify({"Error": "Error de conexion con la base de datos"}),500

    data = request.json

    campos_requeridos = ["nombre_plato","desc_plato","precio","restricciones","seccion"]

    for campo in campos_requeridos:
        if campo not in data:
            cursor.close()
            conn.close()
            mensaje = f"Falta completar el campo {campo}"
            return jsonify({"Error": mensaje}), 400
        
    nombre_act = data["nombre_plato"]
    desc_act = data["desc_plato"]
    precio_act = data["precio"]
    restr_act = data["restricciones"]
    seccion_act = data["seccion"]
    
    cursor.execute("""
                    UPDATE menu SET nombre_plato = %s, desc_plato = %s, precio = %s, restricciones = %s, seccion = %s WHERE id_menu = %s;
                   """, (nombre_act, desc_act, precio_act, restr_act, seccion_act, id_plato))
    conn.commit()

    cursor.close()
    conn.close()

    return " ", 204



@admin_bp.route("/menu/<int:id_plato>", methods=['PATCH'])
def actualizar_parcialmente_un_plato(id_plato):

    if id_plato < 1:
        return jsonify({"Error": "Ingrese un id valido, id>0"}),400
    

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
    except:
        return jsonify({"Error": "Error de conexion con la base de datos"}),500
    
    cursor.execute("SELECT COUNT(*) AS total FROM menu WHERE id_menu=%s",(id_plato,))
    total = cursor.fetchone()["total"]

    if not total:
        cursor.close()
        conn.close()
        return jsonify({"Error": "Plato no encontrado"}), 404

    
    data = request.json

    if not data:
        cursor.close()
        conn.close()
        return jsonify({"Error": "Faltan datos"}), 400

    datos_posibles = ["nombre_plato","desc_plato","precio","restricciones","seccion"]
    secciones_validas = ["Pastas", "Salsas", "Bebidas", "Postres"]
    
    dato_a_modificar = data.get("dato_a_modificar")
    nuevo_dato = data.get("nuevo_dato")


    if dato_a_modificar not in datos_posibles:
        cursor.close()
        conn.close()
        return jsonify({"Error": "El dato a modificar debe ser valido"}), 400
    
    elif dato_a_modificar == "seccion":
        if nuevo_dato not in secciones_validas:
            return jsonify({"Error": "Sección no valida"}), 400

    cursor.execute(f"UPDATE menu SET {dato_a_modificar}=%s WHERE id_menu=%s",(nuevo_dato,id_plato,))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"Mensaje": "Plato actualizado correctamente"}), 201

    

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


@admin_bp.route("/reservas", methods=["GET"])
def mostrar_reservas():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
    except:
        return jsonify({"error": "Error de conexion con la base de datos"}), 500

    cursor.execute("SELECT COUNT(*) AS total FROM reservas")
    total_reservas = cursor.fetchone()["total"]

    if total_reservas == 0:
        cursor.close()
        conn.close()
        return jsonify({"mensaje": "No hay reservas registradas"}), 200

    
    cursor.execute("SELECT * FROM reservas")
    lista_De_reservas = cursor.fetchall()

    reservas_echas = []

    for reserva in lista_De_reservas:
        id_del_cliente = reserva["id_cliente"]

       
        cursor.execute("SELECT nombre, email, celular FROM clientes WHERE id = %s", (id_del_cliente,))
        cliente = cursor.fetchone()

        if cliente:
            reservas = {
                "id_reserva": reserva["id_reserva"],
                "nombre_Cliente": cliente["nombre"],
                "email_cliente": cliente["email"],
                "celular_cliente": cliente["celular"],
                "fecha_y_hora": reserva["fecha_hora"],
                "cantidad_personas": reserva["cantidad_personas"]
            }
            reservas_echas.append(reservas)

    cursor.close()
    conn.close()
    return jsonify({"Reservas": reservas_echas}), 200


@admin_bp.route("/resenas", methods=["GET"])
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

