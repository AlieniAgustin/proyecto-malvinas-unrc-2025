from flask import Flask
from .db import get_db, close_db

def create_app():
    app = Flask(__name__)

    app.config.from_mapping(
        MYSQL_HOST='db',  # coincide con el servicio mysql en docker-compose
        MYSQL_USER='root',
        MYSQL_PASSWORD='Malvinas2025!',
        MYSQL_DB='malvinas_db'
    )

    @app.teardown_appcontext
    def teardown_db(exception):
        close_db()

    # Importar y registrar rutas
    from . import routes
    app.register_blueprint(routes.bp)
    
    return app
