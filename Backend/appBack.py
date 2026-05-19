from flask import Flask,render_template
from routes.menu import menu_bp
from routes.resenas import resenas_bp
from routes.contacto import contacto_bp
from routes.reservas import reservas_bp



app = Flask(__name__)

app.register_blueprint(menu_bp, url_prefix="/menu")
app.register_blueprint(resenas_bp, url_prefix = "/resenas")
app.register_blueprint(contacto_bp, url_prefix = "/contacto")
app.register_blueprint(reservas_bp, url_prefix = "/reservas")


if __name__ == "__main__":
    app.run(port="5001", debug=True)

