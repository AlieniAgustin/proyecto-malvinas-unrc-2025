from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.db import get_db
from .routes import bp

# API para obtener departamentos por provincia
@bp.route('/api/localidades/<int:provincia_id>')
@login_required
def get_localidades(provincia_id):
    from flask import jsonify
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
@login_required
def get_localidades_por_depto(provincia_id, departamento):
    from flask import jsonify
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT id_localidad, nombre_localidad, codigo_postal
        FROM localidad 
        WHERE id_provincia = %s AND departamento = %s
        ORDER BY nombre_localidad
    """, (provincia_id, departamento))
    localidades = cursor.fetchall()
    cursor.close()
    return jsonify(localidades)


# Obtiene las listas para los dropdowns de los formularios de inserción/modificación de personas
def _get_form_context_data(cursor):
    cursor.execute("SELECT id_provincia, nombre FROM provincia ORDER BY nombre")
    provincias = cursor.fetchall()
    cursor.execute("SELECT id_fuerza, nombre FROM fuerza ORDER BY nombre")
    fuerzas = cursor.fetchall()
    cursor.execute("SELECT id_grado, nombre, id_fuerza FROM grado ORDER BY nombre")
    grados = cursor.fetchall()
    cursor.execute("SELECT id_causa, descripcion FROM causa_fallecimiento")
    causas = cursor.fetchall()
    
    # Devuelve un diccionario listo para pasar al template
    return {
        "provincias": provincias,
        "fuerzas": fuerzas,
        "grados": grados,
        "causas": causas
    }
    
    
# Función auxiliar para obtener o crear un grado
def _get_or_create_grado(cursor, id_fuerza, id_grado_form, otro_grado_str):
    if id_grado_form != 'otro':
        return id_grado_form or None

    if not id_fuerza or not otro_grado_str:
        raise Exception("Si selecciona 'Otro' grado, debe completarlo y seleccionar una fuerza.")
    
    cursor.execute(
        "SELECT id_grado FROM grado WHERE id_fuerza = %s AND nombre = %s",
        (id_fuerza, otro_grado_str)
    )
    existente = cursor.fetchone()
    if existente:
        return existente['id_grado']
    
    cursor.execute(
        "INSERT INTO grado (nombre, id_fuerza) VALUES (%s, %s)", 
        (otro_grado_str, id_fuerza)
    )
    return cursor.lastrowid


# Función auxiliar para obtener o crear una localidad
def _get_or_create_localidad(cursor, id_provincia, depto_form_val, otro_depto_str, loc_id_form_val, otra_loc_str, cp_str=None):
    if not id_provincia:
        return None

    if loc_id_form_val and loc_id_form_val != 'otra':
        return loc_id_form_val
    
    if depto_form_val == 'otro':
        departamento_final = otro_depto_str
    else:
        departamento_final = depto_form_val
    
    localidad_final = otra_loc_str
    
    if not departamento_final or not localidad_final:
        raise Exception(f"Al crear una nueva localidad/departamento, debe completar ambos campos de texto (Depto: '{departamento_final}', Loc: '{localidad_final}').")
    
    cursor.execute(
        "SELECT id_localidad FROM localidad WHERE id_provincia = %s AND departamento = %s AND nombre_localidad = %s",
        (id_provincia, departamento_final, localidad_final)
    )
    existente = cursor.fetchone()
    if existente:
        return existente['id_localidad']

    cursor.execute(
        "INSERT INTO localidad (nombre_localidad, departamento, id_provincia, codigo_postal) VALUES (%s, %s, %s, %s)",
        (localidad_final, departamento_final, id_provincia, cp_str or None) # cp_str solo se usa para residencia
    )
    return cursor.lastrowid

# ------------------------------------- INSERTAR VETERANO ------------------------------------- #

@bp.route('/admin/insertar', methods=['GET', 'POST'])
@login_required
def insertar_persona():
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    form_context_data = _get_form_context_data(cursor)
    
    if request.method == 'POST':
        try:
            # Obtengo los datos del formulario
            dni = request.form.get('dni', '').strip()
            nombre = request.form.get('nombre', '').strip()
            apellido = request.form.get('apellido', '').strip()
            genero = request.form.get('genero', 'no especificado')
            fecha_nacimiento = request.form.get('fecha_nacimiento')
            
            provincia_nac = request.form.get('provincia_nacimiento')
            depto_nac = request.form.get('departamento_nacimiento')
            localidad_nac_id = request.form.get('localidad_nacimiento')
            otro_departamento_nac = request.form.get('otro_departamento_nacimiento', '').strip()
            otra_localidad_nac = request.form.get('otra_localidad_nacimiento', '').strip()

            provincia_res = request.form.get('provincia_residencia')
            depto_res = request.form.get('departamento_residencia')
            localidad_res_id = request.form.get('localidad_residencia')
            otro_departamento_res = request.form.get('otro_departamento_residencia', '').strip()
            otra_localidad_res = request.form.get('otra_localidad_residencia', '').strip()
            codigo_postal_form = request.form.get('codigo_postal', '').strip()
            
            direccion = request.form.get('direccion', '').strip()
            mail = request.form.get('mail', '').strip()
            telefono = request.form.get('telefono', '').strip()
            
            id_fuerza = request.form.get('fuerza')
            id_grado_form = request.form.get('grado')
            otro_grado = request.form.get('otro_grado', '').strip()
            funcion = request.form.get('funcion', '').strip()
            secuelas = request.form.get('secuelas', '').strip()
            nro_beneficio = request.form.get('nro_beneficio_nacional', '').strip()

            estado_vida = request.form.get('estado_vida', 'vivo')
            fecha_fallecimiento = request.form.get('fecha_fallecimiento')
            id_causa = request.form.get('causa_fallecimiento')
            
            # Verifico que se hayan ingresado los datos obligatorios
            if not dni or not nombre or not apellido or not fecha_nacimiento or not id_fuerza:
                flash("DNI, nombre, apellido, fecha de nacimiento y fuerza son obligatorios", "danger")
                return render_template('admin/insertar.html', **form_context_data)

            # Validaciones sobre los datos ingresados
            cursor.execute("SELECT dni FROM persona WHERE dni = %s", (dni,))
            if cursor.fetchone():
                flash("Ya existe un veterano con ese DNI", "danger")
                return redirect(url_for('main.insertar_persona'))
            
            if estado_vida == 'fallecido' and not fecha_fallecimiento:
                flash("Debe ingresar la fecha de fallecimiento", "danger")
                return redirect(url_for('main.insertar_persona'))

            # Para grados y localidades, manejo la creación si es necesario
            id_grado_final = _get_or_create_grado(cursor, 
                                                  id_fuerza, 
                                                  id_grado_form, 
                                                  otro_grado)
            
            id_localidad_nac_final = _get_or_create_localidad(cursor, 
                                                              provincia_nac, 
                                                              depto_nac, 
                                                              otro_departamento_nac,
                                                              localidad_nac_id, 
                                                              otra_localidad_nac)
            
            id_localidad_res_final = _get_or_create_localidad(cursor,
                                                              provincia_res, 
                                                              depto_res, 
                                                              otro_departamento_res,
                                                              localidad_res_id, 
                                                              otra_localidad_res,
                                                              codigo_postal_form)
            
            # Inserto los datos en las tablas correspondientes
            cursor.execute(
                "INSERT INTO persona (dni, nombre, apellido, genero) VALUES (%s, %s, %s, %s)",
                (dni, nombre, apellido, genero)
            )
            
            cursor.execute("""
                INSERT INTO veterano (
                    dni_veterano, fecha_nacimiento, localidad_nacimiento, localidad_residencia,
                    direccion, mail, id_fuerza, id_grado, funcion, secuelas, nro_beneficio_nacional
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                dni, 
                fecha_nacimiento,
                id_localidad_nac_final,
                id_localidad_res_final,
                direccion or None,
                mail or None,
                id_fuerza or None,
                id_grado_final,
                funcion or None,
                secuelas or None,
                nro_beneficio or None
            ))
            
            if telefono:
                cursor.execute(
                    "INSERT INTO telefono_persona (dni, telefono) VALUES (%s, %s)", 
                    (dni, telefono)
                )
                
            if estado_vida == 'fallecido':
                cursor.execute(
                    "INSERT INTO fallecido (dni_veterano, fecha_fallecimiento, id_causa) VALUES (%s, %s, %s)",
                    (dni, fecha_fallecimiento, id_causa or None)
                )
                
            conn.commit()
            flash(f"Veterano {nombre} {apellido} insertado correctamente", "success")
            return redirect(url_for('main.insertar_persona'))
        
        except Exception as e:
            conn.rollback()
            flash(f"Error al insertar el veterano: {str(e)}", "danger")
            print(f"Error en insertar_persona [POST]: {e}")
            return redirect(url_for('main.insertar_persona'))
        
        finally:
            cursor.close()
    
    if request.method == 'GET':
             cursor.close()
             return render_template('admin/insertar.html', **form_context_data)


