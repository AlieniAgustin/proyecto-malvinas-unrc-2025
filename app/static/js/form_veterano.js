/* * static/js/form_persona.js
 * Lógica compartida para los formularios de insertar y modificar persona.
 * Lee datos (grados, veterano) inyectados desde el HTML a través de window.APP_DATA.
 */

// --- VARIABLES GLOBALES (inyectadas desde HTML) ---
const gradosData = (window.APP_DATA && window.APP_DATA.grados) ? window.APP_DATA.grados : [];


// --- DEFINICIONES DE FUNCIONES ---

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
 * Carga los departamentos de una provincia en un <select>.
 */
async function cargarDepartamentos(provinciaId, deptoSelect, localidadSelect) {
    deptoSelect.disabled = true;
    deptoSelect.innerHTML = '<option value="">Cargando...</option>';
    localidadSelect.disabled = true;
    localidadSelect.innerHTML = '<option value="">Seleccione una localidad</option>';

    const otroDeptoInputId = deptoSelect.id.replace('departamento_', 'otro_departamento_');
    const otraLocInputId = localidadSelect.id.replace('localidad_', 'otra_localidad_');
    document.getElementById(otroDeptoInputId).style.display = 'none';
    document.getElementById(otraLocInputId).style.display = 'none';

    if (!provinciaId) {
        deptoSelect.innerHTML = '<option value="">Seleccione un departamento</option>';
        deptoSelect.innerHTML += '<option value="otro">Otro</option>'; 
        return;
    }

    try {
        const response = await fetch(`/api/localidades/${provinciaId}`);
        if (!response.ok) throw new Error('Error de red');
        const departamentos = await response.json();

        deptoSelect.innerHTML = '<option value="">Seleccione un departamento</option>';
        departamentos.forEach(depto => {
            deptoSelect.innerHTML += `<option value="${depto}">${depto}</option>`;
        });
        
        deptoSelect.innerHTML += '<option value="otro">Otro</option>'; 
        deptoSelect.disabled = false;
    } catch (error) {
        console.error('Error al cargar departamentos:', error);
        deptoSelect.innerHTML = '<option value="">Error al cargar</option>';
    }
}

/**
 * Carga las localidades de un departamento/provincia en un <select>.
 */
async function cargarLocalidades(provinciaId, departamento, localidadSelect, cpInput = null) {
    localidadSelect.disabled = true;
    localidadSelect.innerHTML = '<option value="">Cargando...</option>';

    const otraLocInputId = localidadSelect.id.replace('localidad_', 'otra_localidad_');
    document.getElementById(otraLocInputId).style.display = 'none';

    if (!provinciaId || !departamento) {
        localidadSelect.innerHTML = '<option value="">Seleccione una localidad</option>';
        localidadSelect.innerHTML += '<option value="otra">Otra</option>';
        return;
    }

    try {
        const response = await fetch(`/api/localidades/${provinciaId}/${encodeURIComponent(departamento)}`);
        if (!response.ok) throw new Error('Error de red');
        const localidades = await response.json();

        localidadSelect.innerHTML = '<option value="">Seleccione una localidad</option>';
        localidades.forEach(loc => {
            const option = document.createElement('option');
            option.value = loc.id_localidad;
            option.textContent = loc.nombre_localidad;
            option.setAttribute('data-codigo-postal', loc.codigo_postal || '');
            localidadSelect.appendChild(option);
        });
        
        const optionOtra = document.createElement('option');
        optionOtra.value = 'otra';
        optionOtra.textContent = 'Otra';
        localidadSelect.appendChild(optionOtra);

        localidadSelect.disabled = false;
    } catch (error) {
        console.error('Error al cargar localidades:', error);
        localidadSelect.innerHTML = '<option value="">Error al cargar</option>';
    }
}

/**
 * Configura los event listeners para un grupo de selects de ubicación (prov/depto/loc).
 */
function setupUbicacionHandlers(provinciaId, deptoId, localidadId, otroDeptoId, otraLocalidadId, cpId = null) {
    const provinciaSelect = document.getElementById(provinciaId);
    const deptoSelect = document.getElementById(deptoId);
    const localidadSelect = document.getElementById(localidadId);
    const otroDeptoInput = document.getElementById(otroDeptoId);
    const otraLocalidadInput = document.getElementById(otraLocalidadId);
    const cpInput = cpId ? document.getElementById(cpId) : null;

    provinciaSelect.addEventListener('change', function () {
        if (cpInput) {
            cpInput.value = '';
            cpInput.readOnly = true;
            cpInput.placeholder = 'Se completa automáticamente';
        }
        cargarDepartamentos(this.value, deptoSelect, localidadSelect);
    });

    deptoSelect.addEventListener('change', function () {
        if (this.value === 'otro') {
            otroDeptoInput.style.display = 'block';
            localidadSelect.disabled = true; 
            localidadSelect.innerHTML = '<option value="otra" selected>Otra</option>'; 
            otraLocalidadInput.style.display = 'block'; 
            
            if (cpInput) {
                cpInput.value = ''; 
                cpInput.readOnly = false; 
                cpInput.placeholder = 'Ingrese el C.P.';
            }
        } else {
            otroDeptoInput.style.display = 'none';
            if (cpInput) cpInput.value = '';
            cargarLocalidades(provinciaSelect.value, this.value, localidadSelect, cpInput);
        }
    });
    
    localidadSelect.addEventListener('change', function () {
        const selectedOption = this.options[this.selectedIndex];
        
        if (this.value === 'otra') {
            otraLocalidadInput.style.display = 'block';
            if (cpInput) {
                cpInput.value = '';
                cpInput.readOnly = false;
                cpInput.placeholder = 'Ingrese el C.P.';
            }
        } else {
            otraLocalidadInput.style.display = 'none';
            if (cpInput) {
                cpInput.value = selectedOption.getAttribute('data-codigo-postal') || '';
                cpInput.readOnly = true; 
                cpInput.placeholder = 'Se completa automáticamente';
            }
        }
    });
}

