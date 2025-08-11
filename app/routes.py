from flask import Blueprint, render_template
from app.db import get_db

bp = Blueprint('main', __name__)

@bp.route('/')
def start():
    conn = get_db()
    cursor = conn.cursor(dictionary=True) #Devuelve filas como diccionario
    cursor.execute("SELECT * FROM persona NATURAL JOIN telefono_persona;")  
    data = cursor.fetchall()
    cursor.close()
    return render_template('start.html', data=data)
