document.addEventListener('DOMContentLoaded', function() {
    const selector = document.getElementById('filtroTipo');
    
    selector.addEventListener('change', function() {
        const filtro = this.value.toLowerCase(); 
        const eventos = document.querySelectorAll('.evento-item');

        eventos.forEach(item => {
            // Obtenemos el tipo del evento desde el atributo HTML (ya viene en minúscula por el template)
            const tipoEvento = item.getAttribute('data-tipo');

            // Lógica de visualización
            let mostrar = false;

            if (filtro === 'todos') {
                mostrar = true;
            } 
            // Filtro Usuarios: Busca 'usuario', pero también podrías agregar 'login' o 'logout'
            else if (filtro === 'usuario') {
                if (tipoEvento.includes('usuario') || tipoEvento.includes('login') || tipoEvento.includes('registro')) {
                    mostrar = true;
                }
            }
            // Filtro Contribuyentes: Busca cualquier evento que diga 'contribuyente'
            else if (filtro === 'contribuyente') {
                if (tipoEvento.includes('contribuyente')) {
                    mostrar = true;
                }
            } 
            // Filtro Clasificaciones: Busca 'clasificacion'
            else if (filtro === 'clasificacion') {
                if (tipoEvento.includes('clasificacion')) {
                    mostrar = true;
                }
            }

            // Aplicar el estilo display
            item.style.display = mostrar ? '' : 'none';
        });
    });
});