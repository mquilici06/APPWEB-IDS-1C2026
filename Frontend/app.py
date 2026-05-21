from flask import Flask, render_template
from routes import mis_rutas

app = Flask(__name__)

app.register_blueprint(mis_rutas, url_prefix="/api")


@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(port=5001, debug=True)
