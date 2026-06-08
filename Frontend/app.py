from flask import Flask, render_template
from flask_mail import Mail
from routes.routes import mis_rutas
from routes.auth import auth_bp
from routes.contacto import contacto_bp

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.secret_key = "altezza_password"

app.register_blueprint(mis_rutas, url_prefix="")
app.register_blueprint(auth_bp)
app.register_blueprint(contacto_bp)

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False
app.config["MAIL_USERNAME"] = "altezzaadmin@gmail.com"
app.config["MAIL_PASSWORD"] = "wvbktnqaujhizdji"  #hay q pasarlo a constante dsp seguro creo un .env para guardar datos mas seguro
app.config["MAIL_DEFAULT_SENDER"] = "altezzaadmin@gmail.com"

mail = Mail(app)


@app.errorhandler(404)
def pagina_no_encontrada(e):
    return render_template("404.html"), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
