from flask import Blueprint, render_template, session, redirect, url_for
from functools import wraps

mis_rutas = Blueprint('rutas_prefijo_api', __name__)

def admin_requerido(funcion):
    @wraps(funcion)
    def wrapper(*args, **kwargs):
        if session.get("rol") != "admin":
            return redirect(url_for("rutas_prefijo_api.admin_login"))
        return funcion(*args, **kwargs)
    return wrapper

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
    return render_template("resenas.html")

@mis_rutas.route("/login/admin")
def admin_login():
    return render_template("admin_login.html")

@mis_rutas.route("/admin")
@admin_requerido
def admin():
    return render_template("admin.html")

@mis_rutas.route("/admin/reservas")
@admin_requerido
def admin_reservas():
    return render_template("admin_reservas.html")

@mis_rutas.route('/admin/menu')
@admin_requerido
def admin_menu():
    return render_template('admin_menu.html')

@mis_rutas.route('/admin/resenas')
@admin_requerido
def admin_resenas():
    return render_template('admin_resenas.html')

