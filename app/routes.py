from collections import defaultdict
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from .models.administrador import Administrador
from werkzeug.security import check_password_hash
from app.db import get_db
from datetime import date

bp = Blueprint('main', __name__)

@bp.route('/')
def start():
    db = get_db()
    cursor = db.cursor(dictionary = True) # para que fetch devuelva diccionarios

    cursor.execute("SELECT COUNT(dni_veterano) AS total_veteranos FROM veterano")
    total_veteranos = cursor.fetchone()['total_veteranos']

    cursor.execute("SELECT COUNT(id_fuerza) AS total_fuerzas FROM fuerza")
    total_fuerzas = cursor.fetchone()['total_fuerzas']

    cursor.execute("SELECT nombre, descripcion, ruta_archivo FROM documento ORDER BY id_documento DESC")
    documentos = cursor.fetchall()

    inicio_guerra = date(1982,4,2)
    hoy = date.today()
    anos_historia = hoy.year - inicio_guerra.year
    if (hoy.month, hoy.day) < (inicio_guerra.month, inicio_guerra.day):
        anos_historia -= 1

    cursor.close()

    return render_template('start.html',total_veteranos = total_veteranos, total_fuerzas = total_fuerzas, documentos = documentos, anos_historia = anos_historia)

@bp.route('/buscar')
def buscar():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id_provincia, nombre FROM provincia ORDER BY nombre ASC")
    provincias = cursor.fetchall()

    cursor.execute("SELECT id_fuerza, nombre FROM fuerza ORDER BY nombre ASC")
    fuerzas = cursor.fetchall()

    query = """
        SELECT 
            p.dni,
            p.apellido,
            p.nombre,
            fza.nombre AS fuerza
        FROM persona p
        JOIN veterano v ON p.dni = v.dni_veterano
        LEFT JOIN fuerza fza ON v.id_fuerza = fza.id_fuerza
        LEFT JOIN localidad loc ON v.localidad_nacimiento = loc.id_localidad
        LEFT JOIN provincia prov ON loc.id_provincia = prov.id_provincia
        LEFT JOIN fallecido fal ON v.dni_veterano = fal.dni_veterano
        LEFT JOIN localidad loc_res ON v.localidad_residencia = loc_res.id_localidad
        WHERE 1=1
    """

    params = []

    # Filtros
    apellido = request.args.get("apellido", "")
    nombre = request.args.get("nombre", "")
    provincia_nacimiento_id = request.args.get("provincia_nacimiento", "")
    departamento_nacimiento_id = request.args.get("departamento_nacimiento", "")
    localidad_nacimiento_id = request.args.get("localidad_nacimiento", "")
    fuerza_id = request.args.get("fuerza", "")
    vf = request.args.get("vf", "") # 1 Vivo - 0 Fallecido

    if apellido:
        query += " AND LOWER(p.apellido) LIKE %s"
        params.append("%" + apellido.lower() + "%")

    if nombre:
        query += " AND LOWER(p.nombre) LIKE %s"
        params.append("%" + nombre.lower() + "%")

    if departamento_nacimiento_id:
        query += " AND LOWER(loc.departamento) LIKE %s"
        params.append("%" + departamento_nacimiento_id.lower() + "%")

    if provincia_nacimiento_id:
        query += " AND loc.id_provincia = %s"
        params.append(provincia_nacimiento_id)

    if localidad_nacimiento_id:
        query += " AND loc.id_localidad = %s"
        params.append(localidad_nacimiento_id)

    if fuerza_id:
        query += " AND v.id_fuerza= %s"
        params.append(fuerza_id)
    
    if vf:
        if vf in ["0", "fallecido"]:
            query += " AND fal.dni_veterano IS NOT NULL" 
        elif vf in ["1", "vivo"]:
            query += " AND fal.dni_veterano IS NULL"       

    # Filtros restringidos a administradores
    if current_user.is_authenticated:
        dni = request.args.get("dni", "")
        provincia_residencia_id = request.args.get("provincia_residencia", "")
        localidad_residencia_id = request.args.get("localidad_residencia", "")
        departamento_residencia = request.args.get("departamento_residencia", "")
        mes_cumple = request.args.get("mes_cumple", "")
        datos_incompletos = request.args.get("incompletos", "")

        if dni:
            query += " AND p.dni = %s"
            params.append(dni)

        if provincia_residencia_id:
            query += " AND loc_res.id_provincia = %s"
            params.append(provincia_residencia_id)

        if departamento_residencia:
            query += " AND LOWER(loc_res.departamento) = %s"
            params.append(departamento_residencia.lower())

        if localidad_residencia_id:
            query += " AND v.localidad_residencia = %s"
            params.append(localidad_residencia_id)

        if mes_cumple:
            query += " AND MONTH(v.fecha_nacimiento) = %s"
            params.append(mes_cumple)

        if datos_incompletos:
            query += """ 
                AND (
                    p.apellido IS NULL OR
                    p.nombre IS NULL OR
                    v.id_fuerza IS NULL OR
                    v.fecha_nacimiento IS NULL
                )
            """

    query += " ORDER BY p.apellido ASC, p.nombre ASC"
    cursor.execute(query, tuple(params))
    resultados = cursor.fetchall()
    conn.close()

    is_admin_view = current_user.is_authenticated

    return render_template('buscar.html',
                           resultados=resultados,
                           provincias=provincias,
                           fuerzas=fuerzas,
                           is_admin_view=is_admin_view)

