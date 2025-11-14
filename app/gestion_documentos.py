import os
from werkzeug.utils import secure_filename
from flask import render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required
from app.db import get_db
import time
from .routes import bp 

# Configuración de archivos permitidos
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ------------------------------------- VER DOCUMENTOS ------------------------------------- #

@bp.route('/admin/documentacion', methods=['GET'])
@login_required
def documentacion():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        query = "SELECT * FROM documento WHERE 1=1"
        params = []
        
        # Búsqueda por nombre
        nombre = request.args.get("nombre", "").strip()
        if nombre:
            query += " AND nombre LIKE %s"
            params.append(f"%{nombre}%")
        
        query += " ORDER BY id_documento DESC"
        
        cursor.execute(query, tuple(params))
        documentos = cursor.fetchall()
        
        return render_template('admin/documentacion.html', documentos=documentos)
    finally:
        cursor.close()

# ------------------------------------- INSERTAR DOCUMENTO ------------------------------------- #

@bp.route('/admin/documentacion/insertar', methods=['POST'])
@login_required
def insertar_documento():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    try:
        nombre = request.form.get('nombre', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        archivo = request.files.get('archivo')
        
        if not nombre:
            flash("El nombre del documento es obligatorio", "danger")
            return redirect(url_for('main.documentacion'))
        
        if not archivo or archivo.filename == '':
            flash("Debe seleccionar un archivo", "danger")
            return redirect(url_for('main.documentacion'))
        
        if not allowed_file(archivo.filename):
            flash("Tipo de archivo no permitido. Use PDF, Word o imágenes", "danger")
            return redirect(url_for('main.documentacion'))
        
        # Validar tamaño
        archivo.seek(0, os.SEEK_END)
        file_size = archivo.tell()
        archivo.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            flash("El archivo es muy grande. Máximo 10MB", "danger")
            return redirect(url_for('main.documentacion'))
        
        # Guardar archivo:
        filename = secure_filename(archivo.filename)
        # Agregar timestamp para evitar duplicados
        timestamp = str(int(time.time()))
        filename = f"{timestamp}_{filename}"
        upload_dir = os.path.join(current_app.static_folder, 'docs')
        # Crear directorio si no existe
        os.makedirs(upload_dir, exist_ok=True)
        filepath = os.path.join(upload_dir, filename)
        archivo.save(filepath)
        
        # Guardar en base de datos
        ruta_db = f"static/docs/{filename}"
        cursor.execute("""
            INSERT INTO documento (nombre, descripcion, ruta_archivo)
            VALUES (%s, %s, %s)
        """, (nombre, descripcion or None, ruta_db))
        
        conn.commit()
        flash(f"Documento '{nombre}' insertado correctamente", "success")
        
    except Exception as e:
        conn.rollback()
        flash(f"Error al insertar el documento: {str(e)}", "danger")
        print(f"Error en insertar_documento: {e}")
    finally:
        cursor.close()
    
    return redirect(url_for('main.documentacion'))

# ------------------------------------- OBTENER DOCUMENTO (API) ------------------------------------- #

@bp.route('/admin/documentacion/api/<int:id>', methods=['GET'])
@login_required
def obtener_documento(id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM documento WHERE id_documento = %s", (id,))
        doc = cursor.fetchone()
        
        if not doc:
            return jsonify({"error": "Documento no encontrado"}), 404
        
        return jsonify(doc)
    finally:
        cursor.close()

# ------------------------------------- MODIFICAR DOCUMENTO ------------------------------------- #

@bp.route('/admin/documentacion/modificar/<int:id>', methods=['POST'])
@login_required
def modificar_documento(id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    try:
        nombre = request.form.get('nombre', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        archivo = request.files.get('archivo')
        
        if not nombre:
            flash("El nombre del documento es obligatorio", "danger")
            return redirect(url_for('main.documentacion'))
        
        # Obtener documento actual
        cursor.execute("SELECT * FROM documento WHERE id_documento = %s", (id,))
        doc_actual = cursor.fetchone()
        
        if not doc_actual:
            flash("Documento no encontrado", "danger")
            return redirect(url_for('main.documentacion'))
        
        # Definir el directorio de subida primero
        upload_dir = os.path.join(current_app.static_folder, 'docs')
        os.makedirs(upload_dir, exist_ok=True) # Asegurarse de que exista
        
        # Esta es la ruta que se guardará en la BD (empezamos con la actual)
        ruta_archivo_db = doc_actual['ruta_archivo']
        
        # Si hay nuevo archivo, procesarlo
        if archivo and archivo.filename != '':
            if not allowed_file(archivo.filename):
                flash("Tipo de archivo no permitido", "danger")
                return redirect(url_for('main.documentacion'))
            
            # 1. Eliminar archivo anterior
            try:
                old_filename = os.path.basename(doc_actual['ruta_archivo'])
                # Usar upload_dir para construir la ruta a eliminar
                old_filepath = os.path.join(upload_dir, old_filename)
                
                if os.path.exists(old_filepath):
                    os.remove(old_filepath)
            except Exception as e:
                print(f"Error al eliminar archivo anterior: {e}")
            
            # 2. Guardar nuevo archivo
            filename = secure_filename(archivo.filename)
            timestamp = str(int(time.time()))
            filename = f"{timestamp}_{filename}"
            
            # Usar upload_dir para construir la ruta a guardar
            filepath = os.path.join(upload_dir, filename)
            archivo.save(filepath)
            
            # 3. Actualizar la ruta para la BD
            ruta_archivo_db = f"static/docs/{filename}"
                
        # Actualizar en base de datos
        cursor.execute("""
            UPDATE documento 
            SET nombre = %s, descripcion = %s, ruta_archivo = %s
            WHERE id_documento = %s
        """, (nombre, descripcion or None, ruta_archivo_db, id))
        
        conn.commit()
        flash(f"Documento '{nombre}' actualizado correctamente", "success")
        
    except Exception as e:
        conn.rollback()
        flash(f"Error al actualizar el documento: {str(e)}", "danger")
        print(f"Error en modificar_documento: {e}")
    finally:
        cursor.close()
    
    return redirect(url_for('main.documentacion'))

# ------------------------------------- ELIMINAR DOCUMENTO ------------------------------------- #

@bp.route('/admin/documentacion/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_documento(id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Obtener documento
        cursor.execute("SELECT * FROM documento WHERE id_documento = %s", (id,))
        doc = cursor.fetchone()
        
        if not doc:
            flash("Documento no encontrado", "danger")
            return redirect(url_for('main.documentacion'))
        
        # Eliminar archivo físico
        try:
            upload_dir = os.path.join(current_app.static_folder, 'docs')
            filename = os.path.basename(doc['ruta_archivo'])
            filepath = os.path.join(upload_dir, filename)
            
            if os.path.exists(filepath):
                os.remove(filepath)
        except Exception as e:
            print(f"Error al eliminar archivo: {e}")   
                 
        # Eliminar de base de datos
        cursor.execute("DELETE FROM documento WHERE id_documento = %s", (id,))
        conn.commit()
        
        flash(f"Documento '{doc['nombre']}' eliminado correctamente", "success")
        
    except Exception as e:
        conn.rollback()
        flash(f"Error al eliminar el documento: {str(e)}", "danger")
        print(f"Error en eliminar_documento: {e}")
    finally:
        cursor.close()
    
    return redirect(url_for('main.documentacion'), code=303)