# ------------------------------------- MODIFICAR VETERANO ------------------------------------- #

@bp.route('/admin/modificar', methods=['GET'])
@login_required
def modificar_datos():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Query base
        query = """
            SELECT 
                p.dni,
                p.nombre,
                p.apellido,
                foto.ruta_foto
            FROM persona p
            JOIN veterano v ON p.dni = v.dni_veterano
            LEFT JOIN foto ON v.dni_veterano = foto.dni_veterano
            WHERE 1=1
        """
        
        params = []
        
        dni = request.args.get("dni", "").strip()
        nombre = request.args.get("nombre", "").strip()
        apellido = request.args.get("apellido", "").strip()
        
        # Aplicar filtros
        if dni:
            query += " AND p.dni = %s"
            params.append(dni)
        
        if nombre:
            query += " AND LOWER(p.nombre) LIKE %s"
            params.append("%" + nombre.lower() + "%")
        
        if apellido:
            query += " AND LOWER(p.apellido) LIKE %s"
            params.append("%" + apellido.lower() + "%")
        
        query += " ORDER BY p.apellido, p.nombre"
        
        cursor.execute(query, tuple(params))
        veteranos = cursor.fetchall()
        
        return render_template('admin/modificar.html', veteranos=veteranos)
    
    finally:
        cursor.close()

