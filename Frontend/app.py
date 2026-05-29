from flask import Flask, render_template
from routes.routes import mis_rutas
from routes.auth import auth_bp

app = Flask(__name__)
app.secret_key = "altezza_password"

app.register_blueprint(mis_rutas, url_prefix="")
app.register_blueprint(auth_bp)

@app.errorhandler(404)
def pagina_no_encontrada(e):
    return render_template("404.html"), 404

if __name__ == "__main__":
    app.run(port=5001, debug=True)
