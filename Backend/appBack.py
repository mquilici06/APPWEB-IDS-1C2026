from flask import Flask, render_template, Blueprint
from flask_cors import CORS
from routes.platos import menu_bp
from routes.resenas import resenas_bp
from routes.reservas import reservas_bp
from routes.admin import admin_bp
from flask_jwt_extended import JWTManager
from routes.servicios_extras import servicios_extras_bp
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
jwt = JWTManager(app)

CORS(app)

app.register_blueprint(menu_bp, url_prefix="/platos")
app.register_blueprint(resenas_bp, url_prefix = "/resenas")
app.register_blueprint(reservas_bp, url_prefix = "/reservas")
app.register_blueprint(admin_bp, url_prefix = "/admin")
app.register_blueprint(servicios_extras_bp, url_prefix = "/servicios_extras")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

