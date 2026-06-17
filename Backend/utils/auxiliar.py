from flask import Blueprint,jsonify,request
from Backend.database.db import get_connection

def errores(codigo,mensaje,descripcion):
    return jsonify({
        "errors": [
            {
                "code": codigo,
                "message": mensaje,
                "description": descripcion,
                "level": "error"
            }
        ]
    }), codigo

