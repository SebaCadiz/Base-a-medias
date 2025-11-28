/* tipo_tributo.js
   Populates the tipo_de_tributo field with sensible options and adds helper UI.
*/

document.addEventListener('DOMContentLoaded', function () {
    // Try to find an existing element named 'tipo_de_tributo'
    let existing = document.querySelector('[name="tipo_de_tributo"]');

    // If there's already a <select> we keep it; if it's an <input> we replace with <select>
    let selectEl = null;
    if (existing && existing.tagName.toLowerCase() === 'select') {
        selectEl = existing;
    } else {
        // Create a select and copy value if input
        selectEl = document.createElement('select');
        selectEl.name = 'tipo_de_tributo';
        selectEl.id = 'tipo_de_tributo';
        selectEl.className = existing ? existing.className : '';

        if (existing) {
            const current = existing.value || '';
            existing.replaceWith(selectEl);
            selectEl.dataset.initial = current;
        }
    }

    // Define a friendly ordered list of options
    const options = [
        {value: '', label: 'Seleccione un tipo...'},
        {value: 'Impuesto', label: 'Impuesto'},
        {value: 'Tasa', label: 'Tasa'},
        {value: 'Contribucion', label: 'Contribución'},
        {value: 'Otro', label: 'Otro (manual)'}
    ];

    // Avoid duplicating options on live-reload / hmr
    if (!selectEl._populated) {
        selectEl.innerHTML = ''; // clear
        options.forEach(opt => {
            const o = document.createElement('option');
            o.value = opt.value;
            o.textContent = opt.label;
            selectEl.appendChild(o);
        });
        selectEl._populated = true;

        // Preserve initial value when present (when editing)
        if (selectEl.dataset.initial) {
            selectEl.value = selectEl.dataset.initial;
        }

        // If the selected value isn't in list, append it so it stays selected
        if (selectEl.value && !Array.from(selectEl.options).some(o => o.value === selectEl.value)){
            const o = document.createElement('option');
            o.value = selectEl.value;
            o.textContent = selectEl.value;
            selectEl.appendChild(o);
            selectEl.value = selectEl.value;
        }
    }

    // Add a small helper message under the select
    let helper = document.getElementById('tipo-helper');
    if (!helper) {
        helper = document.createElement('div');
        helper.id = 'tipo-helper';
        helper.style.fontSize = '0.9rem';
        helper.style.color = '#666';
        helper.style.marginTop = '6px';
        selectEl.insertAdjacentElement('afterend', helper);
    }

    function updateHelper(value) {
        switch (value) {
            case 'Tasa':
                helper.textContent = 'Tasa: suele ser un porcentaje o tasa fija. Si eliges "Tasa" indica el valor en el campo monto (ej: 12 => 12%).';
                break;
            case 'Contribucion':
                helper.textContent = 'Contribución: monto aplicable a contribuciones. Puedes indicar el valor en el campo monto.';
                break;
            case 'Impuesto':
                helper.textContent = 'Impuesto: tributo general. Añade el detalle en el régimen o código CIIU si aplica.';
                break;
            case 'Otro':
                helper.textContent = 'Otro: escribe el tipo explicitamente en el campo (si hace falta) o indica más detalles en la sección Régimen.';
                break;
            default:
                helper.textContent = '';
        }
    }

    // Initialize helper for current value
    updateHelper(selectEl.value);

    // When changed, update helper and adjust input hints
    selectEl.addEventListener('change', function (e) {
        updateHelper(e.target.value);
        // Extra behavior: if 'Tasa' is selected, set monto step to 0.01 and placeholder
        const monto = document.querySelector('[name="monto"]');
        if (monto) {
            if (e.target.value === 'Tasa') {
                monto.placeholder = 'Ej: 12 (porcentaje)';
                monto.step = '0.01';
            } else {
                monto.placeholder = '';
                monto.step = '1';
            }
        }
    });

});
