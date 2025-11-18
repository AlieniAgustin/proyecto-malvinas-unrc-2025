import requests

# URL base de la API Georef (probamos con diferentes versiones)
GEOREF_API_URLS = [
    "https://apis.datos.gob.ar/georef/api",  # Sin versión
    "https://apis.datos.gob.ar/georef/api/v2.0",
    "https://georef-ar-api.datosgobar.gob.ar/api"  # Alternativa
]

def fetch_from_api(endpoint, params=None):
    """Función auxiliar para llamar a la API de Georef."""
    # Intentar con diferentes URLs
    for base_url in GEOREF_API_URLS:
        url = f"{base_url}/{endpoint}"
        print(f"  -> Intentando API: {url}")
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"     Falló: {e}")
            continue
    
    print("Error: No se pudo conectar con ninguna versión de la API Georef")
    return None
            
def populate_provincias(cursor):
    """Puebla la tabla de provincias."""
    print("Poblando provincias...")
    params = {'campos': 'id,nombre', 'max': 24}
    data = fetch_from_api("provincias", params)
    
    if not data or 'provincias' not in data:
        print("No se recibieron datos de provincias.")
        return False
    
    provincias = data['provincias']
    
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
    cursor.execute("TRUNCATE TABLE provincia;")
    
    query = "INSERT INTO provincia (id_provincia, nombre) VALUES (%s, %s)"
    count = 0
    for prov in provincias:
        cursor.execute(query, (prov['id'], prov['nombre']))
        count += 1
            
    print(f"Se insertaron {count} provincias.")
    return True

def populate_localidades(cursor):
    """Puebla la tabla de localidades."""
    print("\nPoblando localidades (esto puede tardar)...")
    cursor.execute("TRUNCATE TABLE localidad;")
    cursor.execute("SELECT id_provincia, nombre FROM provincia;")
    provincias = cursor.fetchall()
    
    query = "INSERT INTO localidad (id_localidad, nombre_localidad, departamento, id_provincia) VALUES (%s, %s, %s, %s)"
    
    total_count = 0
    for prov in provincias:
        prov_id = prov['id_provincia']
        print(f"Procesando provincia: {prov['nombre']} (ID: {prov_id})")
        
        params = {
            "provincia": prov_id, 
            "campos": "id,nombre,departamento.nombre", 
            "max": 5000,
        }
        
        data = fetch_from_api("localidades-censales", params) 
        
        if not data or 'localidades_censales' not in data:
            print(f"  Advertencia: No se recibieron datos de localidades para la provincia {prov['nombre']}.")
            continue
        
        loc_count = 0
        for loc in data['localidades_censales']:
            departamento_nombre = loc['departamento']['nombre'] if loc.get('departamento') else None
            
            cursor.execute(query, (loc['id'], loc['nombre'], departamento_nombre, prov_id))
            loc_count += 1
            
        print(f"  -> Se insertaron {loc_count} localidades en {prov['nombre']}.")
        total_count += loc_count
            
    print(f"\nTotal de localidades insertadas: {total_count}.")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
    return True

