/**
 * Helper para instanciar y mostrar un tab de Bootstrap
 * @param {string} tabId - El ID del *botón* del tab (ej: 'listar-tab')
 */
function showTab(tabId) {
    const tabButton = document.getElementById(tabId);
    if (tabButton) {
        const tabInstance = new bootstrap.Tab(tabButton);
        tabInstance.show();
    }
}

/**
 * Redirige a la página de búsqueda
 * @param {Event} event - El evento de submit del formulario
 */
function buscarDocumentos(event) {
    // Prevenir el envío del formulario
    if (event) {
        event.preventDefault();
    }
    const nombre = document.getElementById('buscar-nombre').value;
    // Asume que la URL base es /admin/documentacion
    // Construye la URL actual con el nuevo parámetro de búsqueda
    const url = new URL(window.location);
    url.searchParams.set('nombre', nombre);
    window.location.href = url.toString();
}

/**
 * Carga un documento y abre el tab de edición
 * @param {string} fetchUrl - La URL de la API para 'obtener_documento'
 * @param {string} actionUrl - La URL del form para 'modificar_documento'
 */
async function editarDocumento(fetchUrl, actionUrl) {
    try {
        const response = await fetch(fetchUrl);
        if (!response.ok) {
            throw new Error(`Error ${response.status}: No se pudo obtener el documento.`);
        }
        
        const doc = await response.json();
        if (doc.error) {
            throw new Error(doc.error);
        }

        // --- 1. Crear el contenido del formulario de edición ---
        const editFormContent = `
        <div class="row">
          <div class="col-lg-8 col-xl-6">
            <form method="POST" enctype="multipart/form-data" action="${actionUrl}">
              <div class="mb-3">
                <label for="edit-nombre" class="form-label">Nombre del documento*</label>
                <input type="text" name="nombre" id="edit-nombre" class="form-control" required value="${doc.nombre}">
              </div>
              <div class="mb-3">
                <label for="edit-descripcion" class="form-label">Descripción</label>
                <textarea name="descripcion" id="edit-descripcion" class="form-control" rows="3">${doc.descripcion || ''}</textarea>
              </div>
              <div class="mb-3">
                <label for="edit-archivo" class="form-label">Reemplazar archivo (opcional)</label>
                <input type="file" name="archivo" id="edit-archivo" class="form-control" accept=".pdf,.doc,.docx,.jpg,.jpeg,.png">
                <div class="form-text">Archivo actual: ${doc.ruta_archivo.split('/').pop()}</div>
              </div>
              <div class="d-flex gap-2">
                <button type="button" class="btn btn-outline-secondary" onclick="cerrarTabEdicion()">Cancelar</button>
                <button type="submit" class="btn btn-primary">Guardar Cambios</button>
              </div>
            </form>
          </div>
        </div>`;
        
        const editPane = document.getElementById('tab-editar');
        editPane.innerHTML = editFormContent;

        // --- 2. Crear el botón del tab de edición (si no existe) ---
        let editTabButton = document.getElementById('editar-tab');
        if (!editTabButton) {
            const tabsContainer = document.getElementById('documentoTabs');
            const newTabLi = document.createElement('li');
            newTabLi.className = 'nav-item';
            newTabLi.setAttribute('role', 'presentation');
            newTabLi.innerHTML = `
                <button class="nav-link" id="editar-tab" data-bs-toggle="tab" data-bs-target="#tab-editar" 
                        type="button" role="tab" aria-controls="tab-editar" aria-selected="false">
                    Editar Documento
                </button>`;
            tabsContainer.appendChild(newTabLi);
            editTabButton = document.getElementById('editar-tab');
        }

        // --- 3. Mostrar el tab de edición ---
        showTab('editar-tab');

    } catch (error) {
        alert('Error al cargar el documento');
        console.error("Error en editarDocumento:", error);
    }
}

/**
 * Elimina el tab de edición y limpia su contenido.
 */
function removeEditTab() {
    // 1. Eliminar el botón del tab de edición
    const editTabButton = document.getElementById('editar-tab');
    if (editTabButton) {
        editTabButton.parentElement.remove(); // Quita el <li>
    }
    
    // 2. Limpiar el contenido del panel de edición
    const editPane = document.getElementById('tab-editar');
    if (editPane) {
        editPane.innerHTML = '';
    }
}

/**
 * Cierra el tab de edición y vuelve a la lista
 */
function cerrarTabEdicion() {
    // 1. Volver al tab de "Listar"
    showTab('listar-tab');

    // 2. Limpiar el tab de edición
    removeEditTab();
}

// --- Limpiar el tab de edición al cambiar a otros tabs ---
document.addEventListener('DOMContentLoaded', () => {
    const listarTabButton = document.getElementById('listar-tab');
    const insertarTabButton = document.getElementById('insertar-tab');

    // Eliminar botones de edición al cambiar a otros tabs
    if (listarTabButton) {
        listarTabButton.addEventListener('show.bs.tab', () => {
            removeEditTab();
        });
    }

    // CuEliminar botones de edición al cambiar a otros tabs
    if (insertarTabButton) {
        insertarTabButton.addEventListener('show.bs.tab', () => {
            removeEditTab();
        });
    }
});