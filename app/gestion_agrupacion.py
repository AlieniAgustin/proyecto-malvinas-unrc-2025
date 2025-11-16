import os
from flask import render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from app.db import get_db
from .routes import bp 
7
@bp.route('/admin/actualizar', methods=['GET', 'POST'])
@login_required
def actualizar_info_agrupacion():
    ID_AGRUPACION_ADMIN = 1 
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    try:
        if request.method == 'POST':
            # --- 1. Actualizar tabla 'agrupacion' ---
            nombre_agrupacion = request.form.get('nombre_agrupacion')
            direccion = request.form.get('direccion')
            mail = request.form.get('email')
            localidad_id = request.form.get('localidad_agrupacion')
            
            cursor.execute("""
                UPDATE agrupacion SET
                    nombre_agrupacion = %s,
                    direccion = %s,
                    mail = %s,
                    localidad_agrupacion = %s
                WHERE id_agrupacion = %s
            """, (nombre_agrupacion, direccion, mail, localidad_id, ID_AGRUPACION_ADMIN))
            
            # --- 2. Actualizar 'telefono_agrupacion' (Borrar y re-insertar) ---
            telefonos = request.form.getlist('telefonos[]') # Recibe una lista
            cursor.execute("DELETE FROM telefono_agrupacion WHERE id_agrupacion = %s", (ID_AGRUPACION_ADMIN,))
            if telefonos:
                tel_data = [(ID_AGRUPACION_ADMIN, tel) for tel in telefonos if tel.strip()]
                if tel_data:
                    cursor.executemany("INSERT INTO telefono_agrupacion (id_agrupacion, telefono) VALUES (%s, %s)", tel_data)

            # --- 3. Actualizar 'red_social' (Facebook/Instagram) ---
            facebook_url = request.form.get('facebook')
            instagram_url = request.form.get('instagram')

            # Borramos las existentes y las creamos de nuevo si tienen valor
            cursor.execute("DELETE FROM red_social WHERE id_agrupacion = %s AND nombre IN ('Facebook', 'Instagram')", (ID_AGRUPACION_ADMIN,))
            redes_data = []
            if facebook_url:
                redes_data.append(('Facebook', facebook_url, ID_AGRUPACION_ADMIN))
            if instagram_url:
                redes_data.append(('Instagram', instagram_url, ID_AGRUPACION_ADMIN))
            
            if redes_data:
                cursor.executemany("INSERT INTO red_social (nombre, link, id_agrupacion) VALUES (%s, %s, %s)", redes_data)

            # --- 4. Actualizar 'autoridad' (Borrar y re-insertar) ---
            roles_ids = request.form.getlist('autoridad_rol[]')
            dnis_autoridad = request.form.getlist('autoridad_dni[]')
            
            # Primero, borramos TODAS las autoridades de esta agrupación
            cursor.execute("""
                DELETE a FROM autoridad a
                JOIN veterano v ON a.dni_autoridad = v.dni_veterano
                WHERE v.id_agrupacion = %s
            """, (ID_AGRUPACION_ADMIN,))

            # Segundo, re-insertamos las que vinieron del formulario
            if roles_ids and dnis_autoridad and len(roles_ids) == len(dnis_autoridad):
                autoridades_data = [
                    (dni, rol_id) for dni, rol_id in zip(dnis_autoridad, roles_ids) if dni and rol_id
                ]
                if autoridades_data:
                    cursor.executemany("INSERT INTO autoridad (dni_autoridad, id_rol) VALUES (%s, %s)", autoridades_data)

            conn.commit()
            flash("Información de la agrupación actualizada correctamente.", "success")
            return redirect(url_for('main.actualizar_info_agrupacion'))

        # --- LÓGICA GET ---
        
        # 1. Info básica de la agrupación
        cursor.execute("""
            SELECT a.*, loc.id_provincia 
            FROM agrupacion a 
            LEFT JOIN localidad loc ON a.localidad_agrupacion = loc.id_localidad
            WHERE a.id_agrupacion = %s
        """, (ID_AGRUPACION_ADMIN,))
        agrupacion = cursor.fetchone()
        
        # 2. Teléfonos
        cursor.execute("SELECT telefono FROM telefono_agrupacion WHERE id_agrupacion = %s", (ID_AGRUPACION_ADMIN,))
        telefonos_db = cursor.fetchall()
        telefonos = [t['telefono'] for t in telefonos_db]
        
        # 3. Redes Sociales
        cursor.execute("SELECT nombre, link FROM red_social WHERE id_agrupacion = %s", (ID_AGRUPACION_ADMIN,))
        redes_db = cursor.fetchall()
        redes = {
            'facebook': next((r['link'] for r in redes_db if r['nombre'].lower() == 'facebook'), ''),
            'instagram': next((r['link'] for r in redes_db if r['nombre'].lower() == 'instagram'), '')
        }

        # 4. Autoridades actuales
        cursor.execute("""
            SELECT 
                r.nombre_rol, 
                p.nombre, 
                p.apellido, 
                a.dni_autoridad,
                a.id_rol
            FROM autoridad a
            JOIN rol r ON a.id_rol = r.id_rol
            JOIN persona p ON a.dni_autoridad = p.dni
            JOIN veterano v ON p.dni = v.dni_veterano
            WHERE v.id_agrupacion = %s
            ORDER BY r.id_rol
        """, (ID_AGRUPACION_ADMIN,))
        autoridades = cursor.fetchall()
        
        # 5. Datos para los <select>
        cursor.execute("SELECT id_provincia, nombre FROM provincia ORDER BY nombre")
        provincias = cursor.fetchall()
        
        cursor.execute("SELECT id_rol, nombre_rol FROM rol ORDER BY id_rol")
        roles = cursor.fetchall()
        
        return render_template('admin/actualizar.html',
                               agrupacion=agrupacion,
                               telefonos=telefonos,
                               redes=redes,
                               autoridades=autoridades,
                               provincias=provincias,
                               roles=roles)

    except Exception as e:
        conn.rollback()
        print(f"Error en actualizar_info_agrupacion: {e}")
        flash(f"Ocurrió un error al procesar la solicitud: {e}", "danger")
        return redirect(url_for('main.dashboard'))
    
    finally:
        cursor.close()