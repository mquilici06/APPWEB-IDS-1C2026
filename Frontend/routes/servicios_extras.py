from flask import Blueprint, render_template, session, redirect, url_for, request, flash
import requests
from routes.auth import admin_requerido, BACKEND_URL

servicios_bp = Blueprint('servicios', __name__)


@servicios_bp.route("/accesibilidad", methods=["GET"])
def servicios_extras():
    try:
        respuesta = requests.get(f"{BACKEND_URL}/servicios_extras", timeout=5)
        servicios = respuesta.json().get("servicios_extras", [])
    except requests.exceptions.RequestException:
        flash("Error de conexión con el Backend", "error")
        servicios = []

    return render_template('servicios_extras.html', servicios_extras=servicios)


@servicios_bp.route("/admin/accesibilidad", methods=["GET", "POST"])
@admin_requerido
def admin_servicios_extras():

    if request.method == "POST":
        datos = {
            "nombre_servicio": request.form.get("nombre_servicio"),
            "descripcion_servicio": request.form.get("descripcion_servicio")
        }
        editar_id = request.args.get("editar_id")

        token = session.get("jwt_token")
        headers = {"Authorization": f"Bearer {token}"}

        try:
            if editar_id:
                respuesta = requests.put(
                    f"{BACKEND_URL}/admin/servicios_extras/{editar_id}",
                    json=datos,
                    headers=headers,
                    timeout=5
                )
                if respuesta.status_code == 200:
                    flash("Servicio actualizado correctamente", "exito")
                else:
                    flash(respuesta.json().get("Mensaje", "Error al actualizar"), "error")
            else:
                respuesta = requests.post(
                    f"{BACKEND_URL}/admin/servicios_extras",
                    json=datos,
                    headers=headers,
                    timeout=5
                )
                if respuesta.status_code == 201:
                    flash("Servicio agregado correctamente", "exito")
                else:
                    flash(respuesta.json().get("Error", "Error al agregar"), "error")

        except requests.exceptions.RequestException:
            flash("Error de conexión con el servidor", "error")

        return redirect(url_for("servicios.admin_servicios_extras"))

    token = session.get("jwt_token")
    headers = {"Authorization": f"Bearer {token}"}

    try:
        respuesta = requests.get(f"{BACKEND_URL}/admin/servicios_extras", headers=headers, timeout=5)
        servicios = respuesta.json().get("servicios_extras", [])
    except:
        servicios = []
        flash("Error al cargar los servicios", "error")

    servicio_a_editar = None
    editar_id = request.args.get("editar_id")
    if editar_id:
        servicio_a_editar = next(
            (s for s in servicios if str(s["id_servicio"]) == editar_id),
            None
        )

    return render_template(
        "admin/admin_servicios_extras.html",
        servicios=servicios,
        servicio_a_editar=servicio_a_editar
    )


@servicios_bp.route("/admin/servicios_extras/eliminar/<int:id>", methods=["POST"])
@admin_requerido
def eliminar_servicio(id):
    token = session.get("jwt_token")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        respuesta = requests.delete(
            f"{BACKEND_URL}/admin/servicios_extras/{id}",
            headers=headers,
            timeout=5
        )
        if respuesta.status_code == 200:
            flash("Servicio eliminado correctamente", "exito")
        else:
            flash("Error al eliminar el servicio", "error")
    except requests.exceptions.RequestException:
        flash("Error de conexión con el servidor", "error")

    return redirect(url_for("servicios.admin_servicios_extras"))
