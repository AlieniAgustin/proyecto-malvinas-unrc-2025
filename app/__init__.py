from flask import Flask
from flask_login import LoginManager
from .db import get_db, close_db

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)

    app.config.from_mapping(
        SECRET_KEY="son-fueron-y-seran-ARGENTINAS-desde1982hastaSiempre", #Clave necesaria para flask_login
        MYSQL_HOST='db',  # coincide con el servicio mysql en docker-compose
        MYSQL_USER='root',
        MYSQL_PASSWORD='Malvinas2025!',
        MYSQL_DB='malvinas_db'
    )

    #Inicializo loginManager
    login_manager.init_app(app)
    login_manager.login_view = "main.login"
    
    # Desactivar mensaje automático de Flask-Login al requerir autenticación
    login_manager.login_message = None
    login_manager.needs_refresh_message = None

    @app.teardown_appcontext
    def teardown_db(exception):
        close_db()

    # Importar y registrar rutas
    from . import routes
    app.register_blueprint(routes.bp)

    #Importar administradores
    from .models.administrador import Administrador
    @login_manager.user_loader
    def load_admin(user_id):
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM administrador WHERE agrupacion = %s", (user_id,))
        row = cursor.fetchone()
        cursor.close()

        if (row):
            return Administrador(row["agrupacion"], row["email"], row["psswd"])
        return None
    
    # Importa las funciones del script
    from .scripts.populate_georef import populate_provincias, populate_localidades
    
    # Comando para ejecutar en la consola para poblar la base de datos con provincias y localidades obtenidas de la API Georef del gobierno
    @app.cli.command("db-populate-geo")
    def populate_geo_command():
        """Puebla la base de datos con provincias y localidades de Georef."""
        print("Iniciando comando de población geográfica...")
        db = None
        cursor = None
        try:
            db = get_db()
            cursor = db.cursor(dictionary=True)
            
            if not populate_provincias(cursor):
                raise Exception("Error al poblar provincias.")
            
            if not populate_localidades(cursor):
                raise Exception("Error al poblar localidades.")
                
            db.commit()
            print("\n¡Población de datos geográficos completada exitosamente!")
            
        except Exception as e:
            if db:
                db.rollback()
            print(f"\nError durante la población de datos: {e}")
        finally:
            if cursor:
                cursor.close()

    return app