@bp.route('/admin/modificar/<string:dni>', methods=['GET'])
@login_required
def modificar_persona_form(dni):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Obtener datos completos del veterano
        query = """
            SELECT 
                p.dni, p.nombre, p.apellido, p.genero,
                v.fecha_nacimiento, v.direccion, v.mail, v.funcion, v.secuelas,
                v.nro_beneficio_nacional, v.id_fuerza, v.id_grado,
                v.localidad_nacimiento, v.localidad_residencia,
                loc_nac.id_provincia as provincia_nacimiento,
                loc_nac.departamento as departamento_nacimiento,
                loc_res.id_provincia as provincia_residencia,
                loc_res.departamento as departamento_residencia,
                f.dni_veterano as es_fallecido,
                f.fecha_fallecimiento,
                f.id_causa
            FROM persona p
            JOIN veterano v ON p.dni = v.dni_veterano
            LEFT JOIN localidad loc_nac ON v.localidad_nacimiento = loc_nac.id_localidad
            LEFT JOIN localidad loc_res ON v.localidad_residencia = loc_res.id_localidad
            LEFT JOIN fallecido f ON v.dni_veterano = f.dni_veterano
            WHERE p.dni = %s
        """
        cursor.execute(query, (dni,))
        veterano = cursor.fetchone()
        
        if not veterano:
            flash("Veterano no encontrado", "danger")
            return redirect(url_for('main.modificar_datos'))
        
        # Obtener teléfonos
        cursor.execute("SELECT telefono FROM telefono_persona WHERE dni = %s", (dni,))
        telefono = cursor.fetchone()

        form_context_data = _get_form_context_data(cursor)    
        
        return render_template('admin/modificar_veterano.html',
                                veterano=veterano,
                                telefono=telefono,
                                **form_context_data)
    finally:
        cursor.close()
        
