from flask import Blueprint, render_template
from app.db import get_db

bp = Blueprint('main', __name__)

@bp.route('/')
def start():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT NOW();")  # Consulta simple para probar
    current_time = cursor.fetchone()[0]
    cursor.close()
    return render_template('start.html', current_time=current_time)
