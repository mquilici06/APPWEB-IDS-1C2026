from flask import Blueprint, render_template, session, redirect, url_for, request, flash
import requests
from routes.auth import admin_requerido, BACKEND_URL
from datetime import datetime

reservas_bp = Blueprint('reservas', __name__)


@reservas_bp.route('/reservas', methods=['GET', 'POST'])
def crear_reservas():

    if request.method == 'POST':
        datos_reserva = {
            "nombre": request.form.get('f_nombre'),
            "email": request.form.get('f_email'),
            "telefono": request.form.get('f_telefono'),
            "personas": request.form.get('f_personas'),
            "fecha": request.form.get('f_fecha_reserva'),
            "horario": request.form.get('f_hora'),
            "notas": request.form.get('f_notas', '')
        }
        respuesta = requests.get(f"{BACKEND_URL}/reservas/disponibilidad?fecha={datos_reserva['fecha']}&hora={datos_reserva['horario']}&cliente={datos_reserva['personas']}")
        se_puede = respuesta.json()
        se_puede = se_puede.get("esta_disp")
        if se_puede:
            try:
                respuesta = requests.post(f"{BACKEND_URL}/reservas/", json=datos_reserva, timeout=15)
                resultado = respuesta.json()

                if respuesta.status_code != 201:
                    lista_errores = resultado.get('errors', [])
                    mensaje_error = lista_errores[0].get('description', 'Error al procesar la reserva.') if lista_errores else 'Error al procesar la reserva.'
                    return redirect(url_for("reservas.crear_reservas", aviso=mensaje_error, tipo="error"))

                return redirect(url_for("reservas.crear_reservas", aviso="¡Reserva confirmada con éxito! Revisá tu mail.", tipo="exito"))

            except requests.exceptions.RequestException:
                return redirect(url_for("reservas.crear_reservas", aviso="Error de conexión con el servidor", tipo="error"))
        else:
            return redirect(url_for("reservas.crear_reservas", aviso="No hay disponibilidad para ese horario", tipo="error"))
    aviso = request.args.get("aviso")
    tipo = request.args.get("tipo")

    return render_template('reservas.html', aviso=aviso, tipo=tipo)


@reservas_bp.route('/reservas/cancelar/<int:id_reserva>', methods=['GET'])
def cancelar_reserva(id_reserva):
    email = request.args.get("email", "").strip()

    if not email:
        return render_template("reserva_cancelada.html", exito=False,
                                mensaje="Falta el email para confirmar la cancelación.")

    try:
        respuesta = requests.delete(
            f"{BACKEND_URL}/reservas/cancelar/{id_reserva}",
            json={"email": email},
            timeout=10
        )
    except requests.exceptions.RequestException:
        return render_template("reserva_cancelada.html", exito=False,
                                mensaje="Error de conexión con el servidor.")

    if respuesta.status_code == 200:
        return render_template("reserva_cancelada.html", exito=True, id_reserva=id_reserva)

    resultado = respuesta.json()
    lista_errores = resultado.get("errors", [])
    mensaje_error = lista_errores[0].get("description", "No pudimos cancelar la reserva.") if lista_errores else "No pudimos cancelar la reserva."
    return render_template("reserva_cancelada.html", exito=False, mensaje=mensaje_error)


@reservas_bp.route("/admin/reservas", methods=['GET'])
@admin_requerido
def admin_reservas():
    buscar = request.args.get('buscar', '')
    fecha = request.args.get('fecha', '')
    estado = request.args.get('estado', '')

    parametros = {
        'buscar': buscar,
        'fecha': fecha,
        'estado': estado
    }

    token = session.get("jwt_token")
    headers = {"Authorization": f"Bearer {token}"}

    reservas = []
    try:
        respuesta = requests.get(f"{BACKEND_URL}/admin/reservas", params=parametros, headers=headers)
        if respuesta.status_code == 401:
            return redirect(url_for("auth.login_admin"))
        if respuesta.status_code == 200:
            datos = respuesta.json()
            reservas = datos.get("Reservas", [])
    except Exception:
        reservas = []

    hoy = datetime.now().strftime('%Y-%m-%d')
    total_hoy = 0
    pendientes = 0
    confirmadas = 0

    for reserva in reservas:
        if reserva.get('fecha') == hoy:
            total_hoy += 1

        estado_reserva = reserva.get('estado', 'Pendiente').lower()
        if estado_reserva == 'pendiente':
            pendientes += 1
        elif estado_reserva == 'confirmada':
            confirmadas += 1

    indicadores = {
        'total_hoy': total_hoy,
        'pendientes': pendientes,
        'confirmadas': confirmadas
    }

    return render_template(
        '/admin/admin_reservas.html',
        reservas=reservas,
        indicadores=indicadores,
        filtro_buscar=buscar,
        filtro_fecha=fecha,
        filtro_estado=estado
    )


@reservas_bp.route("/admin/reservas/estado/<int:id>", methods=["POST"])
@admin_requerido
def cambiar_estado_reserva(id):
    nuevo_estado = request.form.get("nuevo_estado")

    token = session.get("jwt_token")
    headers = {"Authorization": f"Bearer {token}"}

    try:
        respuesta = requests.put(
            f"{BACKEND_URL}/admin/reservas/{id}/estado",
            json={"estado": nuevo_estado},
            headers=headers,
            timeout=5
        )

        if respuesta.status_code == 200:
            flash(f"Reserva {nuevo_estado} exitosamente.", "exito")
        else:
            flash("Error al actualizar la reserva en el backend.", "error")

    except requests.exceptions.RequestException:
        flash("Error de conexión con el servidor.", "error")

    return redirect(url_for("reservas.admin_reservas"))


@reservas_bp.route("/admin/reservas/cancelar/<int:id>", methods=["POST"])
@admin_requerido
def admin_cancelar_reserva(id):
    token = session.get("jwt_token")
    headers = {"Authorization": f"Bearer {token}"}

    try:
        respuesta = requests.delete(
            f"{BACKEND_URL}/admin/reservas/{id}/eliminar",
            headers=headers,
            timeout=5
        )

        if respuesta.status_code == 200:
            flash("Reserva eliminada correctamente.", "exito")
        else:
            flash("Error al eliminar la reserva en el backend.", "error")

    except requests.exceptions.RequestException:
        flash("Error de conexión con el servidor.", "error")

    return redirect(url_for("reservas.admin_reservas"))


@reservas_bp.route("/admin/reservas/<int:id>/confirmar")
@admin_requerido
def confirmar_reserva_qr(id):

    return render_template(
        "admin/admin_confirmar_reserva_qr.html",
        id_reserva=id
    )
