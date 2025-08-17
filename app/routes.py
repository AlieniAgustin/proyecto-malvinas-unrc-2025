from flask import Blueprint, render_template
from app.db import get_db

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

    cursor.close()

    return render_template('start.html',total_veteranos = total_veteranos, total_fuerzas = total_fuerzas, documentos = documentos)

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



