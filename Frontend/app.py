from flask import Flask, render_template
from flask_mail import Mail
from routes.core import core_bp
from routes.reservas import reservas_bp
from routes.resenas import resenas_bp
from routes.menu import menu_bp
from routes.servicios_extras import servicios_bp
from routes.auth import auth_bp
from routes.contacto import contacto_bp
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

app.register_blueprint(core_bp, url_prefix="")
app.register_blueprint(reservas_bp, url_prefix="")
app.register_blueprint(resenas_bp, url_prefix="")
app.register_blueprint(menu_bp, url_prefix="")
app.register_blueprint(servicios_bp, url_prefix="")
app.register_blueprint(auth_bp)
app.register_blueprint(contacto_bp)

app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER")
app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", 587))
app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS", "False").lower() == "true"
app.config["MAIL_USE_SSL"] = os.getenv("MAIL_USE_SSL", "False").lower() == "true"
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")  
app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_DEFAULT_SENDER")

mail = Mail(app)


@app.errorhandler(404)
def pagina_no_encontrada(e):
    return render_template("404.html"), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)