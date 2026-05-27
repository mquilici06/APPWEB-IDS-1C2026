from flask import Blueprint, render_template

mis_rutas = Blueprint('rutas_prefijo_api', __name__)

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

@mis_rutas.route("/admin")
def admin():
    return render_template("base_admin.html")

@mis_rutas.route("/login/admin")
def admin_login():
    return render_template("admin_login.html")

@mis_rutas.route("/admin/reservas")
def admin_reservas():
    return render_template("admin_reservas.html")

@mis_rutas.route('/admin/resenas')
def admin_resenas():
    return render_template('admin_resenas.html')

