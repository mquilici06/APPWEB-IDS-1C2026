from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify, flash
import requests
from routes.auth import admin_requerido, BACKEND_URL
from datetime import datetime

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
    return render_template("404.html")
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

@mis_rutas.route("/admin/reservas", methods=['GET'])
@admin_requerido
def admin_reservas():
    buscar = request.args.get('buscar', '')
    fecha = request.args.get('fecha', '')
    estado = request.args.get('estado', '')
    
    parametros = {
        'buscar': buscar,
        'fecha': fecha,
        'estado': estado
    }
    
    reservas = []
    try:
        respuesta = requests.get(f"{BACKEND_URL}/admin/reservas", params=parametros)
        
        if respuesta.status_code == 200:
            datos = respuesta.json()
            reservas = datos.get("Reservas", [])
    except Exception:
        reservas = []
        
    hoy = datetime.now().strftime('%Y-%m-%d')
    total_hoy = 0
    pendientes = 0
    confirmadas = 0
    
    for reserva in reservas:
        if reserva.get('fecha') == hoy:
            total_hoy += 1
        
        estado_reserva = reserva.get('estado', 'Pendiente').lower()
        if estado_reserva == 'pendiente':
            pendientes += 1
        elif estado_reserva == 'confirmada':
            confirmadas += 1
            
    indicadores = {
        'total_hoy': total_hoy,
        'pendientes': pendientes,
        'confirmadas': confirmadas
    }
    
    return render_template(
        '/admin/admin_reservas.html',
        reservas=reservas,
        indicadores=indicadores,
        filtro_buscar=buscar,
        filtro_fecha=fecha,
        filtro_estado=estado
    )
        

@mis_rutas.route("/admin/resenas", methods=["GET"])
@admin_requerido
def admin_resenas():
    try:
        response = requests.get(f"{BACKEND_URL}/resenas/todas") 
        data = response.json()
        resenas = data.get("resenas", [])
    except:
        resenas = []
    return render_template("admin/admin_resenas.html", resenas=resenas)

@mis_rutas.route("/admin/resenas/eliminar/<int:id>", methods=["POST"])
@admin_requerido
def eliminar_resena(id):
    token = session.get("jwt_token")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.delete(f"{BACKEND_URL}/resenas/{id}", headers=headers, timeout=5)
        
        if response.status_code != 200:
            flash("Error al eliminar la reseña", "error")
        else:
            flash("Reseña eliminada correctamente", "exito")
            
    except requests.exceptions.RequestException:
        print("Error al eliminar reseña")
        flash("Error de conexión con el servidor", "error")
    return redirect(url_for("frontend.admin_resenas"))


@mis_rutas.route('/admin/menu', methods=['GET', 'POST'])
@admin_requerido
def admin_menu():
    if request.method == 'POST':
        token = session.get("jwt_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        datos_plato = {
            "nombre": request.form.get("nombre_plato"),
            "descripcion": request.form.get("desc_plato"),
            "precio": request.form.get("precio"),
            "seccion": request.form.get("seccion"),
            "restricciones": request.form.get("restricciones")
        }

       
        archivo = request.files.get("imagen_plato")
        files = {}
        if archivo and archivo.filename != '':

            files = {'imagen_plato': (archivo.filename, archivo.read(), archivo.content_type)}
    
        actualizar_id = request.args.get('actualizar_id', type=int)

        try:
            if actualizar_id:
                respuesta = requests.put(f"{BACKEND_URL}/platos/{actualizar_id}", data=datos_plato, files=files, headers=headers, timeout=10)
                mensaje_ok = "Plato actualizado correctamente"
            else:
                respuesta = requests.post(f"{BACKEND_URL}/platos", data=datos_plato, files=files, headers=headers, timeout=10)
                mensaje_ok = "Plato guardado correctamente"
            
            if respuesta.status_code in [200, 201]:
                flash(mensaje_ok, "exito")
            else:
                flash(f"Error al procesar: {respuesta.text}", "error")
        except requests.exceptions.RequestException:
            flash("Error de conexión con el Backend", "error")
            
        return redirect(url_for('frontend.admin_menu'))

    
    try:
        response = requests.get(f"{BACKEND_URL}/platos")
        platos = response.json().get("platos", [])
    except:
        platos = []

    editar_id = request.args.get('editar_id', type=int)
    plato_a_editar = None
    if editar_id:
        plato_a_editar = next((p for p in platos if p['id_menu'] == editar_id), None)
    
    
    
    return render_template('admin/admin_menu.html', platos=platos, plato_a_editar=plato_a_editar)

@mis_rutas.route("/admin/menu/eliminar/<int:id>", methods=["POST"])
@admin_requerido
def eliminar_plato(id):
    token = session.get("jwt_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.delete(f"{BACKEND_URL}/platos/{id}", headers=headers, timeout=5)
        
        if response.status_code == 200:
            flash("Plato eliminado correctamente", "exito")
        else:
            flash("Error al eliminar el plato", "error")
            
    except requests.exceptions.RequestException:
        flash("Error de conexión con el servidor al intentar eliminar", "error")
        
    return redirect(url_for("frontend.admin_menu"))



@mis_rutas.route("/admin/resenas/<int:id>/estado", methods=["POST"])
@admin_requerido
def cambiar_estado_resena(id):
    nuevo_estado = request.form.get("estado")
    
    try:
        requests.put(
            f"{BACKEND_URL}/resenas/{id}/estado", 
            json={"estado": nuevo_estado},
            timeout=10
        )
    except requests.exceptions.RequestException:
        flash("Error al conectar con el servidor para cambiar estado", "error")
        
    return redirect(url_for('frontend.admin_resenas'))

    

@mis_rutas.route('/admin/estadisticas')
@admin_requerido
def admin_stats():
    fecha_filtro = request.args.get('fecha_filtro')  
    
    token = session.get("jwt_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        parametros = {'fecha': fecha_filtro} if fecha_filtro else {}
        respuesta = requests.get(f"{BACKEND_URL}/admin/stats", params=parametros, headers=headers, timeout=5)
        datos = respuesta.json()
        
    except requests.exceptions.RequestException:
        print("Error de conexión con el Backend al cargar estadísticas")
        datos = {}
    except ValueError:
        print("Error al decodificar el JSON de las estadísticas")
        datos = {}

    dias_ingles = datos.get('stats_dias', {})
    stats_dias_castellano = {}
    DIAS_TRADUCCION = {
        'Monday': 'Lunes',
        'Tuesday': 'Martes',
        'Wednesday': 'Miércoles',
        'Thursday': 'Jueves',
        'Friday': 'Viernes',
        'Saturday': 'Sábado',
        'Sunday': 'Domingo'
    }
    
    for dia_en, valor in dias_ingles.items():
        dia_es = DIAS_TRADUCCION.get(dia_en, dia_en)
        stats_dias_castellano[dia_es] = valor

    try:
        total_pers = int(datos.get('total_personas', 0))
    except (ValueError, TypeError):
        total_pers = 0

    return render_template('admin/admin_stats.html', 
                           total_reservas=datos.get('total_reservas', 0),
                           reservas_hoy=datos.get('reservas_hoy', 0),
                           total_personas=total_pers,
                           stats_dias=stats_dias_castellano,  
                           stats_horas=datos.get('stats_horas', {}))