from flask import Blueprint, render_template
import requests

mis_rutas = Blueprint('rutas_prefijo_api', __name__)

@mis_rutas.route("/menu")
def menu():
    response = requests.get("http://127.0.0.1:5000/platos")
    data = response.json()
    platos = data.get("Menu", [])
    return render_template("menu.html", platos=platos)

@mis_rutas.route("/index")
def index():
    return render_template("index.html")