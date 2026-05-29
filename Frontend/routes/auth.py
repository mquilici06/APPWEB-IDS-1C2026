from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from functools import wraps
import requests

auth_bp = Blueprint("auth", __name__)

BACKEND_URL = "http://127.0.0.1:5000"

def admin_requerido(funcion):
    @wraps(funcion)
    def wrapper(*args, **kwargs):
        if session.get("rol") != "admin":
            return redirect(url_for("auth.login_admin"))
        return funcion(*args, **kwargs)
    return wrapper


@auth_bp.route("/admin/login", methods=["GET", "POST"])
def login_admin():
    if request.method == "POST":
        email = request.form.get("femail", "").strip()
        contrasena = request.form.get("fcontrasena", "").strip()

        try:
            respuesta = requests.post(
                f"{BACKEND_URL}/admin/login",
                json={
                    "femail": email,
                    "fcontrasena": contrasena
                },
                timeout=10
            )
            resultado = respuesta.json()

        except requests.exceptions.RequestException:
            flash("No se pudo conectar con el servidor", "error")
            return redirect(url_for("auth.login_admin"))

        if resultado.get("ok"):
            session["usuario_id"] = resultado["usuario"]["id"]
            session["rol"] = resultado["usuario"]["rol"]
            return redirect(url_for("frontend.admin"))

        flash(resultado.get("mensaje", "Error al iniciar sesión"), "error")
        return redirect(url_for("auth.login_admin"))

    return render_template("admin/admin_login.html")