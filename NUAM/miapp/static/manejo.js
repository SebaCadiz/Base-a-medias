// Script de filtrado para `manejo_usuario.html`
(function(){
	const searchInput = document.getElementById('searchMail');
	const roleSelect = document.getElementById('filterRol');
	const clearBtn = document.getElementById('clearFilters');
	const table = document.getElementById('usuariosTable');
	if(!table) return; // seguridad si la página no contiene la tabla
	const tbody = table.tBodies[0];

	function normalize(s){
		return (s||'').toString().trim().toLowerCase();
	}

	function filterRows(){
		const q = normalize(searchInput ? searchInput.value : '');
		const role = roleSelect ? roleSelect.value : 'all';

		for(const row of Array.from(tbody.rows)){
			const mailCell = row.querySelector('.cell-mail');
			const rolCell = row.querySelector('.cell-rol');
			const mailText = normalize(mailCell ? mailCell.textContent : '');
			const rolText = normalize(rolCell ? rolCell.textContent : '');

			const matchesMail = q === '' || mailText.indexOf(q) !== -1;
			const matchesRol = role === 'all' || rolText.indexOf(role) !== -1;

			row.style.display = (matchesMail && matchesRol) ? '' : 'none';
		}
	}

	if(searchInput) searchInput.addEventListener('input', filterRows);
	if(roleSelect) roleSelect.addEventListener('change', filterRows);
	if(clearBtn) clearBtn.addEventListener('click', function(){ if(searchInput) searchInput.value=''; if(roleSelect) roleSelect.value='all'; filterRows(); if(searchInput) searchInput.focus(); });

	// Inicializar filtrado
	filterRows();
})();