@bp.route('/admin/modificar/<string:dni>', methods=['POST'])
@login_required
def modificar_persona_guardar(dni):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Obtener datos del formulario
        nombre = request.form.get('nombre', '').strip()
        apellido = request.form.get('apellido', '').strip()
        genero = request.form.get('genero', 'no especificado')
        fecha_nacimiento = request.form.get('fecha_nacimiento')
        
        provincia_nac = request.form.get('provincia_nacimiento')
        depto_nac = request.form.get('departamento_nacimiento')
        localidad_nac_id = request.form.get('localidad_nacimiento')
        otro_departamento_nac = request.form.get('otro_departamento_nacimiento', '').strip()
        otra_localidad_nac = request.form.get('otra_localidad_nacimiento', '').strip()

        provincia_res = request.form.get('provincia_residencia')
        depto_res = request.form.get('departamento_residencia')
        localidad_res_id = request.form.get('localidad_residencia')
        otro_departamento_res = request.form.get('otro_departamento_residencia', '').strip()
        otra_localidad_res = request.form.get('otra_localidad_residencia', '').strip()
        codigo_postal_form = request.form.get('codigo_postal', '').strip()
        
        direccion = request.form.get('direccion', '').strip()
        mail = request.form.get('mail', '').strip()
        telefono = request.form.get('telefono', '').strip()
        
        id_fuerza = request.form.get('fuerza')
        id_grado_form = request.form.get('grado')
        otro_grado = request.form.get('otro_grado', '').strip()
        funcion = request.form.get('funcion', '').strip()
        secuelas = request.form.get('secuelas', '').strip()
        nro_beneficio = request.form.get('nro_beneficio_nacional', '').strip()

        estado_vida = request.form.get('estado_vida', 'vivo')
        fecha_fallecimiento = request.form.get('fecha_fallecimiento')
        id_causa = request.form.get('causa_fallecimiento')  
              
        # Validaciones
        if not nombre or not apellido or not fecha_nacimiento or not id_fuerza:
            flash("Nombre, apellido, fecha de nacimiento y fuerza son obligatorios", "danger")
            return redirect(url_for('main.modificar_persona_form', dni=dni))
        
        if estado_vida == 'fallecido' and not fecha_fallecimiento:
            flash("Debe ingresar la fecha de fallecimiento", "danger")
            return redirect(url_for('main.modificar_persona_form', dni=dni))
        
        id_grado_final = _get_or_create_grado(cursor, 
                                              id_fuerza, 
                                              id_grado_form, 
                                              otro_grado)
        
        id_localidad_nac_final = _get_or_create_localidad(cursor, 
                                                          provincia_nac, 
                                                          depto_nac, 
                                                          otro_departamento_nac,
                                                          localidad_nac_id, 
                                                          otra_localidad_nac)
        
        id_localidad_res_final = _get_or_create_localidad(cursor,
                                                          provincia_res, 
                                                          depto_res, 
                                                          otro_departamento_res,
                                                          localidad_res_id, 
                                                          otra_localidad_res,
                                                          codigo_postal_form)
        
        # Actualizar persona
        cursor.execute("""
            UPDATE persona 
            SET nombre = %s, apellido = %s, genero = %s
            WHERE dni = %s
        """, (nombre, apellido, genero, dni))
        
        # Actualizar veterano
        cursor.execute("""
            UPDATE veterano 
            SET fecha_nacimiento = %s,
                localidad_nacimiento = %s,
                localidad_residencia = %s,
                direccion = %s,
                mail = %s,
                id_fuerza = %s,
                id_grado = %s,
                funcion = %s,
                secuelas = %s,
                nro_beneficio_nacional = %s
            WHERE dni_veterano = %s
        """, (fecha_nacimiento, 
              id_localidad_nac_final, 
              id_localidad_res_final,
              direccion or None, 
              mail or None, 
              id_fuerza or None, 
              id_grado_final,
              funcion or None, 
              secuelas or None,
              nro_beneficio or None, 
              dni)
        )
        
        # Actualizar teléfono
        cursor.execute("DELETE FROM telefono_persona WHERE dni = %s", (dni,))
        if telefono:
            cursor.execute("INSERT INTO telefono_persona (dni, telefono) VALUES (%s, %s)", (dni, telefono))
        
        # Gestionar estado de fallecido
        cursor.execute("SELECT dni_veterano FROM fallecido WHERE dni_veterano = %s", (dni,))
        es_fallecido_actual = cursor.fetchone()
        
        if estado_vida == 'fallecido':
            if es_fallecido_actual:
                cursor.execute("""
                    UPDATE fallecido 
                    SET fecha_fallecimiento = %s, id_causa = %s
                    WHERE dni_veterano = %s
                """, (fecha_fallecimiento, id_causa or None, dni))
            else:
                cursor.execute("""
                    INSERT INTO fallecido (dni_veterano, fecha_fallecimiento, id_causa)
                    VALUES (%s, %s, %s)
                """, (dni, fecha_fallecimiento, id_causa or None))
        else:
            if es_fallecido_actual:
                cursor.execute("DELETE FROM fallecido WHERE dni_veterano = %s", (dni,))
        
        conn.commit()
        flash(f"Datos de {nombre} {apellido} actualizados correctamente", "success")
        return redirect(url_for('main.modificar_datos'))
        
    except Exception as e:
        conn.rollback()
        flash(f"Error al actualizar: {str(e)}", "danger")
        printf("Error en modificar_persona_guardar [POST]: {e}")
        return redirect(url_for('main.modificar_persona_form', dni=dni))
    
    finally:
        cursor.close()
        
