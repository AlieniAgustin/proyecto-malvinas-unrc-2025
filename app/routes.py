from flask import Blueprint, render_template, request, redirect, url_for, flash
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

    cursor.execute("SELECT nombre, descripcion, ruta_archivo FROM documento")
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
    query = """
        SELECT 
           *
           
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

 # Filtros restringidos a administradore
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
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, params)
    resultados = cursor.fetchall()
    conn.close()

    return render_template('buscar.html')

@bp.route('/admin')
@login_required
def admin():
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
    return render_template('contacto.html')

@bp.route('/terminos')
def terminos():
    return render_template('terminos.html')

@bp.route('/privacidad')
def privacidad():
    return render_template('privacidad.html')

@bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


