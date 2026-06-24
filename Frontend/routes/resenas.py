from flask import Blueprint, render_template, session, redirect, url_for, request, flash
import requests
from routes.auth import admin_requerido, BACKEND_URL

resenas_bp = Blueprint('resenas', __name__)


@resenas_bp.route("/resenas", methods=["GET", "POST"])
def resenas():
    if request.method == "POST":
        data = {
            "nombre": request.form.get("f_nombre"),
            "mensaje": request.form.get("f_mensaje"),
            "puntuacion": request.form.get("f_puntuacion")
        }
        try:
            response = requests.post(f"{BACKEND_URL}/resenas", json=data, timeout=5)
            if response.status_code != 201:
                error = response.json().get("error", "Error al enviar la reseña.")
                flash(error, "error")
            else:
                flash("¡Reseña enviada! Quedara visible una vez aprobada.", "exito")
        except requests.exceptions.RequestException:
            flash("Error de conexión con el servidor", "error")
    try:
        response = requests.get(f"{BACKEND_URL}/resenas", timeout=5)
        data = response.json()
        resenas = data.get("resenas", [])
    except requests.exceptions.RequestException:
        resenas = []
    return render_template("resenas.html", resenas=resenas)


@resenas_bp.route("/admin/resenas", methods=["GET"])
@admin_requerido
def admin_resenas():
    try:
        token = session.get("jwt_token")
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BACKEND_URL}/admin/resenas", headers=headers, timeout=5)
        data = response.json()
        resenas = data.get("resenas", [])
    except:
        resenas = []
    return render_template("admin/admin_resenas.html", resenas=resenas)


@resenas_bp.route("/admin/resenas/eliminar/<int:id>", methods=["POST"])
@admin_requerido
def eliminar_resena(id):
    token = session.get("jwt_token")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.delete(f"{BACKEND_URL}/admin/resenas/{id}", headers=headers, timeout=5)

        if response.status_code != 204:
            flash("Error al eliminar la reseña", "error")
        else:
            flash("Reseña eliminada correctamente", "exito")

    except requests.exceptions.RequestException:
        print("Error al eliminar reseña")
        flash("Error de conexión con el servidor", "error")
    return redirect(url_for("resenas.admin_resenas"))


@resenas_bp.route("/admin/resenas/<int:id>/estado", methods=["POST"])
@admin_requerido
def cambiar_estado_resena(id):
    nuevo_estado = request.form.get("estado")
    token = session.get("jwt_token")
    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.put(
            f"{BACKEND_URL}/admin/resenas/{id}/estado",
            json={"estado": nuevo_estado},
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            flash(f"Reseña marcada como {nuevo_estado}", "exito")
        else:
            flash("Error al cambiar el estado", "error")
    except requests.exceptions.RequestException:
        flash("Error al conectar con el servidor para cambiar estado", "error")

    return redirect(url_for('resenas.admin_resenas'))
