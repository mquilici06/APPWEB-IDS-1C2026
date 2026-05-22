from flask import Flask, render_template
from routes.routes import mis_rutas

app = Flask(__name__)

app.register_blueprint(mis_rutas, url_prefix="")

if __name__ == "__main__":
    app.run(port=5001, debug=True)
