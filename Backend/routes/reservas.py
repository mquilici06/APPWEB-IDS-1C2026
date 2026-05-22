from flask import Blueprint, request, jsonify
from database.db import get_connection

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