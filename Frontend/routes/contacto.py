from flask import Blueprint, render_template, request, current_app
from flask_mail import Message,Mail
import re

contacto_bp = Blueprint("contacto", __name__)

@contacto_bp.route("/contacto", methods=["GET", "POST"])
def contactanos():

    if request.method == "POST":

        nombre = request.form.get("fnombre", "").strip()
        email = request.form.get("femail", "").strip()
        mensaje = request.form.get("fmensaje", "").strip()
        patron = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+.[A-Za-z]{2,}$"
        
        if not nombre or not email or not mensaje:
            return render_template("contacto.html", error="Por favor complete todos los campos")
        
        if not re.match(patron,email):
            return render_template("contacto.html", error="Por favor ingrese un E-mail valido")
        
        mensaje_mail = Message(
            subject="Nuevo mensaje de ALTEZZA-clientes",
            recipients=["altezzaadmin@gmail.com"],
            reply_to=email,
        )   

        mensaje_mail.body = render_template("e-mail_contacto.txt", nombre=nombre, email=email, mensaje=mensaje)
        mail = Mail(current_app)

        try:
            mail.send(mensaje_mail)
        except Exception:
            return render_template("contacto.html", error="No pudimos enviar el mensaje")
        
        return render_template("contacto.html",exito="Mensaje enviado correctamente")

    return render_template("contacto.html")


