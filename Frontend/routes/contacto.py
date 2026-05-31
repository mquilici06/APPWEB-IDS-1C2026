from flask import Blueprint, render_template, request

contacto_bp = Blueprint("contacto", __name__)

@contacto_bp.route("/contacto", methods=["GET", "POST"])
def contactanos():

    if request.method == "POST":

        nombre = request.form.get("fnombre", "").strip()
        email = request.form.get("femail", "").strip()
        mensaje = request.files.get("fmensaje", "").strip()


        return render_template("contacto.html")
    
    return render_template("contacto.html")
#no esta terminado falta que agregue la logica del mail con flask-mail

