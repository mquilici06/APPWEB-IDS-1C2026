from flask import Blueprint, request, jsonify
from database.db import get_connection
from datetime import datetime

reservas_bp = Blueprint("reservas", __name__)

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

    if ocupacion + int(personas) > 10: 
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
            (nombre, email, telefono)
        )
        id_cliente = cursor.lastrowid 
    cursor.execute("""
        INSERT INTO reservas (id_cliente, fecha, hora, cantidad_personas, estado) 
        VALUES (%s, %s, %s, %s, %s)
    """, (id_cliente, fecha, hora, personas, "confirmada"))
 
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"mensaje": "Reserva confirmada exitosamente"}), 201

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