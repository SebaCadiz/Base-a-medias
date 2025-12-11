// manejo.js — filtrado unificado para tabla o bloques
(function () {
    // Elementos principales
    const searchInput = document.getElementById('searchMail');
    const roleSelect = document.getElementById('filterRol');
    const clearBtn = document.getElementById('clearFilters');
    const table = document.getElementById('usuariosTable');
    const blocks = document.querySelectorAll('.usuario-block');

    // Utilidad: normalizar texto
    function normalize(s) {
        return (s || '').toString().trim().toLowerCase();
    }

    // Filtrado para tabla (si existe)
    function filterTableRows(q, role) {
        if (!table) return;
        const tbody = table.tBodies[0];
        if (!tbody) return;

        for (const row of Array.from(tbody.rows)) {
            const mailCell = row.querySelector('.cell-mail');
            const rolCell = row.querySelector('.cell-rol');

            const mailText = normalize(mailCell ? mailCell.textContent : row.textContent);
            const rolText = normalize(rolCell ? rolCell.textContent : '');

            const matchesMail = q === '' || mailText.indexOf(q) !== -1;
            const matchesRol = !role || role === 'all' || rolText.indexOf(role) !== -1;

            row.style.display = (matchesMail && matchesRol) ? '' : 'none';
        }
    }

    // Filtrado para bloques (tu layout actual)
    function filterBlocks(q, role) {
        if (!blocks || blocks.length === 0) return;

        blocks.forEach(block => {
            // El correo está dentro de <em> en tu template: (<em>{{ block.usuario.mail }}</em>)
            const mailEl = block.querySelector('em');
            const mailText = normalize(mailEl ? mailEl.textContent : block.textContent);

            // Si tienes rol dentro del bloque, podría estar en .user-rol u otro. Intentamos detectar.
            const rolEl = block.querySelector('.user-rol') || block.querySelector('[data-rol]');
            const rolText = normalize(rolEl ? rolEl.textContent : '');

            const matchesMail = q === '' || mailText.indexOf(q) !== -1;
            const matchesRol = !role || role === 'all' || rolText.indexOf(role) !== -1;

            block.style.display = (matchesMail && matchesRol) ? '' : 'none';
        });
    }

    // Función principal de filtrado (llama a la versión correspondiente)
    function filterAll() {
        const q = normalize(searchInput ? searchInput.value : '');
        const role = roleSelect ? roleSelect.value : 'all';

        filterTableRows(q, role);
        filterBlocks(q, role);
    }

    // Conectar eventos (si existen)
    if (searchInput) {
        searchInput.addEventListener('input', filterAll);
    }

    if (roleSelect) {
        roleSelect.addEventListener('change', filterAll);
    }

    if (clearBtn) {
        clearBtn.addEventListener('click', function () {
            if (searchInput) searchInput.value = '';
            if (roleSelect) roleSelect.value = 'all';
            filterAll();
            if (searchInput) searchInput.focus();
        });
    }

    // Inicializar al cargar (por si hay un valor prellenado)
    document.addEventListener('DOMContentLoaded', filterAll);
    // También correr una vez inmediatamente (por si el script se carga al final)
    filterAll();
})();