@bp.route('/persona/<string:dni>')
def ver_perfil(dni):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    query_publica = """
        SELECT
            p.nombre, p.apellido,
            v.fecha_nacimiento,
            fza.nombre AS fuerza,
            loc.nombre_localidad, loc.departamento,
            prov.nombre AS provincia_nacimiento,
            fallecido.fecha_fallecimiento
        FROM persona p
        JOIN veterano v ON p.dni = v.dni_veterano
        LEFT JOIN fuerza fza ON v.id_fuerza = fza.id_fuerza
        LEFT JOIN localidad loc ON v.localidad_nacimiento = loc.id_localidad
        LEFT JOIN provincia prov ON loc.id_provincia = prov.id_provincia
        LEFT JOIN fallecido ON v.dni_veterano = fallecido.dni_veterano
        WHERE p.dni = %s
    """
    cursor.execute(query_publica, (dni,))
    veterano = cursor.fetchone()

    if not veterano:
        # Render the perfil page with no veterano so the site layout is preserved
        # and return a 404 status code so clients know it's not found.
        cursor.close()
        return render_template('perfil.html', veterano=None, veterano_admin=None, telefonos=None), 404

    # Variables para los datos de administrador
    veterano_admin = None
    telefonos = None

    # Si el usuario es admin, buscar todos los datos adicionales
    if current_user.is_authenticated:
        query_admin = """
            SELECT
                v.direccion, v.nro_beneficio_nacional, v.funcion, v.secuelas, v.mail,
                loc_res.nombre_localidad AS localidad_residencia,
                prov_res.nombre AS provincia_residencia,
                g.nombre AS grado,
                causa.descripcion AS causa_fallecimiento
            FROM veterano v
            LEFT JOIN localidad loc_res ON v.localidad_residencia = loc_res.id_localidad
            LEFT JOIN provincia prov_res ON loc_res.id_provincia = prov_res.id_provincia
            LEFT JOIN grado g ON v.id_grado = g.id_grado
            LEFT JOIN fallecido f ON v.dni_veterano = f.dni_veterano
            LEFT JOIN causa_fallecimiento causa ON f.id_causa = causa.id_causa
            WHERE v.dni_veterano = %s
        """
        cursor.execute(query_admin, (dni,))
        veterano_admin = cursor.fetchone()

        # Consulta separada para los teléfonos (puede haber más de uno)
        cursor.execute("SELECT telefono FROM telefono_persona WHERE dni = %s", (dni,))
        telefonos = cursor.fetchall()

    edad = None
    if veterano and veterano['fecha_nacimiento'] and not veterano['fecha_fallecimiento']:
        hoy = date.today()
        nac = veterano['fecha_nacimiento']
        edad = hoy.year - nac.year - ((hoy.month, hoy.day) < (nac.month, nac.day))

    cursor.close()

    return render_template('perfil.html',
                           veterano=veterano,
                           veterano_admin=veterano_admin,
                           telefonos=telefonos,
                           edad=edad)

@bp.route('/admin')
@login_required
def admin():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    return render_template('admin.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Ingresá email y contraseña.", "warning")
            return redirect(url_for("main.login"))

        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT agrupacion, email, psswd FROM administrador WHERE email = %s", (email,))
        row = cursor.fetchone()
        cursor.close()

        if row and (row["psswd"] == password or check_password_hash(row["psswd"], password)):
            user = Administrador(row["agrupacion"], row["email"], row["psswd"])
            login_user(user)
            return redirect(url_for("main.dashboard"))
        else:
            flash("Usuario o contraseña incorrectos", "danger")
            return redirect(url_for("main.login"))

    return render_template("admin.html")

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.start"))

@bp.route('/contacto')
def contacto():

    db = get_db()
    cursor = db.cursor(dictionary = True) # para que fetch devuelva diccionarios

    cursor.execute("SELECT nombre_agrupacion, direccion, mail FROM agrupacion WHERE id_agrupacion = 1")
    agrupacion = cursor.fetchone()

    cursor.execute("SELECT telefono FROM telefono_agrupacion WHERE id_agrupacion = 1")
    telefonos = cursor.fetchall()

    cursor.execute("SELECT nombre, link FROM red_social WHERE id_agrupacion = 1")
    redes = cursor.fetchall()

    cursor.execute("""
            SELECT r.nombre_rol, p.apellido, p.nombre 
            FROM autoridad a
            JOIN rol r ON a.id_rol = r.id_rol
            JOIN persona p ON a.dni_autoridad = p.dni
            JOIN veterano v ON a.dni_autoridad = v.dni_veterano 
            WHERE v.id_agrupacion = 1
        """)
    autoridades_lista = cursor.fetchall()

    autoridades_agrupadas = defaultdict(list)
    for autoridad in autoridades_lista:
        nombre_completo = f"{autoridad['apellido']}, {autoridad['nombre']}"
        autoridades_agrupadas[autoridad['nombre_rol']].append(nombre_completo)

    cursor.execute("""
            SELECT l.nombre_localidad, p.nombre AS provincia
            FROM agrupacion ag
            JOIN localidad l ON ag.localidad_agrupacion = l.id_localidad
            JOIN provincia p ON l.id_provincia = p.id_provincia
            WHERE ag.id_agrupacion = 1
        """)
    ubicacion = cursor.fetchone()

    cursor.close()

    return render_template('contacto.html',
        agrupacion=agrupacion,
        telefonos=telefonos,
        redes=redes,
        ubicacion=ubicacion,
        autoridades_agrupadas=autoridades_agrupadas)

@bp.route('/terminos-privacidad')
def terminos_privacidad():
    return render_template('terminos_privacidad.html')

@bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@bp.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Importar otros modulos
from . import apis
from . import veteranos_admin
from . import gestion_documentos
from . import gestion_agrupacion
