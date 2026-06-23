from flask import Blueprint, render_template, session, redirect, url_for, request, flash
import requests
from routes.auth import admin_requerido, BACKEND_URL

menu_bp = Blueprint('menu', __name__)


@menu_bp.route("/menu")
def menu():
    try:
        response = requests.get(f"{BACKEND_URL}/platos")
        data = response.json()
        platos = data.get("platos", [])
    except:
        platos = []
    return render_template("menu.html", platos=platos)


@menu_bp.route('/admin/menu', methods=['GET', 'POST'])
@admin_requerido
def admin_menu():
    if request.method == 'POST':
        token = session.get("jwt_token")
        headers = {"Authorization": f"Bearer {token}"}

        datos_plato = {
            "nombre": request.form.get("nombre_plato"),
            "descripcion": request.form.get("desc_plato"),
            "precio": request.form.get("precio"),
            "seccion": request.form.get("seccion"),
            "restricciones": request.form.get("restricciones")
        }


        archivo = request.files.get("imagen_plato")
        files = {}
        if archivo and archivo.filename != '':

            files = {'imagen_plato': (archivo.filename, archivo.read(), archivo.content_type)}

        actualizar_id = request.args.get('actualizar_id', type=int)

        try:
            if actualizar_id:
                respuesta = requests.put(f"{BACKEND_URL}/platos/{actualizar_id}", data=datos_plato, files=files, headers=headers, timeout=10)
                mensaje_ok = "Plato actualizado correctamente"
            else:
                respuesta = requests.post(f"{BACKEND_URL}/platos", data=datos_plato, files=files, headers=headers, timeout=10)
                mensaje_ok = "Plato guardado correctamente"

            if respuesta.status_code in [200, 201]:
                flash(mensaje_ok, "exito")
            else:
                flash(f"Error al procesar: {respuesta.text}", "error")
        except requests.exceptions.RequestException:
            flash("Error de conexión con el Backend", "error")

        return redirect(url_for('menu.admin_menu'))


    try:
        response = requests.get(f"{BACKEND_URL}/platos")
        platos = response.json().get("platos", [])
    except:
        platos = []

    editar_id = request.args.get('editar_id', type=int)
    plato_a_editar = None
    if editar_id:
        plato_a_editar = next((p for p in platos if p['id_menu'] == editar_id), None)



    return render_template('admin/admin_menu.html', platos=platos, plato_a_editar=plato_a_editar)


@menu_bp.route("/admin/menu/eliminar/<int:id>", methods=["POST"])
@admin_requerido
def eliminar_plato(id):
    token = session.get("jwt_token")
    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.delete(f"{BACKEND_URL}/platos/{id}", headers=headers, timeout=5)

        if response.status_code == 200:
            flash("Plato eliminado correctamente", "exito")
        else:
            flash("Error al eliminar el plato", "error")

    except requests.exceptions.RequestException:
        flash("Error de conexión con el servidor al intentar eliminar", "error")

    return redirect(url_for("menu.admin_menu"))
