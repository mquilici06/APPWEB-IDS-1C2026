from flask import Blueprint, request, jsonify
from database.db import get_connection
from flask_jwt_extended import create_access_token, jwt_required
import bcrypt
from datetime import date, datetime
from utils.auxiliar import errores

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/menu", methods=['POST'])
@jwt_required()
def agregar_plato():
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
    
        data = request.json

        datos_requeridos = ["nombre_plato","desc_plato","precio","restricciones","seccion","imagen"]
        secciones_validas = ["platos principales", "bebidas", "postres"]

        for campo in datos_requeridos:
            if campo not in data:
                return errores(400,"Datos incompletos","Falta Completar algun campo obligatorio")
    
        nombre_plato = data.get("nombre_plato")
        descripcion_plato = data.get("desc_plato")
        precio_plato = data.get("precio")
        restricciones_plato = data.get("restricciones")
        seccion_plato = data.get("seccion")
        imagen = data.get("imagen")

        cursor.execute("""
                    SELECT COUNT(*) AS total FROM menu WHERE nombre_plato = %s AND desc_plato = %s """,(nombre_plato,descripcion_plato))
        existente = cursor.fetchone()["total"]

        if existente > 0:
            return errores(409,"Plato existente","Ya existe un plato con ese nombre o descripcion") 
        

        if not isinstance(precio_plato,(int,float)) or precio_plato <= 0:
            return errores(400,"Precio establecido invalido","El precio debe ser un entero mayor a 0 ")

        if seccion_plato.lower() not in secciones_validas:
            return errores(400,"Seccion del menu invalida", "la seccion indicada no existe")
        
        cursor.execute("""
                    INSERT INTO menu (nombre_plato, desc_plato, precio, restricciones, seccion, imagen)
                    VALUES (%s,%s,%s,%s,%s,%s)
                    """,(nombre_plato.capitalize(), descripcion_plato.capitalize(), precio_plato, restricciones_plato.capitalize(), seccion_plato.capitalize(),imagen)
                    )
        conn.commit()
    
        return jsonify({"Mensaje": "Plato agregado correctamente"}), 201
    
    except Exception as e:
        return errores(500, "Error interno", str(e))
    
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()
    


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
    imagen_act = data["imagen"]

    if imagen_act is None:
        imagen_act = plato["imagen"]
    
    cursor.execute("""
                    UPDATE menu SET nombre_plato = %s, desc_plato = %s, precio = %s, restricciones = %s, seccion = %s, imagen = %s WHERE id_menu = %s;
                   """, (nombre_act, desc_act, precio_act, restr_act, seccion_act,imagen_act, id_plato))
    conn.commit()

    cursor.close()
    conn.close()

    return " ", 204

    

