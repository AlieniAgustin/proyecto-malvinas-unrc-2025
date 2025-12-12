/* static/js/form_agrupacion.js */

// Datos globales inyectados desde el HTML
const agrupacionData = (window.APP_DATA && window.APP_DATA.agrupacion) ? window.APP_DATA.agrupacion : null;

function setupUbicacionHandlers(provinciaSelectId, localidadSelectId, cpInputId = null) {
    // Usamos jQuery (requerido por Select2)
    const $provinciaSelect = $(`#${provinciaSelectId}`);
    const $localidadSelect = $(`#${localidadSelectId}`);
    const $cpInput = cpInputId ? $(`#${cpInputId}`) : null;

    // Inicializa Select2 en la provincia (para que sea buscable)
    $provinciaSelect.select2({ 
        theme: "bootstrap-5",
        width: '100%',
        placeholder: "Seleccione una provincia"
    });

    // Inicializa Select2 en la localidad (configuración AJAX)
    $localidadSelect.select2({
        theme: "bootstrap-5",
        width: '100%',
        placeholder: '(Seleccione una provincia primero)',
        ajax: {
            url: "/api/localidades/buscar",
            dataType: 'json',
            delay: 50, // Espera 50ms antes de buscar
            data: function (params) {
                return {
                    q: params.term, // Término de búsqueda
                    provincia_id: $provinciaSelect.val() // Pasa el ID de la provincia
                };
            },
            processResults: function (data) {
                return {
                    results: data.items // Select2 espera { results: [...] }
                };
            },
            cache: true
        }
    });

    // Cuando cambia la provincia, resetea y habilita la localidad
    $provinciaSelect.on('change', function() {
        // Limpia la selección de localidad y el CP
        $localidadSelect.val(null).trigger('change');
        if ($cpInput) $cpInput.val('');
        
        if ($provinciaSelect.val()) {
            // Habilita el Select2 de localidad
            $localidadSelect.prop("disabled", false);
            $localidadSelect.select2('open'); // Abre el dropdown para buscar
        } else {
            // Deshabilita si no hay provincia
            $localidadSelect.prop("disabled", true);
        }
    });
}

/**
 * Lógica de inicialización para el formulario 'Actualizar Agrupación'
 */
async function initAgrupacionForm(data) {
    if (!data) return;

    // Pre-cargar localidad de la agrupación
    if (data.localidadAgrupacion) {
        const $locSelect = $('#localidad_agrupacion');
        
        // Llama a la API para obtener los datos de la localidad
        try {
            // Usamos la API que busca por ID
            const response = await fetch(`/api/localidad/${data.localidadAgrupacion}`); 
            
            if (response.ok) {
                const locData = await response.json();
                // Crea la <option>
                const option = new Option(locData.text, locData.id, true, true);
                $locSelect.append(option).trigger('change');
                // Habilita el select
                $locSelect.prop("disabled", false);
            } else {
                console.error("Error: No se pudo cargar la localidad", data.localidadAgrupacion);
            }
        } catch (e) { 
            console.error("Error en fetch de localidad:", e); 
        }
    }
}

/**
 * Configura el modal de búsqueda de veteranos
 */
