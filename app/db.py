# db.py
import mysql.connector
from flask import current_app, g

def get_db():
    if 'db' not in g:
        g.db = mysql.connector.connect(
            host=current_app.config['MYSQL_HOST'],
            user=current_app.config['MYSQL_USER'],
            password=current_app.config['MYSQL_PASSWORD'],
            database=current_app.config['MYSQL_DB'],
            charset='utf8mb4',
            use_unicode=True
        )
        g.db.cursor().execute("SET NAMES utf8mb4;")
        g.db.cursor().execute("SET CHARACTER SET utf8mb4;")
        g.db.cursor().execute("SET character_set_connection=utf8mb4;")
        
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
