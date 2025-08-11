from flask import Blueprint, render_template
from app.db import get_db

bp = Blueprint('main', __name__)

@bp.route('/')
def start():
   return render_template('start.html')
