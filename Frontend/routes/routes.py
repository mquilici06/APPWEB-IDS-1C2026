from flask import Blueprint, render_template, session, redirect, url_for, request
import requests
from routes.auth import admin_requerido, BACKEND_URL

mis_rutas = Blueprint('frontend', __name__)

@mis_rutas.route("/menu")
def menu():
    try:
        response = requests.get(f"{BACKEND_URL}/platos")
        data = response.json()
        platos = data.get("platos", [])
    except:
        platos = []
    return render_template("menu.html", platos=platos)


@mis_rutas.route("/")
def index():
    return render_template("index.html")

@mis_rutas.route('/reservas', methods=['GET', 'POST'])
def reservas():
    if request.method == 'POST':
        datos_reserva = {
            "nombre": request.form.get('f_nombre'),
            "email": request.form.get('f_email'),
            "telefono": request.form.get('f_telefono'),
            "personas": request.form.get('f_personas'),
            "fecha": request.form.get('f_fecha_reserva'),
            "hora": request.form.get('f_hora')
        }
        try:
            respuesta = requests.post(f"{BACKEND_URL}/reservas", json=datos_reserva, timeout=5)
            if respuesta.status_code != 201:
                mensaje_error = respuesta.json().get('error', 'Error al procesar la reserva.')
                return redirect(url_for("frontend.reservas", aviso=mensaje_error, tipo="error"))
            else:
                return redirect(url_for("frontend.reservas", aviso="¡Reserva confirmada con exito!", tipo="exito"))
                
        except requests.exceptions.RequestException:
            return redirect(url_for("frontend.reservas", aviso="Error de conexión con el servidor", tipo="error"))
    aviso = request.args.get("aviso")
    tipo = request.args.get("tipo")

    return render_template('reservas.html', aviso=aviso, tipo=tipo)

@mis_rutas.route("/resenas", methods=["GET", "POST"])
def resenas():
    if request.method == "POST":
        data = {
            "nombre": request.form.get("f_nombre"),
            "mensaje": request.form.get("f_mensaje"),
            "puntuacion": request.form.get("f_puntuacion")
        }
        try:
            response = requests.post(f"{BACKEND_URL}/resenas", json=data, timeout=5)
            if response.status_code != 201:
                error = response.json().get("error", "Error al enviar la reseña.")
                return redirect(url_for("frontend.resenas", aviso=error, tipo="error"))
            else:
                return redirect(url_for("frontend.resenas", aviso="¡Reseña publicada!", tipo="exito"))
        except:
            return redirect(url_for("frontend.resenas", aviso="Error de conexion con el servidor", tipo="error"))
    try:
        response = requests.get(f"{BACKEND_URL}/resenas", timeout=5)
        data = response.json()
        resenas = data.get("resenas", [])
    except:
        resenas = []
    aviso = request.args.get("aviso")
    tipo = request.args.get("tipo")
    return render_template("resenas.html", resenas=resenas, aviso=aviso, tipo=tipo)

@mis_rutas.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect(url_for("auth.login_admin"))

@mis_rutas.route("/admin")
@admin_requerido
def admin():
    return render_template("admin/admin.html")

@mis_rutas.route("/admin/reservas")
@admin_requerido
def admin_reservas():
    return render_template("admin/admin_reservas.html")



@mis_rutas.route("/admin/resenas", methods=["GET"])
@admin_requerido
def admin_resenas():
    try:
        response = requests.get(f"{BACKEND_URL}/resenas")
        data = response.json()
        resenas = data.get("resenas", [])
    except:
        resenas = []
    return render_template("admin/admin_resenas.html", resenas=resenas)

@mis_rutas.route("/admin/resenas/eliminar/<int:id>", methods=["POST"])
@admin_requerido
def eliminar_resena(id):
    try:
        token = session.get("jwt_token")
        requests.delete(f"{BACKEND_URL}/admin/resenas/{id}", headers={"Authorization": f"Bearer {token}"})
    except:
        print("Error al eliminar reseña")
    return redirect(url_for("frontend.admin_resenas"))



@mis_rutas.route('/admin/estadisticas')
@admin_requerido
def admin_stats():
    fecha_filtro = request.args.get('fecha_filtro')  
    
    try:
        parametros = {'fecha': fecha_filtro} if fecha_filtro else {}
        
        respuesta = requests.get(f"{BACKEND_URL}/admin/stats/", params=parametros)
        datos = respuesta.json()
        
    except Exception as e:
        print(f"Error de conexión con el Backend: {e}")
        datos = {}

    try:
        total_pers = int(datos.get('total_personas', 0))
    except (ValueError, TypeError):
        total_pers = 0

    return render_template('admin/admin_stats.html', 
                           total_reservas=datos.get('total_reservas', 0),
                           reservas_hoy=datos.get('reservas_hoy', 0),
                           total_personas=total_pers,
                           stats_dias=datos.get('stats_dias', {}),
                           stats_horas=datos.get('stats_horas', {}))



@mis_rutas.route('/admin/menu')
@admin_requerido
def admin_menu():
    platos = []
    plato_a_editar = None
    editar_id = request.args.get('editar_id', type=int)

    try:
        response = requests.get(f"{BACKEND_URL}/platos")
        if response.status_code == 200:
            platos = response.json().get("platos", [])
            
            if editar_id:
                for plato in platos:
                    if plato.get('id_menu') == editar_id:
                        plato_a_editar = plato
                        
    except:
        platos = []

    return render_template('admin/admin_menu.html', platos=platos, plato_a_editar=plato_a_editar)


@mis_rutas.route("/admin/menu/eliminar/<int:id>", methods=["POST"])
@admin_requerido
def eliminar_plato(id):
    token = session.get("jwt_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        requests.delete(f"{BACKEND_URL}/admin/menu/{id}", headers=headers)
    except:
         print("Error al eliminar menu")
        
        
    return redirect(url_for("frontend.admin_menu"))