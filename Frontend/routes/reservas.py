from flask import Blueprint, render_template, request
import requests
import os
 
 
reservas_bp = Blueprint("reservas", __name__)
 
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:5000")
 
@reservas_bp.route("/", methods=["GET", "POST"])
def crear_reserva():
    if request.method == "GET":
        return render_template("reservas.html")
 
    datos = {
        "nombre": request.form.get("fnombre"),
        "email": request.form.get("femail"),
        "telefono": request.form.get("ftelefono"),
        "personas": request.form.get("fpersonas"),
        "fecha": request.form.get("ffecha_reserva"),
        "hora": request.form.get("fhora"),
        "notas": request.form.get("fnotas", ""),
    }
 
    try:
        resp = requests.post(f"{BACKEND_URL}/reservas/", json=datos, timeout=10)
        resultado = resp.json()
    except Exception:
        return render_template(
            "reservas.html",
            error="No se pudo conectar con el servidor. Intentá de nuevo más tarde."
        )
 
    if resp.status_code == 201:
        return render_template(
            "reservas.html",
            exito=f"¡Reserva confirmada! Te enviamos el QR al mail. N° de reserva: {resultado.get('id_reserva')}"
        )
    else:
        return render_template(
            "reservas.html",
            error=resultado.get("error", "Verifica que los campos esten completos y sean correctos e intentá de nuevo.")
        )