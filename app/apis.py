from flask import request, jsonify
from flask_login import login_required
from app.db import get_db
from .routes import bp 

# API para buscar códigos postales por localidad (Select2)
@bp.route('/api/codigos_postales')
def buscar_codigos_postales():
    localidad_id = request.args.get('localidad_id')
    query = request.args.get('q', '').strip()

    if not localidad_id:
        return jsonify({"items": []})

    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        # Buscar códigos postales asociados a la localidad
        sql_query = """
            SELECT DISTINCT codigo_postal_residencia as codigo_postal
            FROM veterano
            WHERE localidad_residencia = %s 
              AND codigo_postal_residencia IS NOT NULL
              AND codigo_postal_residencia LIKE %s
            ORDER BY codigo_postal_residencia
        """
        cursor.execute(sql_query, (localidad_id, f"%{query}%"))
        codigos = cursor.fetchall()
    except Exception as e:
        print(f"Error en buscar_codigos_postales: {e}")
        codigos = []
    finally:
        cursor.close()

    resultados = [
        {"id": c['codigo_postal'], "text": c['codigo_postal']}
        for c in codigos
    ]

    # Agregar "Otro" al final
    resultados.append({"id": "otro", "text": "Otro"})
    print(f"[API] /api/codigos_postales localidad_id={localidad_id!r} q={query!r} -> {len(resultados)} items")
    return jsonify({"items": resultados})


# API para obtener departamentos por provincia
@bp.route('/api/localidades/<int:provincia_id>')
def get_localidades(provincia_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT DISTINCT departamento 
        FROM localidad 
        WHERE id_provincia = %s AND departamento IS NOT NULL
        ORDER BY departamento
    """, (provincia_id,))
    departamentos = cursor.fetchall()
    cursor.close()
    return jsonify([d['departamento'] for d in departamentos])


# API para obtener localidades por departamento y provincia
@bp.route('/api/localidades/<int:provincia_id>/<string:departamento>')
def get_localidades_por_depto(provincia_id, departamento):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT id_localidad, nombre_localidad
        FROM localidad 
        WHERE id_provincia = %s AND departamento = %s
        ORDER BY nombre_localidad
    """, (provincia_id, departamento))
    localidades = cursor.fetchall()
    cursor.close()
    return jsonify(localidades)

# API para Select2. Busca localidades por nombre dentro de una provincia. Recibe provincia_id y q (query)
@bp.route('/api/localidades/buscar')
def buscar_localidades_api():
    provincia_id = request.args.get('provincia_id')
    query = request.args.get('q', '').strip()

    # Si no hay provincia, no devolver nada
    if not provincia_id:
        return jsonify({"items": []}) # Select2 espera un objeto con 'items'

    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    # Buscamos coincidencias con LIKE
    sql_query = """
        SELECT id_localidad, nombre_localidad, departamento 
        FROM localidad 
        WHERE id_provincia = %s AND nombre_localidad LIKE %s
        ORDER BY nombre_localidad
    """
    params = (provincia_id, f"%{query}%")
    
    try:
        cursor.execute(sql_query, params)
        localidades = cursor.fetchall()
    except Exception as e:
        print(f"Error en buscar_localidades_api: {e}")
        localidades = []
    finally:
        cursor.close()

    # Formateamos la respuesta para Select2
    # Select2 necesita { id: 'valor', text: 'Etiqueta' }
    resultados = [
        {"id": loc['id_localidad'], "text": f"{loc['nombre_localidad']} ({loc['departamento']})"}
        for loc in localidades
    ]
    return jsonify({"items": resultados})


# API para obtener una localidad por su ID (para Select2 inicial)
@bp.route('/api/localidad/<string:localidad_id>')
def get_localidad_por_id(localidad_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute(
            "SELECT id_localidad, nombre_localidad, departamento FROM localidad WHERE id_localidad = %s", 
            (localidad_id,)
        )
        loc = cursor.fetchone()
    except Exception as e:
        print(f"Error en get_localidad_por_id: {e}")
        loc = None
    finally:
        cursor.close()
    
    if not loc:
        return jsonify({"error": "No encontrado"}), 404
        
    # Formato para Select2
    resultado = {
        "id": loc['id_localidad'],
        "text": f"{loc['nombre_localidad']} ({loc['departamento']})"
    }
    return jsonify(resultado)

# Api para buscar veteranos por nombre o dni
@bp.route('/api/veteranos/buscar')
def buscar_veteranos_api():
    query = request.args.get('q', '').strip()
    
    # Prevenir búsqueda vacía si se desea
    if not query:
        return jsonify({"items": []})

    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    # Buscamos por DNI, nombre o apellido solo de veteranos de la agrupación 1
    sql_query = """
        SELECT p.dni, p.nombre, p.apellido 
        FROM persona p
        JOIN veterano v ON p.dni = v.dni_veterano
        WHERE v.id_agrupacion = 1
          AND (p.dni LIKE %s 
           OR p.nombre LIKE %s 
           OR p.apellido LIKE %s)
        ORDER BY p.apellido, p.nombre
    """
    like_query = f"%{query}%"
    params = (like_query, like_query, like_query)
    
    try:
        cursor.execute(sql_query, params)
        veteranos = cursor.fetchall()
    except Exception as e:
        print(f"Error en buscar_veteranos_api: {e}")
        veteranos = []
    finally:
        cursor.close()

    # Formateamos la respuesta para Select2
    # El JS espera { dni: '...', nombre: '...', apellido: '...' }
    resultados = [
        {
            "dni": v['dni'], 
            "nombre": v['nombre'],
            "apellido": v['apellido']
        }
        for v in veteranos
    ]
    return jsonify({"items": resultados})