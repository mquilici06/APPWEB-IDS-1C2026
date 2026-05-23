from flask import Blueprint, render_template
import requests

mis_rutas = Blueprint('rutas_prefijo_api', __name__)

@mis_rutas.route("/menu")
def menu():
    return render_template("menu.html")

@mis_rutas.route("/index")
def index():
    return render_template("index.html")