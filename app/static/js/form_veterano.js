/* static/js/form_veterano.js */

// Datos globales inyectados desde el HTML
const gradosData = (window.APP_DATA && window.APP_DATA.grados) ? window.APP_DATA.grados : [];
const veteranoData = (window.APP_DATA && window.APP_DATA.veterano) ? window.APP_DATA.veterano : null;

/**
 * Configura el dropdown Select2 para códigos postales según la localidad
 */
function setupCodigoPostalHandler(localidadSelectId, codigoPostalSelectId, otroInputId = null) {
    const $localidadSelect = $(`#${localidadSelectId}`);
    const $codigoSelect = $(`#${codigoPostalSelectId}`);
    const $otroInput = otroInputId ? $(`#${otroInputId}`) : null;

    // Inicializa Select2
    $codigoSelect.select2({
        theme: "bootstrap-5",
        width: '100%',
        placeholder: "Seleccione un código postal",
        ajax: {
            url: "/api/codigos_postales",
            dataType: 'json',
            delay: 50,
            data: function (params) {
                return {
                    q: params.term,
                    localidad_id: $localidadSelect.val()
                };
            },
            processResults: function (data) {
                return { results: data.items };
            },
            cache: true
        }
    });

    // Cuando cambia la localidad, limpiamos el código postal
    $localidadSelect.on('change', function() {
        $codigoSelect.val(null).trigger('change');
        if ($localidadSelect.val()) {
            $codigoSelect.prop("disabled", false);
            $codigoSelect.select2('open');
        } else {
            $codigoSelect.prop("disabled", true);
        }
        if ($otroInput) $otroInput.hide().val('');
    });

    // Mostrar campo "Otro" cuando se selecciona “otro”
    $codigoSelect.on('change', function() {
        if ($codigoSelect.val() === 'otro') {
            if ($otroInput) $otroInput.show();
        } else {
            if ($otroInput) $otroInput.hide().val('');
        }
    });
}

/**
 * Calcula y muestra la edad basada en la fecha de nacimiento.
 */
function calcularEdad() {
    const fechaNac = document.getElementById('fecha_nacimiento').value;
    const edadInput = document.getElementById('edad');
    if (fechaNac) {
        const hoy = new Date();
        const nacimiento = new Date(fechaNac);
        let edad = hoy.getFullYear() - nacimiento.getFullYear();
        const mes = hoy.getMonth() - nacimiento.getMonth();
        if (mes < 0 || (mes === 0 && hoy.getDate() < nacimiento.getDate())) {
            edad--;
        }
        edadInput.value = (edad >= 0) ? edad + ' años' : '';
    } else {
        edadInput.value = '';
    }
}

/**
 * Configura los event listeners para un grupo de Provincia -> Localidad (con Select2)
 */
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
 * Lógica de inicialización para el formulario 'Modificar'
 */
async function initModificarForm(veteranoData) {
    
    // Pre-cargar localidad de nacimiento
    if (veteranoData.localidadNacimiento) {
        const $locNacSelect = $('#localidad_nacimiento');
        // Llama a la API para obtener los datos de la localidad
        try {
            const response = await fetch(`/api/localidad/${veteranoData.localidadNacimiento}`);
            if (response.ok) {
                const locData = await response.json();
                // Crea la <option>
                const option = new Option(locData.text, locData.id, true, true);
                $locNacSelect.append(option).trigger('change');
                // Habilita el select
                $locNacSelect.prop("disabled", false);
            }
        } catch (e) { console.error("Error cargando localidad nac:", e); }
    }

    // Pre-cargar localidad de residencia
    if (veteranoData.localidadResidencia) {
        const $locResSelect = $('#localidad_residencia');
        try {
            const response = await fetch(`/api/localidad/${veteranoData.localidadResidencia}`);
            if (response.ok) {
                const locData = await response.json();
                const option = new Option(locData.text, locData.id, true, true);
                $locResSelect.append(option).trigger('change');
                $locResSelect.prop("disabled", false);
            }
        } catch (e) { console.error("Error cargando localidad res:", e); }
    }
    
    // Cargar grado
    if (veteranoData.idFuerza) {
        const fuerzaSelect = document.getElementById('fuerza');
        const gradoSelect = document.getElementById('grado');
        
        if (veteranoData.idGrado) {
            gradoSelect.value = veteranoData.idGrado;
        }
        fuerzaSelect.dispatchEvent(new Event('change'));
        if (veteranoData.idGrado) {
            gradoSelect.value = veteranoData.idGrado;
        }
    }

    // --- Precargar código postal ---
    if (veteranoData.codigoPostal) {
        const $cpSelect = $('#codigo_postal');
        try {
            // Agrega la opción actual como seleccionada
            const option = new Option(veteranoData.codigoPostal, veteranoData.codigoPostal, true, true);
            $cpSelect.append(option).trigger('change');
            $cpSelect.prop("disabled", false);
        } catch (e) { console.error("Error cargando código postal:", e); }
    }

}

