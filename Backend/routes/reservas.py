from flask import Blueprint, request, jsonify
from database.db import get_connection
from datetime import datetime
from flask_mail import Message
import qrcode
import io
import re

reservas_bp = Blueprint("reservas", __name__)

capacidad_max = 10

def generar_qr(datos: str) -> bytes:
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=4,
    )
    qr.add_data(datos)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#6d071a", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def enviar_mail_reserva(mail, nombre, email, fecha, hora, personas, id_reserva, notas=""):
    qr_texto = (
        f"----ALTEZZA RISTORANTE----\n"
        f"Reserva #{id_reserva}\n"
        f"Nombre: {nombre}\n"
        f"Fecha: {fecha}\n"
        f"Hora: {hora}\n"
        f"Personas: {personas}"
    )
    qr_texto += f"\nNotas: {notas}" if notas else "\nSin notas adicionales"
 
    qr_bytes = generar_qr(qr_texto)
 
    mensaje = Message(
        subject=f"Tu reserva en Altezza - #{id_reserva}",
        sender="altezzaadmin@gmail.com",
        recipients=[email],
    )
    mensaje.body = (
        f"Hola {nombre},\n\n"
        f"Tu reserva fue confirmada con éxito.\n\n"
        f"  Reserva N°: {id_reserva}\n"
        f"  Fecha: {fecha}\n"
        f"  Hora: {hora}\n"
        f"  Personas: {personas}\n"
        + (f"  Notas: {notas}\n" if notas else "")
        + f"\nPresentá el QR adjunto al llegar al restaurante.\n\n"
        f"¡Te esperamos!\n"
        f"Altezza Ristorante · Av. Del Libertador 6820, CABA"
    )
    mensaje.attach(
        filename=f"reserva_{id_reserva}_qr.png",
        content_type="image/png",
        data=qr_bytes,
        disposition="attachment",
    )
    mail.send(mensaje)

@reservas_bp.route("/disponibilidad", methods=["GET"])
def esta_disponible():
    #se manda la fecha como query params
    fecha = request.args.get('fecha')
    
    if not fecha:
        return jsonify({"error": "Falta el parámetro 'fecha'"}), 400

    horarios_disp = ["20:00", "20:30", "21:00", "21:30", "22:00"]
    
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
    except:
        return jsonify({"Error": "Error de conexion con la base de datos"}),500
    
    cursor.execute("""SELECT hora, COUNT(*) as total
                   FROM reservas WHERE fecha = %s AND estado = %s 
                   GROUP BY hora""", (fecha, "pendiente"))
    resultados = cursor.fetchall()

    if resultados >= 10:
        esta_disponible = False
    else:
        esta_disponible = True

    cursor.close()
    conn.close()

    rdo = {"esta_disp": f"{esta_disponible}"}
    return jsonify(rdo), 200

reservas_bp.route("/disponibilidad", methods=["GET"])
def esta_disponible():
    # se manda la fecha como query param
    fecha = request.args.get('fecha')
 
    if not fecha:
        return jsonify({"error": "Falta el parámetro 'fecha'"}), 400
 
    horarios_disp = ["20:00", "20:30", "21:00", "21:30", "22:00"]
 
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
    except Exception:
        return jsonify({"error": "Error de conexión con la base de datos"}), 500
 
    cursor.execute("""
        SELECT hora, COALESCE(SUM(cantidad_personas), 0) AS ocupacion
        FROM reservas WHERE fecha = %s AND estado = 'confirmada'
        GROUP BY hora
    """, (fecha,))
    resultados = cursor.fetchall()
 
    cursor.close()
    conn.close()
 
    ocupacion_por_hora = {fila["hora"]: fila["ocupacion"] for fila in resultados}
 
    disponibilidad = {
        horario: (ocupacion_por_hora.get(horario, 0) < capacidad_max)
        for horario in horarios_disp
    }
 
    return jsonify({"disponibilidad": disponibilidad}), 200
 
@reservas_bp.route("/", methods=["POST"])
def crear_reserva():
    patron = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+\.[A-Za-z]{2,}$"
    datos = request.get_json()
 
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
    except Exception:
        return jsonify({"error": "Error de conexión con la base de datos"}), 500
 
    for campo in ["nombre", "email", "telefono", "personas", "fecha", "hora"]:
        if not datos or not datos.get(campo):
            return jsonify({"error": f"Falta el campo '{campo}'"}), 400
 
    nombre = datos["nombre"]
    email = datos["email"].strip()
    telefono = datos["telefono"]
    personas = int(datos["personas"])
    fecha = datos["fecha"]
    hora = datos["hora"]
    notas = datos.get("notas", "")
 
    if not re.match(patron, email):
        return jsonify({"error": "Ingresá un email válido"}), 400
 
    try:
        fecha_ = datetime.strptime(fecha, "%Y-%m-%d").date()
        if fecha_ < datetime.now().date():
            return jsonify({"error": "No podés reservar en una fecha pasada"}), 400
        if fecha_.weekday() not in [3, 4, 5, 6]:
            return jsonify({"error": "Solo aceptamos reservas de jueves a domingo"}), 400
    except ValueError:
        return jsonify({"error": "Formato de fecha inválido"}), 400
 
 
    cursor.execute("""
        SELECT COALESCE(SUM(cantidad_personas), 0) AS total
        FROM reservas WHERE fecha = %s AND hora = %s AND estado = 'confirmada'
        """, (fecha, hora))
 
    ocupacion = cursor.fetchone()["total"]
 
    if ocupacion + personas > capacidad_max:
        cursor.close()
        conn.close()
        return jsonify({"error": "El horario seleccionado excede la capacidad disponible"}), 409
 
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
 
    mail = Mail(current_app._get_current_object())
    try:
        enviar_mail_reserva(mail, nombre, email, fecha, hora, personas, id_reserva, notas)
    except Exception:
        conn.rollback()
        cursor.close()
        conn.close()
        return jsonify({
            "error": "No pudimos enviarte el mail de confirmación, así que la reserva no se guardó. Intentá de nuevo en unos minutos."
        }), 500
 
    conn.commit()
    cursor.close()
    conn.close()
 
    return jsonify({"mensaje": "Reserva confirmada exitosamente", "id_reserva": id_reserva}), 201

@reservas_bp.route("/<int:id>", methods=["POST"])
def borrar_reserva(id):
    if id < 0:
        return jsonify({"error": "Ingresar id valido, id > 0"}), 409
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
    except Exception:
        return jsonify({"error": "Error de conexión con la base de datos"}), 500

    cursor.execute("SELECT * FROM reservas WHERE id_reserva = %s", (id,))
    reserva = cursor.fetchone()
    if not reserva:
        cursor.close()
        conn.close()
        return jsonify({"error": "Reserva no encontrada"}), 404 
    
    cursor.execute("DELETE FROM reservas WHERE id_reserva = %s", (id,))
        
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"mensaje": "Reserva eliminada"}), 200