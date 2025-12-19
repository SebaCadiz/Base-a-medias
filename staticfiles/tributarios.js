// Archivo: NUAM/app/static/tributarios.js (CONTENIDO COMPLETO Y FINAL)

document.addEventListener('DOMContentLoaded', function() {
    // 1. Sistema de Tabulación (Se mantiene)
    const tabButtons = document.querySelectorAll('.tab-button');
    const contentTabs = document.querySelectorAll('.content-tab');

    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tabName = this.getAttribute('data-tab');
            
            tabButtons.forEach(btn => btn.classList.remove('active'));
            contentTabs.forEach(tab => tab.classList.remove('active'));
            
            this.classList.add('active');
            document.getElementById(tabName).classList.add('active');
        });
    });

    // Establecer 'Mis Contribuyentes' como activo por defecto
    const defaultTabButton = document.querySelector('[data-tab="contribuyentes-tab"]');
    const defaultTabContent = document.getElementById('contribuyentes-tab');
    if (defaultTabButton && defaultTabContent) {
        defaultTabButton.classList.add('active');
        defaultTabContent.classList.add('active');
    }


    // 2. Elementos del Formulario de Creación (¡IDs actualizados!)
    const paisSelect = document.getElementById('id_pais');
    const tipoSelect = document.getElementById('tipo'); // ID ACTUALIZADO
    const identificadorInput = document.getElementById('identificador_tributario');
    const identificadorHelper = document.getElementById('identificador-helper');
    const empleadosGroup = document.getElementById('empleados-group');
    const empleadosInput = document.getElementById('empleados');

    // 3. Definiciones de Formato de Identificadores Tributarios por País (Se mantiene)
    const FORMATO_IDENTIFICADORES = {
        'Chile': { label: 'RUT (Ej: 76.284.155-K)', regex: /^\d{1,2}\.\d{3}\.\d{3}-[\dkK]$/i, placeholder: 'Ej: 76.284.155-K' },
        'Colombia': { label: 'NIT (Ej: XXXXXXXXX-X)', regex: /^\d{9}-\d{1}$/, placeholder: 'Ej: 900.123.456-7' },
        'Perú': { label: 'RUC (Ej: XXXXXXXXXXX)', regex: /^\d{11}$/, placeholder: 'Ej: 20512345678' },
    };

    /**
     * Valida el formato del identificador tributario según el país seleccionado.
     */
    function validateTributario() {
        if (!paisSelect || !identificadorInput) return true;

        const selectedPaisName = paisSelect.options[paisSelect.selectedIndex].textContent.trim();
        const identificadorValue = identificadorInput.value.trim();
        const format = FORMATO_IDENTIFICADORES[selectedPaisName];
        
        identificadorHelper.textContent = format ? format.label : 'Formato desconocido para este país.';
        
        if (format && identificadorValue) {
            if (!format.regex.test(identificadorValue)) {
                identificadorInput.classList.add('error');
                identificadorHelper.style.color = 'red';
                return false;
            } else {
                identificadorInput.classList.remove('error');
                identificadorHelper.style.color = '#6c757d';
                return true;
            }
        }
        
        identificadorInput.classList.remove('error');
        identificadorHelper.style.color = '#6c757d';
        return true;
    }

    /**
     * Muestra u oculta el campo de empleados según el tipo (Jurídica/Natural).
     */
    function toggleEmpleadosField() {
        if (!tipoSelect || !empleadosGroup) return;

        const selectedOption = tipoSelect.options[tipoSelect.selectedIndex];
        // Usamos el atributo data-tipo (o value) que contiene 'Jurídica' o 'Natural'
        const tipoValor = selectedOption ? selectedOption.getAttribute('data-tipo') : '';
        
        if (tipoValor === 'Jurídica') {
            empleadosGroup.style.display = 'block';
            empleadosInput.setAttribute('required', 'required');
            if(empleadosInput.value === '0') empleadosInput.value = ''; 
        } else {
            empleadosGroup.style.display = 'none';
            empleadosInput.removeAttribute('required');
            // Lógica de Negocio: Si es Natural, se debe enviar 0 empleados.
            if (tipoValor === 'Natural') {
                 empleadosInput.value = '0'; 
            } else {
                empleadosInput.value = '';
            }
        }
    }

    // Event Listeners
    if (paisSelect) paisSelect.addEventListener('change', validateTributario);
    if (tipoSelect) tipoSelect.addEventListener('change', toggleEmpleadosField); // ID ACTUALIZADO
    if (identificadorInput) identificadorInput.addEventListener('input', validateTributario);

    // Initial check on load
    if (paisSelect && identificadorInput) validateTributario();
    if (tipoSelect) toggleEmpleadosField(); // ID ACTUALIZADO
    
    
    // 4. Form submission for create tributario (Validación Final)
    const createForm = document.getElementById('createContribuyenteForm');
    if (createForm) {
        createForm.addEventListener('submit', function(e) {
            let isValid = true;
            
            // 4.1. Pre-envío para Natural (Forzar 0 empleados)
            const selectedOption = tipoSelect.options[tipoSelect.selectedIndex];
            const tipoValor = selectedOption ? selectedOption.getAttribute('data-tipo') : '';
            if (tipoValor === 'Natural') {
                empleadosInput.value = '0'; 
            }
            
            // 4.2. Validación de campos requeridos
            const requiredFields = this.querySelectorAll('[required]');
            requiredFields.forEach(field => {
                // Solo validar el campo de empleados si tiene el atributo 'required' (es decir, si es Jurídica)
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('error');
                } else {
                    field.classList.remove('error');
                }
            });
            
            // 4.3. Validación de formato de Identificador
            if (isValid && identificadorInput && !validateTributario()) {
                isValid = false;
            }
            

            if (!isValid) {
                e.preventDefault();
                alert('Por favor completa todos los campos obligatorios y revisa el formato del identificador tributario.');
            }
        });
    }

    // 5. Delete confirmation (Se mantiene)
    const deleteButtons = document.querySelectorAll('.delete-btn');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('¿Estás seguro de que deseas eliminar este contribuyente? Esta acción es permanente.')) {
                e.preventDefault();
            }
        });
    });
});