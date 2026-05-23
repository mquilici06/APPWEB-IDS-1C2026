from flask import Flask, render_template, Blueprint
from Backend.routes.platos import menu_bp
from Backend.routes.resenas import resenas_bp
from Backend.routes.reservas import reservas_bp
from Backend.routes.admin import admin_bp

app = Flask(__name__)

app.register_blueprint(menu_bp, url_prefix="/platos")
app.register_blueprint(resenas_bp, url_prefix = "/resenas")
app.register_blueprint(reservas_bp, url_prefix = "/reservas")
app.register_blueprint(admin_bp, url_prefix = "/admin")

if __name__ == "__main__":
    app.run(port=5000, debug=True)

