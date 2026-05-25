from flask import Blueprint, request, jsonify
from Backend.database.db import get_connection

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
 
    campos_requeridos = [ "personas", "fecha", "hora"]
    for campo in campos_requeridos:
        if not datos or not datos.get(campo):
            return jsonify({"error": f"Falta el campo '{campo}'"}), 400
 
    personas = datos["personas"]
    fecha    = datos["fecha"]
    hora     = datos["hora"]

    try:
        conn   = get_connection()
        cursor = conn.cursor(dictionary=True)
    except Exception:
        return jsonify({"error": "Error de conexión con la base de datos"}), 500


    cursor.execute("""
        SELECT COUNT(*) as total FROM reservas WHERE fecha = %s AND hora = %s AND estado = %s
    """, (fecha, hora, "confirmada"))

    ocupacion =  cursor.fetchone()["total"]

    if ocupacion >= 10:
        cursor.close()
        conn.close()
        return jsonify({"error": "El horario seleccionado ya no tiene lugares disponibles"}), 409
 
    cursor.execute("""
        INSERT INTO reservas (fecha, hora,cantidad_personas, estado) VALUES (%s, %s, %s, %s)
        """, (fecha, hora, personas, "confirmada"))
 
    conn.commit()
 
    cursor.close()
    conn.close()
 
    return jsonify({"mensaje":    "Reserva confirmada"}), 201


