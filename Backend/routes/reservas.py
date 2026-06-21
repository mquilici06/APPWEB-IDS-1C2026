from flask import Blueprint, request, jsonify, current_app
from database.db import get_connection
from datetime import datetime
from flask_mail import Mail
from utils.auxiliar import enviar_mail_reserva
from utils.auxiliar import errores
import re

reservas_bp = Blueprint("reservas", __name__)

capacidad_max = 10


@reservas_bp.route("/disponibilidad", methods=["GET"])
def esta_disponible():
    #se manda la fecha como query params
    fecha = request.args.get('fecha')
    capacidad = 0
    
    if not fecha:
        return errores(400,"Bad request","Falta el parámetro 'fecha'")
    
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
    except:
        return errores(500,"Internal server error", "Error de conexion con la base de datos")
    
    cursor.execute("""
        SELECT COALESCE(SUM(cantidad_personas),0) AS total
        FROM reservas
        WHERE fecha = %s
        AND estado = 'confirmada'
    """, (fecha,))

    total_personas = cursor.fetchone()
    capacidad = total_personas["total"]


    if capacidad >= capacidad_max:
        esta_disponible = False
    else:
        esta_disponible = True

    cursor.close()
    conn.close()

    rdo = {"esta_disp": f"{esta_disponible}"}
    return jsonify(rdo), 200



@reservas_bp.route("/", methods=["POST"])
def crear_reserva():
    patron = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+\.[A-Za-z]{2,}$"
    datos = request.get_json()

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
    except Exception:
        return errores(500,"Internal server error", "Error de conexion con la base de datos")

    for campo in ["nombre", "email", "telefono", "personas", "fecha", "hora"]:
        if not datos or not datos.get(campo):
            return errores(400,"Bad request",f"Falta el campo '{campo}'")

    nombre = datos["nombre"]
    email = datos["email"].strip()
    telefono = datos["telefono"]
    personas = int(datos["personas"])
    fecha = datos["fecha"]
    hora = datos["hora"]
    notas = datos.get("notas", "")

    if not re.match(patron, email):
        return errores(400,"Bad request","Ingresá un email válido")

    try:
        fecha_ = datetime.strptime(fecha, "%Y-%m-%d").date()
        if fecha_ < datetime.now().date():
            return errores(400,"Bad request","No podés reservar en una fecha pasada")
        if fecha_.weekday() not in [3, 4, 5, 6]:
            return errores(400,"Bad request","Solo aceptamos reservas de jueves a domingo")
    except ValueError:
        return errores(400,"Bad request","Solo aceptamos reservas de jueves a domingo")
        

    cursor.execute("""
        SELECT COALESCE(SUM(cantidad_personas), 0) AS total
        FROM reservas WHERE fecha = %s AND hora = %s AND estado = 'confirmada'
        """, (fecha, hora))

    ocupacion = cursor.fetchone()["total"]

    if ocupacion + personas > capacidad_max:
        cursor.close()
        conn.close()
        return errores(409,"Conflict","El horario seleccionado excede la capacidad disponible")

    cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
    existente = cursor.fetchone()
    if existente:
        id_cliente = existente["id"]
    else:
        cursor.execute(
            "INSERT INTO usuarios (nombre, email, celular, rol) VALUES (%s, %s, %s, 'cliente')",
            (nombre, email, telefono)
        )
        id_cliente = cursor.lastrowid

    cursor.execute("""
        INSERT INTO reservas (id_cliente, fecha, hora, cantidad_personas, estado)
        VALUES (%s, %s, %s, %s, 'confirmada')
    """, (id_cliente, fecha, hora, personas))
    id_reserva = cursor.lastrowid

    try:
        mail = Mail(current_app._get_current_object())
        enviar_mail_reserva(mail, nombre, email, fecha, hora, personas, id_reserva, notas)
    except Exception:
        conn.rollback()
        cursor.close()
        conn.close()
        return errores(500,"Internal server error", "No pudimos enviarte el mail de confirmación, así que la reserva no se guardó. Intentá de nuevo en unos minutos.")


    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"mensaje": "Reserva confirmada exitosamente", "id_reserva": id_reserva}), 201


@reservas_bp.route("/<int:id>", methods=["POST"])
def cancelar_reserva(id):
    if id < 0:
        return errores(400,"Bad request","Ingresar id valido, id > 0")

    datos = request.get_json(silent=True) or {}
    email = datos.get("email", "").strip().lower()

    if not email:
        return errores(400,"Bad request","Falta el email para confirmar a quién pertenece la reserva")

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
    except Exception:
        return errores(500,"Internal server error", "Error de conexión con la base de datos")

    cursor.execute("SELECT id_reserva, id_cliente FROM reservas WHERE id_reserva = %s", (id,))
    reserva = cursor.fetchone()

    if not reserva:
        cursor.close()
        conn.close()
        return errores(404,"Not found", "Reserva no encontrada")

    cursor.execute("SELECT email FROM usuarios WHERE id = %s", (reserva["id_cliente"],))
    cliente = cursor.fetchone()

    if not cliente or cliente["email"].strip().lower() != email:
        cursor.close()
        conn.close()
        return errores(403,"Forbidden", "El email no coincide con el titular de la reserva")

    cursor.execute("DELETE FROM reservas WHERE id_reserva = %s", (id,))

    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"mensaje": "Reserva cancelada"}), 200