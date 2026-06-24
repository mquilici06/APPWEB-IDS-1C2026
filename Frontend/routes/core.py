from flask import Blueprint, render_template, session, redirect, url_for, request
import requests
from routes.auth import admin_requerido, BACKEND_URL

core_bp = Blueprint('core', __name__)


@core_bp.route("/")
def index():
    return render_template("index.html")


@core_bp.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect(url_for("auth.login_admin"))


@core_bp.route("/admin")
@admin_requerido
def admin():
    return render_template("admin/admin.html")


@core_bp.route('/admin/estadisticas')
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