function setupVeteranoSearchModal() {
    const $modal = $('#modalAgregarAutoridad');
    const $selectVeterano = $('#select-veterano-modal');
    const $selectRol = $('#select-rol-modal');
    const $btnGuardar = $('#btn-guardar-autoridad-modal');

    $selectVeterano.select2({
        theme: "bootstrap-5",
        width: '100%',
        placeholder: 'Buscar veterano por DNI, nombre o apellido...',
        dropdownParent: $modal, // para que el buscador funcione dentro del modal
        ajax: {
            url: "/api/veteranos/buscar", 
            dataType: 'json',
            delay: 100,
            data: function (params) {
                return {
                    q: params.term // Término de búsqueda
                };
            },
            processResults: function (data) {
                return {
                    results: data.items.map(v => ({
                        id: v.dni,
                        text: `${v.apellido}, ${v.nombre} (DNI: ${v.dni})`,
                        data: v 
                    }))
                };
            },
            cache: true
        }
    });

    // Lógica para agregar la autoridad al DOM
    $btnGuardar.on('click', function() {
        const veteranoData = $selectVeterano.select2('data')[0];
        const rolId = $selectRol.val();
        const rolText = $selectRol.find('option:selected').text();

        if (!veteranoData || !rolId) {
            alert('Debe seleccionar un rol y un veterano.');
            return;
        }
        
        // Chequear que la autoridad a agregar no tenga otro rol
        const dni = veteranoData.id;
        const grid = document.getElementById('autoridades-grid');
        if (grid.querySelector(`div[data-dni="${dni}"]`)) {
            alert('Esta persona ya tiene un rol. No puede ser asignada a más de un cargo');
            return;
        }
        
        // Agregar al DOM
        addAutoridadToDOM({
            dni: veteranoData.id,
            nombreCompleto: veteranoData.text,
            idRol: rolId,
            nombreRol: rolText
        });

        // Limpiar y cerrar modal
        $selectVeterano.val(null).trigger('change');
        $selectRol.val('');
    });
}

/**
 * Helper para añadir la nueva autoridad al formulario
 */
function addAutoridadToDOM(data) {
    const html = `
    <div data-dni="${data.dni}">
        <div class="autoridad-item">
            <label>${data.nombreRol}</label>
            <div class="autoridad-input-group">
                <input type="text" value="${data.nombreCompleto}" disabled>
                <button class="btn-eliminar-autoridad" type="button">
                    <i class="bi bi-trash"></i>
                </button>
                <input type="hidden" name="autoridad_rol[]" value="${data.idRol}">
                <input type="hidden" name="autoridad_dni[]" value="${data.dni}">
            </div>
        </div>
    </div>
    `;
    
    const grid = document.getElementById('autoridades-grid');
    grid.querySelector('[style*="grid-column"]').insertAdjacentHTML('beforebegin', html);
    
    grid.querySelector(`[data-dni="${data.dni}"] .btn-eliminar-autoridad`).addEventListener('click', function() {
        // Ahora el <div> padre es el que tiene el data-dni
        this.closest('div[data-dni]').remove();
    });
}


function setupTelefonoHandlers() {
    const container = document.getElementById('telefonos-container');
    const btnAgregar = document.getElementById('btn-agregar-telefono');
    const template = document.getElementById('telefono-template');

    // Función para agregar un nuevo input de teléfono
    function agregarTelefono() {
        const newGroup = template.cloneNode(true);
        newGroup.id = '';
        newGroup.style.display = 'flex';
        container.insertBefore(newGroup, template);
        // Agregar listener al botón eliminar
        newGroup.querySelector('.btn-eliminar-telefono').addEventListener('click', function() {
            newGroup.remove();
        });
    }

    // Agregar listener al botón de agregar
    btnAgregar.addEventListener('click', agregarTelefono);

    // Agregar listeners a los botones eliminar existentes
    document.querySelectorAll('.btn-eliminar-telefono').forEach(btn => {
        btn.addEventListener('click', function() {
            this.closest('.telefono-input-group').remove();
        });
    });
}

// --- EJECUCIÓN PRINCIPAL ---
window.addEventListener('DOMContentLoaded', function () {
    
    // 1. Configurar los handlers de ubicación para la agrupación
    setupUbicacionHandlers(
        'provincia_agrupacion',
        'localidad_agrupacion'
    );

    // 2. Configurar handlers para teléfonos
    setupTelefonoHandlers();

    // 3. Configurar el modal de búsqueda de veteranos
    setupVeteranoSearchModal();
    
    // 4. Añadir listeners a los botones "eliminar" ya existentes
    document.querySelectorAll('.btn-eliminar-autoridad').forEach(btn => {
        btn.addEventListener('click', function() {
            this.closest('div[data-dni]').remove();
        });
    });

    // 5. Inicializar el formulario con datos pre-cargados
    if (agrupacionData) {
        initAgrupacionForm(agrupacionData);
    }
});