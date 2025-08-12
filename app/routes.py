from flask import Blueprint, render_template
from app.db import get_db

bp = Blueprint('main', __name__)

@bp.route('/')
def start():
    return render_template('start.html')

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