# ------------------------------------- ELIMINAR VETERANO ------------------------------------- #

@bp.route('/admin/eliminar', methods=['GET'])
@login_required
def eliminar_persona():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Query base
        query = """
            SELECT 
                p.dni,
                p.nombre,
                p.apellido,
                foto.ruta_foto
            FROM persona p
            JOIN veterano v ON p.dni = v.dni_veterano
            LEFT JOIN foto ON v.dni_veterano = foto.dni_veterano
            WHERE 1=1
        """
        
        params = []
        
        dni = request.args.get("dni", "").strip()
        nombre = request.args.get("nombre", "").strip()
        apellido = request.args.get("apellido", "").strip()
        
        # Aplicar filtros
        if dni:
            query += " AND p.dni = %s"
            params.append(dni)
        
        if nombre:
            query += " AND LOWER(p.nombre) LIKE %s"
            params.append("%" + nombre.lower() + "%")
        
        if apellido:
            query += " AND LOWER(p.apellido) LIKE %s"
            params.append("%" + apellido.lower() + "%")
        
        query += " ORDER BY p.apellido, p.nombre"
        
        cursor.execute(query, tuple(params))
        veteranos = cursor.fetchall()

        return render_template('admin/eliminar.html', veteranos=veteranos)

    finally:
        cursor.close()
        
@bp.route('/admin/eliminar/<string:dni>', methods=['POST'])
@login_required
def eliminar_persona_confirmado(dni):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    persona = None
    
    try:
        print(dni)
        dni = dni.strip()
        print(dni)
        
        cursor.execute("""
            SELECT p.nombre, p.apellido 
            FROM persona p
            WHERE p.dni = %s
        """, (dni,))
        
        persona = cursor.fetchone()
        
        if not persona:
            flash("No se encontró una persona con el DNI especificado.", "danger")
            return redirect(url_for('main.eliminar_persona'))
        
        cursor.execute("DELETE FROM persona WHERE dni = %s", (dni,))

        conn.commit()
        
        flash(f"Se eliminó correctamente a {persona['nombre']} {persona['apellido']} (DNI: {dni}).", "success")
        
    except Exception as e:
        conn.rollback()
        flash(f"Error al eliminar la persona: {str(e)}", "danger")
        print(f"Error en eliminar_persona_confirmado [POST]: {e}")
    
    finally:
        cursor.close() 
        print("Persona encontrada:", persona)
        print("Filas afectadas:", cursor.rowcount)

    return redirect(url_for('main.eliminar_persona'), code=303)
