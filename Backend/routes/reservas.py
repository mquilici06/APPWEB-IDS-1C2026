from flask import Blueprint, request, jsonify
from database.db import get_connection
from datetime import datetime
import qrcode
import io

reservas_bp = Blueprint("reservas", __name__)

def _generar_qr(datos: str) -> bytes:
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

def _enviar_mail_reserva(mail, nombre, email, fecha, hora, personas, id_reserva, notas=""):

    qr_texto = (
        f"----ALTEZZA RISTORANTE----\n"
        f"Reserva #{id_reserva}\n"
        f"Nombre: {nombre}\n"
        f"Fecha: {fecha}\n"
        f"Hora: {hora}\n"
        f"Personas: {personas}"
    )
    if notas:
        qr_texto += f"\nNotas: {notas}"
    else :
        qr_texto += "\nSin notas adicionales"


 
    qr_bytes = _generar_qr(qr_texto)
 
    mensaje = Message(
        subject=f"Tu reserva en Altezza - #{id_reserva}",
        recipients=[email],
    )
 
    mensaje.body = (
        f"Hola {nombre},\n\n"
        f"Tu reserva fue confirmada con éxito.\n\n"
        f" -Reserva N°: {id_reserva}\n"
        f" -Fecha:      {fecha}\n"
        f" -Hora:       {hora}\n"
        f" -Personas:   {personas}\n"
        if notas:
            f" -Notas:      {notas}\n"
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
def consultar_disponibilidad():
    #se manda la fecha como query params
    fecha = request.args.get('fecha')
    
    if not fecha:
        return jsonify({"error": "Falta el parámetro 'fecha'"}), 400

    horarios_disp = ["20:00", "20:30", "21:00", "21:30", "22:00"]
    capacidad_max = 10
    
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
    except:
        return jsonify({"Error": "Error de conexion con la base de datos"}),500
    
    cursor.execute("""SELECT hora, COUNT(*) as total
                   FROM reservas WHERE fecha = %s AND estado = %s 
                   GROUP BY hora""", (fecha, "confirmada"))
    resultados = cursor.fetchall()

    ocupacion = {}
    for fila in resultados: #Por cada Fila que trajo (ej: {'hora': 20:00:00, 'total': 5})
        hora_limpia = str(fila['hora'])[:5]
        ocupacion[hora_limpia] = fila['total']

    disponibilidad = []
    for h in horarios_disp:
        cantidad = ocupacion.get(h, 0)#consulta disponibilidad en c/u horario, si no hay devuelve 0
        disponibilidad.append({
            "hora": h,
            "estado": "disponible" if cantidad < capacidad_max else "agotado",
            "lugares_libres": capacidad_max - cantidad
        })
    
    cursor.close()
    conn.close()

    return jsonify(disponibilidad), 200

@reservas_bp.route("/", methods=["POST"])
def crear_reserva():
    datos = request.get_json()
    campos_requeridos = ["nombre", "email", "telefono", "personas", "fecha", "hora"]
    for campo in campos_requeridos:
        if not datos or not datos.get(campo):
            return jsonify({"error": f"Falta el campo '{campo}'"}), 400
 
    nombre = datos["nombre"]
    email = datos["email"]
    telefono = datos["telefono"]
    personas = datos["personas"]
    fecha = datos["fecha"]
    hora = datos["hora"]
    notas = datos.get("notas")

    try:
        fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
        if fecha_obj < datetime.now().date():
            return jsonify({"error": "no podés realizar una reserva en una fecha pasada"}), 400
    except ValueError:
        return jsonify({"error": "formato de fecha inválido"}), 400
    
    try:
        conn   = get_connection()
        cursor = conn.cursor(dictionary=True)
    except:
        return jsonify({"Error": "Error de conexion con la base de datos"}), 500
    cursor.execute("""
        SELECT COUNT(*) as total FROM reservas 
        WHERE fecha = %s AND hora = %s AND estado = %s
    """, (fecha, hora, "confirmada"))
    ocupacion = cursor.fetchone()["total"]

    if ocupacion + int(personas) > capacidad_max: 
        cursor.close()
        conn.close()
        return jsonify({"error": "El horario seleccionado excede la capacidad disponible"}), 409

    cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
    usuario_existente = cursor.fetchone()

    if usuario_existente:
        id_cliente = usuario_existente["id"]   
    else:  
        cursor.execute(
        "INSERT INTO usuarios (nombre, email, celular, rol) VALUES (%s, %s, %s, 'cliente')",
        (nombre, email, telefono))
        id_cliente = cursor.lastrowid 
    
    try:
     _enviar_mail_reserva(mail, nombre, email, fecha, hora, personas, id_reserva, notas)
    except:
        cursor.close()
        conn.close()
        return jsonify({"error": "No se pudo enviar el mail de confirmación. La reserva no fue guardada."}), 500

    cursor.execute("""
        INSERT INTO reservas (id_cliente, fecha, hora, cantidad_personas, estado) 
        VALUES (%s, %s, %s, %s, %s)
        """, (id_cliente, fecha, hora, personas, "confirmada"))
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