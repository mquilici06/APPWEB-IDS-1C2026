from flask import Flask, render_template, Blueprint
from flask_cors import CORS
from routes.platos import menu_bp
from routes.resenas import resenas_bp
from routes.reservas import reservas_bp
from routes.admin import admin_bp
from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.secret_key = "altezza_password"  
app.config["JWT_SECRET_KEY"] = "altezza_jwt_password"
jwt = JWTManager(app)

CORS(app)

app.register_blueprint(menu_bp, url_prefix="/platos")
app.register_blueprint(resenas_bp, url_prefix = "/resenas")
app.register_blueprint(reservas_bp, url_prefix = "/reservas")
app.register_blueprint(admin_bp, url_prefix = "/admin")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