@admin_bp.route("/menu/<int:eliminar_id>", methods=["DELETE"])
@jwt_required()
def eliminar_plato(eliminar_id):
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT id_menu FROM menu WHERE id_menu = %s", (eliminar_id,))
        existe = cursor.fetchone()

        if not existe:
            return jsonify({"Mensaje": "El plato no existe en el menu"}), 404

        cursor.execute("DELETE FROM menu WHERE id_menu = %s", (eliminar_id,))
        conn.commit()
        return jsonify({"Mensaje": "Plato eliminado"}), 200

    except Exception as e:
        return jsonify({"Error": f"Error de conexion con la base de datos: {str(e)}"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@admin_bp.route("/reservas", methods=["GET"])
@jwt_required()
def mostrar_reservas():
    #Atrapa params
    buscar = request.args.get('buscar', '').lower()
    fecha_filtro = request.args.get('fecha', '')
    estado_filtro = request.args.get('estado', '').lower()
    

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
    except Exception as e:
        return jsonify({"error": "Error de conexion con la base de datos"}), 500

    cursor.execute("SELECT COUNT(*) AS total FROM reservas")
    total_reservas = cursor.fetchone()["total"]

    if total_reservas == 0:
        cursor.close()
        conn.close()
        return jsonify({"mensaje": "No hay reservas registradas", "Reservas": []}), 200

    cursor.execute("SELECT * FROM reservas")
    lista_De_reservas = cursor.fetchall()

    reservas_hechas = []

    for reserva in lista_De_reservas:
        id_del_cliente = reserva["id_cliente"]

        cursor.execute(
            "SELECT nombre, email, celular FROM usuarios WHERE id = %s",
            (id_del_cliente,)
        )

        cliente = cursor.fetchone()

        if cliente:
            nombre_cliente = cliente["nombre"]
            email_cliente = cliente["email"]
            fecha_reserva = str(reserva["fecha"])
            estado_reserva = reserva.get("estado", "Pendiente")

            # Filtros
            if buscar and (buscar not in nombre_cliente.lower() and buscar not in email_cliente.lower()):
                continue 
            
            if fecha_filtro and fecha_filtro != fecha_reserva:
                continue 
                
            if estado_filtro and estado_filtro != estado_reserva.lower():
                continue 

            reservas = {
                "id_reserva": reserva["id_reserva"],
                "nombre_Cliente": nombre_cliente,
                "email_cliente": email_cliente,
                "celular_cliente": cliente["celular"],
                "fecha": fecha_reserva,
                "hora": str(reserva["hora"]),
                "cantidad_personas": reserva["cantidad_personas"],
                "estado": estado_reserva
            }

            reservas_hechas.append(reservas)

    cursor.close()
    conn.close()

    return jsonify({"Reservas": reservas_hechas}), 200

@admin_bp.route("/reservas/<int:id_reserva>/estado", methods=["PUT"])
@jwt_required()
def actualizar_estado_reserva(id_reserva):
    data = request.json
    nuevo_estado = data.get("estado")

    if nuevo_estado not in ["confirmada", "cancelada", "pendiente"]:
        return jsonify({"Error": "Estado no válido"}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE reservas 
            SET estado = %s 
            WHERE id_reserva = %s
        """, (nuevo_estado, id_reserva))
        
        conn.commit()
        return jsonify({"Mensaje": "Estado de la reserva actualizado"}), 200

    except Exception as e:
        return jsonify({"Error": f"Error en BD: {str(e)}"}), 500
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@admin_bp.route("/reservas/<int:modificar_reserva>", methods=["PUT"])
@jwt_required()
def modificar_reserva(modificar_reserva):
    conn = None
    cursor = None

    if modificar_reserva < 1:
        return jsonify({"Error": "Ingrese un id valido"}), 400

    data = request.json

    campos_requeridos = ["fecha", "hora", "cantidad_personas", "estado"]
    for campo in campos_requeridos:
        if campo not in data:
            return jsonify({"Error": f"Falta el campo {campo}"}), 400

    cantidad_personas = data["cantidad_personas"]
    if not isinstance(cantidad_personas, int) or cantidad_personas <= 0:
        return jsonify({"Error": "La cantidad de personas debe ser un número positivo"}), 400

    estado_nuevo = data["estado"].strip().lower()
    if estado_nuevo not in ["pendiente", "confirmada", "cancelada"]:
        return jsonify({"Error": "Estado inválido"}), 400

    try:
        fecha_reserva = datetime.strptime(data["fecha"], "%Y-%m-%d").date()
        if fecha_reserva < datetime.now().date():
            return jsonify({"Error": "No se pueden programar reservas para fechas pasadas"}), 400
    except ValueError:
        return jsonify({"Error": "Formato de fecha inválido. Por favor, use el formato YYYY-MM-DD"}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM reservas WHERE id_reserva = %s", (modificar_reserva,))
        reserva = cursor.fetchone()
        if not reserva:
            return jsonify({"Error": "Reserva no encontrada"}), 404

        query = """UPDATE reservas SET fecha = %s, hora = %s, cantidad_personas = %s, estado = %s 
                   WHERE id_reserva = %s"""
        valores = (data["fecha"], data["hora"], cantidad_personas, estado_nuevo, modificar_reserva)
        cursor.execute(query, valores)
        conn.commit()

        return jsonify({"Mensaje": "El cambio se realizó correctamente"}), 200

    except Exception as e:
        return jsonify({"Error": f"Error al modificar reserva: {str(e)}"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

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

@admin_bp.route("/resenas/<int:id>/estado", methods=["PUT"])
@jwt_required()
def cambiar_estado_resena(id):
    if id < 1:
        return jsonify({"error": "ID invalido"}), 400

    data = request.get_json(silent=True)
    nuevo_estado = data.get("estado") if data else None

    if nuevo_estado not in ["Publicada", "Pendiente"]:
        return jsonify({"error": "Estado invalido, debe ser Publicada o Pendiente"}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
    except Exception:
        return jsonify({"error": "Error de conexion con la base de datos"}), 500
    
    cursor.execute("SELECT * FROM resenas WHERE id_resena = %s", (id,))

    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({"error": "Reseña no encontrada"}), 404
    
    cursor.execute("UPDATE resenas SET estado = %s WHERE id_resena = %s", (nuevo_estado, id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"mensaje": f"Reseña marcada como {nuevo_estado}"}), 200

@admin_bp.route("/resenas", methods=["GET"])
@jwt_required()
def listar_todas_resenas():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
    except Exception:
        return jsonify({"error": "Error de conexion con la base de datos"}), 500

    cursor.execute("SELECT * FROM resenas")
    lista_resenas = cursor.fetchall()

    if not lista_resenas:
        cursor.close()
        conn.close()
        return jsonify({"resenas": []}), 200

    resenas_armadas = []
    for resena in lista_resenas:
        cursor.execute("SELECT nombre FROM usuarios WHERE id = %s", (resena["id_cliente"],))
        cliente = cursor.fetchone()
        if cliente:
            resena_completa = {
                "id_resena": resena["id_resena"],
                "nombre_cliente": cliente["nombre"],
                "mensaje": resena["mensaje"],
                "puntuacion": resena["puntuacion"],
                "estado": resena.get("estado", "Pendiente")
            }
            resenas_armadas.append(resena_completa)

    cursor.close()
    conn.close()
    return jsonify({"resenas": resenas_armadas}), 200

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
@jwt_required()
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

@admin_bp.route("/servicios_extras", methods=["GET"])
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
        return jsonify({"Mensaje": f"Error con la base de datos: {str(e)}"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    
    
@admin_bp.route("/servicios_extras", methods=["POST"])
def agregar_servicio_extra():
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        data = request.json
        if not data:
            return jsonify({"Error": "No se recibieron datos"}), 400

        nombre_servicio = data.get("nombre_servicio")
        descripcion_servicio = data.get("descripcion_servicio")

        if not nombre_servicio or not descripcion_servicio:
            return jsonify({"Error": "Faltan datos requeridos"}), 400

        cursor.execute("SELECT COUNT(*) AS total FROM servicios_extras WHERE nombre_servicio = %s", (nombre_servicio,))
        existente = cursor.fetchone()["total"]

        if existente > 0:
            return jsonify({"Error": "Servicio extra ya existente"}), 409

        cursor.execute("""
            INSERT INTO servicios_extras (nombre_servicio, descripcion_servicio) 
            VALUES (%s, %s)
        """, (nombre_servicio, descripcion_servicio))
        conn.commit()
        return jsonify({"Mensaje": "Servicio extra agregado correctamente"}), 201

    except Exception as e:
        return jsonify({"Error": f"Error de conexion con la base de datos: {str(e)}"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    
    
@admin_bp.route("/servicios_extras/<int:id_servicio>", methods=["PUT"])
def editar_servicio_extra(id_servicio):
    conn = None
    cursor = None

    if id_servicio < 1:
        return jsonify({"Mensaje": "Por favor ingrese un id valido"}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        data = request.json
        if not data:
            return jsonify({"Mensaje": "No se recibieron los datos necesarios"}), 400

        nombre_servicio_act = data.get("nombre_servicio")
        descripcion_servicio_act = data.get("descripcion_servicio")

        if not nombre_servicio_act or not descripcion_servicio_act:
            return jsonify({"Mensaje": "Faltan datos requeridos para la actualización"}), 400

        cursor.execute("SELECT * FROM servicios_extras WHERE id_servicio = %s", (id_servicio,))
        servicio = cursor.fetchone()

        if not servicio:
            return jsonify({"Mensaje": "El servicio extra no existe"}), 404

        if (nombre_servicio_act == servicio["nombre_servicio"] and
                descripcion_servicio_act == servicio["descripcion_servicio"]):
            return jsonify({"Mensaje": "Para modificar el servicio debe ingresar valores nuevos"}), 400

        cursor.execute("""
            SELECT COUNT(*) AS total 
            FROM servicios_extras WHERE nombre_servicio = %s AND id_servicio != %s
        """, (nombre_servicio_act, id_servicio))
        duplicado = cursor.fetchone()["total"]

        if duplicado > 0:
            return jsonify({"Mensaje": "Ya existe otro servicio con ese nombre"}), 409

        cursor.execute("""
            UPDATE servicios_extras SET nombre_servicio = %s, descripcion_servicio = %s 
            WHERE id_servicio = %s
        """, (nombre_servicio_act, descripcion_servicio_act, id_servicio))
        conn.commit()
        return jsonify({"Mensaje": "Servicio extra actualizado"}), 200

    except Exception as e:
        return jsonify({"Error": f"Error de conexion con la base de datos: {str(e)}"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    
@admin_bp.route("/servicios_extras/<int:id_servicio>", methods=["DELETE"])
def eliminar_servicio_extra(id_servicio):
    conn = None
    cursor = None

    if id_servicio < 1:
        return jsonify({"Mensaje": "Por favor ingrese un id valido"}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM servicios_extras WHERE id_servicio = %s", (id_servicio,))
        servicio = cursor.fetchone()

        if not servicio:
            return jsonify({"Mensaje": "El servicio extra no existe"}), 404

        cursor.execute("DELETE FROM servicios_extras WHERE id_servicio = %s", (id_servicio,))
        conn.commit()
        return jsonify({"Mensaje": "Servicio extra eliminado"}), 200

    except Exception as e:
        return jsonify({"Error": f"Error de conexion con la base de datos: {str(e)}"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@admin_bp.route("/reservas/<int:id>/eliminar", methods=["DELETE"])
@jwt_required()
def eliminar_reserva(id):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
    except Exception:
        return errores(500, "Internal server error", "Error de conexión con la base de datos")

    cursor.execute("SELECT id_reserva FROM reservas WHERE id_reserva = %s", (id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return errores(404, "Not found", "Reserva no encontrada")

    cursor.execute("DELETE FROM reservas WHERE id_reserva = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"mensaje": "Reserva eliminada"}), 200