/**
 * Lógica de inicialización específica para el formulario de 'Modificar'.
 * Pre-carga y selecciona los valores existentes del veterano.
 */
async function initModificarForm(veteranoData) {
    // 1. Cargar ubicación de nacimiento
    if (veteranoData.provinciaNacimiento) {
        const provNac = document.getElementById('provincia_nacimiento');
        const deptoNac = document.getElementById('departamento_nacimiento');
        const locNac = document.getElementById('localidad_nacimiento');
        
        await cargarDepartamentos(provNac.value, deptoNac, locNac);
        if (veteranoData.departamentoNacimiento) {
            deptoNac.value = veteranoData.departamentoNacimiento;
            await cargarLocalidades(provNac.value, deptoNac.value, locNac);
            if (veteranoData.localidadNacimiento) {
                locNac.value = veteranoData.localidadNacimiento;
            }
        }
    }

    // 2. Cargar ubicación de residencia
    if (veteranoData.provinciaResidencia) {
        const provRes = document.getElementById('provincia_residencia');
        const deptoRes = document.getElementById('departamento_residencia');
        const locRes = document.getElementById('localidad_residencia');
        const cpInput = document.getElementById('codigo_postal');
        
        await cargarDepartamentos(provRes.value, deptoRes, locRes);
        if (veteranoData.departamentoResidencia) {
            deptoRes.value = veteranoData.departamentoResidencia;
            await cargarLocalidades(provRes.value, deptoRes.value, locRes, cpInput);
            if (veteranoData.localidadResidencia) {
                locRes.value = veteranoData.localidadResidencia;
                locRes.dispatchEvent(new Event('change'));
            }
        }
    }
    
    // 3. Cargar grado
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
}


// --- EJECUCIÓN PRINCIPAL (al cargar el DOM) ---

window.addEventListener('DOMContentLoaded', function () {
    
    // 1. Configurar los listeners de ubicación
    setupUbicacionHandlers(
        'provincia_nacimiento',
        'departamento_nacimiento',
        'localidad_nacimiento',
        'otro_departamento_nacimiento',
        'otra_localidad_nacimiento'
    );

    setupUbicacionHandlers(
        'provincia_residencia',
        'departamento_residencia',
        'localidad_residencia',
        'otro_departamento_residencia',
        'otra_localidad_residencia',
        'codigo_postal' 
    );

    // 2. Configurar listener de edad
    calcularEdad();
    document.getElementById('fecha_nacimiento').addEventListener('change', calcularEdad);

    // 3. Configurar listener de estado de vida
    document.querySelectorAll('input[name="estado_vida"]').forEach(radio => {
        radio.addEventListener('change', function() {
            const display = this.value === 'fallecido' ? 'block' : 'none';
            document.getElementById('fecha_fallecido').style.display = display;
            document.getElementById('causa_fallecido').style.display = display;
        });
    });

    // 4. Configurar listeners de fuerza/grado
    document.getElementById('fuerza').addEventListener('change', function () {
        const fuerzaId = this.value;
        const gradoSelect = document.getElementById('grado');
        const valorAnterior = gradoSelect.value;
        
        gradoSelect.innerHTML = '<option value="">Seleccione un grado</option><option value="otro">Otro</option>';
        document.getElementById('otro_grado').style.display = 'none';

        if (fuerzaId) {
            // Lee desde la variable global inyectada
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

    document.getElementById('grado').addEventListener('change', function() {
        const otroGrado = document.getElementById('otro_grado');
        otroGrado.style.display = this.value === 'otro' ? 'block' : 'none';
    });
    
    // 5. Ejecutar inicialización
    // Comprueba si se pasaron datos de un veterano (página de modificar)
    if (window.APP_DATA && window.APP_DATA.veterano) {
        // Estamos en 'modificar', ejecutar la inicialización
        initModificarForm(window.APP_DATA.veterano);
    } else {
        // Estamos en 'insertar', solo disparamos el change de 'fuerza'
        // para que se popule la lista de grados (vacía si no hay fuerza)
        document.getElementById('fuerza').dispatchEvent(new Event('change'));
    }
});