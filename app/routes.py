from flask import Blueprint, render_template
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
    return render_template('buscar.html')

@bp.route('/admin')
def admin():
    return render_template('admin.html')

@bp.route('/contacto')
def contacto():
    return render_template('contacto.html')

@bp.route('/terminos')
def terminos():
    return render_template('terminos.html')

@bp.route('/privacidad')
def privacidad():
    return render_template('privacidad.html')



