from flask import Blueprint, request, jsonify
from database.db import get_connection
from flask_jwt_extended import create_access_token, jwt_required
import bcrypt
from datetime import date

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/menu", methods=['POST'])
@jwt_required()
def agregar_plato():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
    except:
        return jsonify({"Error": "Error de conexion con la base de datos"}),500
    
    data = request.json

    datos_requeridos = ["nombre_plato","desc_plato","precio","restricciones","seccion"]
    secciones_validas = ["platos principales", "bebidas", "postres"]

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

    if seccion_plato.lower() not in secciones_validas:
        cursor.close()
        conn.close()
        return jsonify({"Error": "Seccion del menu invalida"}), 400
    
    cursor.execute("""
                   INSERT INTO menu (nombre_plato, desc_plato, precio, restricciones, seccion)
                   VALUES (%s,%s,%s,%s,%s)
                   """,(nombre_plato.capitalize(), descripcion_plato.capitalize(), precio_plato, restricciones_plato.capitalize(), seccion_plato.capitalize())
                   )
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"Mensaje": "Plato agregado correctamente"}), 201


@admin_bp.route("/menu/<int:id_plato>", methods=["PUT"])
@jwt_required()
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

    cursor.execute("SELECT * FROM menu WHERE id_menu = %s", (id_plato,))
    plato = cursor.fetchone()  
    if not plato:
        cursor.close()
        conn.close()
        return jsonify({"Error": "Plato no encontrado"}), 404

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
@jwt_required()
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
        return jsonify({"Mensaje": "El plato no existe en el menu"}), 404

    cursor.execute("DELETE FROM menu WHERE id_menu = %s", (eliminar_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"Mensaje": "Plato eliminado"}), 200


@admin_bp.route("/reservas", methods=["GET"])
@jwt_required()
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

@admin_bp.route("/reservas/<int:modificar_reserva>", methods=["PUT"])
def modificar_reserva(modificar_reserva):
    if modificar_reserva < 1:
        return jsonify({"Error": "Ingrese un id valido"}),400
    
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
    except:
        return jsonify({"Error": "Error de conexion con la base de datos"}),500

    data = request.json
    
    campos_requeridos = ["id_reserva", "fecha", "hora", "cantidad_personas", "estado"]

    cursor.execute("SELECT * FROM reservas WHERE id_reserva = %s", (modificar_reserva,))
    reserva = cursor.fetchone()
    if not reserva:
        cursor.close()
        conn.close()
        return jsonify({"Error": "Reserva no encontrada"}), 404

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
@jwt_required()
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

@admin_bp.route("/login", methods=["POST"])
def login():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
    except:
        return jsonify({"ok": False, "mensaje": "Error de conexión"}), 500

    data = request.get_json(silent=True)
    email = data.get("femail")
    contrasena = data.get("fcontrasena")

    if not email or not contrasena:
        cursor.close()
        conn.close()
        return jsonify({"ok": False, "mensaje": "Faltan datos"}), 400

    cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
    usuario = cursor.fetchone()
    cursor.close()
    conn.close()

    if not usuario:
        return jsonify({"ok": False, "mensaje": "Usuario no encontrado"}), 404

    if not bcrypt.checkpw(contrasena.encode(), usuario["contrasena"].encode()):
        return jsonify({"ok": False, "mensaje": "Contraseña incorrecta"}), 401

    if usuario["rol"] != "admin":
        return jsonify({"ok": False, "mensaje": "No autorizado"}), 403

    token = create_access_token(identity=str(usuario["id"]))
    return jsonify({
        "ok": True,
        "mensaje": "Login correcto",
        "token": token,
        "usuario":{
        "id": usuario["id"],
        "rol": usuario["rol"]
        }
    }), 200

@admin_bp.route('/stats/', methods=['GET'])
def obtener_estadisticas():
    fecha_filtro = request.args.get('fecha')
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
    except:
        return jsonify({"Error": "Error de conexion con la base de datos"}), 500 

    if fecha_filtro:
            
        cursor.execute("SELECT COUNT(*) FROM reservas WHERE fecha = %s", (fecha_filtro,))
        total_res = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(cantidad_personas) FROM reservas WHERE fecha = %s", (fecha_filtro,))
        resultado_suma = cursor.fetchone()[0]
        comensales = resultado_suma if resultado_suma is not None else 0
        
        res_hoy = total_res
    
    else:
            
        hoy_python = date.today().strftime('%Y-%m-%d')
            
        cursor.execute("SELECT COUNT(*) FROM reservas")
        total_res = cursor.fetchone()[0]
            
        cursor.execute("SELECT SUM(cantidad_personas) FROM reservas")
        resultado_suma = cursor.fetchone()[0]
        comensales = resultado_suma if resultado_suma is not None else 0
            
        cursor.execute("SELECT COUNT(*) FROM reservas WHERE fecha = %s", (hoy_python,))
        res_hoy = cursor.fetchone()[0]

    cursor.execute("SELECT DAYNAME(fecha), COUNT(*) FROM reservas GROUP BY DAYNAME(fecha)")
    filas_dias = cursor.fetchall()
    dias_dict = {fila[0]: fila[1] for fila in filas_dias}

    cursor.execute("SELECT hora, COUNT(*) FROM reservas GROUP BY hora")
    filas_horas = cursor.fetchall()
    # Convertimos a diccionario
    horas_dict = {str(fila[0]): fila[1] for fila in filas_horas}


    cursor.close()
    conn.close()

    respuesta_json = {
            "total_reservas": total_res,
            "reservas_hoy": res_hoy,
            "total_personas": comensales,
            "stats_dias": dias_dict,
            "stats_horas": horas_dict
        }

    return jsonify(respuesta_json), 200