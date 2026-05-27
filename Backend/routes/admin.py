from flask import Blueprint, request, jsonify, session, redirect
from database.db import get_connection
import bcrypt

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

    

@admin_bp.route("/<int:eliminar_id>", methods=["DELETE"])
def eliminar_plato(eliminar_id):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
    except:
        return jsonify({"Error": "Error de conexion con la base de datos"}), 500
    
    cursor.execute("SELECT id_menu FROM menu WHERE id_menu = %s", (eliminar_id,))
    existe = cursor.fetchone()

    if not existe:
        cursor.close()
        conn.close()
        return jsonify({"Mensaje": "El ID no existe en el menu"}), 404

    cursor.execute("DELETE FROM menu WHERE id_menu = %s", (eliminar_id,))
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

        cursor.execute("SELECT nombre, email, celular FROM usuarios WHERE id = %s", (id_del_cliente,))
        cliente = cursor.fetchone()

        if cliente:
            reservas = {
                "id_reserva": reserva["id_reserva"],
                "nombre_Cliente": cliente["nombre"],
                "email_cliente": cliente["email"],
                "celular_cliente": cliente["celular"],
                "fecha": reserva["fecha"],
                "hora": reserva["hora"],
                "cantidad_personas": reserva["cantidad_personas"]
            }
            reservas_echas.append(reservas)

    cursor.close()
    conn.close()
    return jsonify({"Reservas": reservas_echas}), 200

@admin_bp.route("/reservas/<int:modificar_reserva>", methods=["Put"])
def modificar_plato(modificar_reserva):
    if modificar_reserva < 1:
        return jsonify({"Error": "Ingrese un id valido"}),400
    
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
    except:
        return jsonify({"Error": "Error de conexion con la base de datos"}),500

    data = request.json
    
    campos_requeridos = ["id_reserva", "fecha", "hora", "cantidad_personas", "estado"]

    for campo in campos_requeridos:
        if campo not in data:
            cursor.close()
            conn.close()
            return jsonify({"Error": f"Falta el campo {campo}"}), 400

    id_reserva_nuevo = data["id_reserva"]
    fecha_nueva = data["fecha"]
    hora_nueva = data["hora"]
    cantidad_personas_nueva = data["cantidad_personas"]
    estado_nuevo = data["estado"]

    cursor.execute("UPDATE reservas SET id_reserva = %s, fecha = %s, hora = %s, cantidad_personas = %s, estado = %s WHERE id_reserva = %s", (id_reserva_nuevo, fecha_nueva, hora_nueva, cantidad_personas_nueva, estado_nuevo, modificar_reserva))
    conn.commit()
    cursor.close()
    conn.close()
    return " ", 204 



@admin_bp.route("/resenas/<int:resena_id>", methods=["DELETE"])
def eliminar_resena(resena_id):
    if resena_id < 1:
        return jsonify({"error": "Ingresar id valido, id > 0"}), 409
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
    except:
        return jsonify({"Error": "Error de conexion con la base de datos"}), 500

    cursor.execute("SELECT id_resena FROM resenas WHERE id_resena = %s", (resena_id,))
    existe_reseña = cursor.fetchone()

    if not existe_reseña:
        cursor.close()
        conn.close()
        return jsonify({"Error": "La reseña no existe"}), 404

    cursor.execute("DELETE FROM resenas WHERE id_resena = %s", (resena_id,))
    conn.commit()
    
    cursor.close()
    conn.close()
    return '', 204

@admin_bp.route("/login", methods=["GET","POST"])
def login():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
    except:
        return jsonify({"error": "Error de conexion"}), 500

    email = request.form.get("email")
    contrasena = request.form.get("contrasena")

    cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
    usuario = cursor.fetchone()

    cursor.close()
    conn.close()

    if not usuario:
        return "Usuario no encontrado", 404

    if not bcrypt.checkpw(contrasena.encode(), usuario["contrasena"].encode()):
        return "Contraseña incorrecta", 401

    session["usuario_id"] = usuario["id"] # agrego para que se guarde del id de usuario y el rol
    session["rol"] = usuario["rol"]       # preguntar a leo sobre las sesiones en 2 puertos distintos(cookies)

    if usuario["rol"] != "admin":
        return redirect("http://localhost:5001/login/admin")

    return redirect("http://127.0.0.1:5001/admin")


@admin_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"mensaje": "Sesion cerrada"}), 200