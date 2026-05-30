from flask import Blueprint, render_template, session, redirect, url_for
import requests
from routes.auth import admin_requerido, BACKEND_URL

mis_rutas = Blueprint('frontend', __name__)

@mis_rutas.route("/menu")
def menu():
    return render_template("menu.html")

@mis_rutas.route("/")
def index():
    return render_template("index.html")

@mis_rutas.route("/contacto")
def contacto():
    return render_template("contacto.html")

@mis_rutas.route("/reservas")
def reservas():
    return render_template("reservas.html")

@mis_rutas.route("/resenas")
def resenas():
    try:
        response = requests.get(f"{BACKEND_URL}/resenas")
        data = response.json()
        resenas = data.get("resenas", [])
    except:
        resenas = []
    return render_template("resenas.html", resenas=resenas)

@mis_rutas.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect(url_for("auth.login_admin"))

@mis_rutas.route("/admin")
@admin_requerido
def admin():
    return render_template("admin/admin.html")

@mis_rutas.route("/admin/reservas")
@admin_requerido
def admin_reservas():
    return render_template("admin/admin_reservas.html")

@mis_rutas.route('/admin/menu')
@admin_requerido
def admin_menu():
    return render_template('admin/admin_menu.html')

@mis_rutas.route("/admin/resenas", methods=["GET"])
@admin_requerido
def admin_resenas():
    try:
        response = requests.get(f"{BACKEND_URL}/resenas")
        data = response.json()
        resenas = data.get("resenas", [])
    except:
        resenas = []
    return render_template("admin/admin_resenas.html", resenas=resenas)

@mis_rutas.route('/admin/estadisticas')
@admin_requerido
def admin_stats():
    return render_template('admin/admin_stats.html')