// --- EJECUCIÓN PRINCIPAL ---
window.addEventListener('DOMContentLoaded', function () {
    
    setupUbicacionHandlers(
        'provincia_nacimiento',
        'localidad_nacimiento'
    );

    setupUbicacionHandlers(
        'provincia_residencia',
        'localidad_residencia',
        'codigo_postal'
    );

    setupCodigoPostalHandler('localidad_residencia', 'codigo_postal', 'otro_codigo_postal');

    // Validacion de fecha de nacimiento
    const fechaNacInput = document.getElementById('fecha_nacimiento');

    function validarFechaNacimiento() {
        if (!fechaNacInput || !fechaNacInput.value) return true;

        const hoy = new Date();
        hoy.setHours(0, 0, 0, 0); // Ignorar hora
        const fechaNac = new Date(fechaNacInput.value + 'T00:00:00');

        if (fechaNac > hoy) {
            alert("La fecha de nacimiento no puede ser futura.");
            fechaNacInput.value = ""; // Limpiar el campo
            fechaNacInput.classList.add('is-invalid'); // Feedback visual (Bootstrap)
            document.getElementById('edad').value = ""; // Limpiar edad calculada
            return false;
        } else {
            fechaNacInput.classList.remove('is-invalid');
            return true;
        }
    }

    if (fechaNacInput) {
        // Calcular edad inicial si hay valor
        calcularEdad();

        fechaNacInput.addEventListener('change', function() {
            if (validarFechaNacimiento()) {
                calcularEdad();
            }
        });
    }


    // Configurar listener de estado de vida
    document.querySelectorAll('input[name="estado_vida"]').forEach(radio => {
        radio.addEventListener('change', function() {
            const display = this.value === 'fallecido' ? 'block' : 'none';
            document.getElementById('fecha_fallecido').style.display = display;
            document.getElementById('causa_fallecido').style.display = display;
        });
    });

    // 4. Configurar listeners de fuerza/grado
    // Usamos jQuery .on() ya que Select2 lo prefiere
    $('#fuerza').on('change', function () {
        const fuerzaId = this.value;
        const gradoSelect = document.getElementById('grado');
        const valorAnterior = gradoSelect.value;
        
        gradoSelect.innerHTML = '<option value="">Seleccione un grado</option><option value="otro">Otro</option>';
        document.getElementById('otro_grado').style.display = 'none';

        if (fuerzaId) {
            gradosData.filter(g => g.id_fuerza == fuerzaId).forEach(grado => {
                const option = document.createElement('option');
                option.value = grado.id_grado;
                option.textContent = grado.nombre;
                gradoSelect.insertBefore(option, gradoSelect.lastChild); 
            });
            gradoSelect.disabled = false;
            
            if (valorAnterior && gradoSelect.querySelector(`option[value="${valorAnterior}"]`)) {
                gradoSelect.value = valorAnterior;
            }
        } else {
            gradoSelect.disabled = true; 
        }
    });

    $('#grado').on('change', function() {
        const otroGrado = document.getElementById('otro_grado');
        otroGrado.style.display = this.value === 'otro' ? 'block' : 'none';
    });

    // Validaciones de fechas de fallecimiento
    const fechaNacimiento = document.getElementById('fecha_nacimiento');
    const fechaFallecimiento = document.getElementById('fecha_fallecimiento');
    const errorFechaFallecimiento = document.getElementById('error_fecha_fallecimiento');
    
    function validarFechaFallecimiento() {
        if (!fechaFallecimiento || !fechaFallecimiento.value) {
            errorFechaFallecimiento.classList.add('d-none');
            return true;
        }
        
        const hoy = new Date();
        hoy.setHours(0, 0, 0, 0);
        const fechaFall = new Date(fechaFallecimiento.value);
        const fechaNac = fechaNacimiento.value ? new Date(fechaNacimiento.value) : null;
        
        // Validar que no sea fecha futura
        if (fechaFall > hoy) {
            errorFechaFallecimiento.textContent = 'La fecha de fallecimiento no puede ser futura';
            errorFechaFallecimiento.classList.remove('d-none');
            fechaFallecimiento.classList.add('is-invalid');
            return false;
        }
        
        // Validar que no sea anterior a la fecha de nacimiento
        if (fechaNac && fechaFall < fechaNac) {
            errorFechaFallecimiento.textContent = 'La fecha de fallecimiento no puede ser anterior a la de nacimiento';
            errorFechaFallecimiento.classList.remove('d-none');
            fechaFallecimiento.classList.add('is-invalid');
            return false;
        }
        
        errorFechaFallecimiento.classList.add('d-none');
        fechaFallecimiento.classList.remove('is-invalid');
        return true;
    }
    
    if (fechaFallecimiento) {
        fechaFallecimiento.addEventListener('change', validarFechaFallecimiento);
        fechaNacimiento.addEventListener('change', validarFechaFallecimiento);
    }
    
    // Ejecutar inicialización
    if (window.APP_DATA && window.APP_DATA.veterano) {
        initModificarForm(window.APP_DATA.veterano);
    } else {
        document.getElementById('fuerza').dispatchEvent(new Event('change'));
    }
});
