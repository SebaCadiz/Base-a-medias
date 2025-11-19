// Obtener los elementos del DOM usando sus IDs
// El modal entero (el overlay gris)
const modal = document.getElementById("registerModal"); 
// El botón "Register" del formulario de login
const openBtn = document.getElementById("openRegisterModal"); 
// El botón de cerrar 'x' dentro del modal
const closeBtn = document.querySelector(".close-button"); 

// --- FUNCIONES ---

// Función para abrir el modal
function openModal() {
    // Cambia la propiedad CSS de 'display: none' a 'display: flex' (lo hace visible)
    modal.style.display = "flex"; 
}

// Función para cerrar el modal
function closeModal() {
    // Vuelve a ocultar el modal
    modal.style.display = "none";
}

// --- ASIGNACIÓN DE EVENTOS ---

// 1. Abre el modal cuando se hace clic en el botón "Register"
openBtn.addEventListener('click', openModal);

// 2. Cierra el modal cuando se hace clic en el botón 'x'
closeBtn.addEventListener('click', closeModal);

// 3. Opcional: Cierra el modal cuando el usuario hace clic en el fondo oscuro (fuera de la ventana principal)
window.addEventListener('click', (event) => {
    // Si el elemento clickeado es el modal mismo (el fondo)
    if (event.target === modal) {
        closeModal();
    }
});

// Obtener los elementos del dropdown
const rolDropdownBtn = document.getElementById('rolDropdownBtn');
const rolDropdownContent = document.getElementById('rolDropdownContent');
const rolOptions = document.querySelectorAll('.rol-option'); // Todas las opciones de rol

// 1. Función para mostrar/ocultar rol
function toggleRolDropdown() {
    // Si está visible ('block'), lo oculta; si está oculto ('none'), lo muestra.
    if (rolDropdownContent.style.display === "block") {
        rolDropdownContent.style.display = "none";
    } else {
        rolDropdownContent.style.display = "block";
    }
}

// 2. Asignar el evento al botón principal
rolDropdownBtn.addEventListener('click', toggleRolDropdown);

// 3. Opcional: Cerrar el dropdown cuando se hace click en una opción
rolOptions.forEach(option => {
    option.addEventListener('click', () => {
        // Obtenemos el texto de la opción clickeada
        const label = option.querySelector('label').textContent;
        
        // Actualizamos el texto del botón principal con la opción seleccionada
        rolDropdownBtn.textContent = label;
        
        // Ocultamos el dropdown
        rolDropdownContent.style.display = "none";
    });
});

// 4. Opcional: Cerrar el dropdown si se hace click fuera
window.addEventListener('click', function(event) {
    if (!event.target.matches('#rolDropdownBtn')) {
        if (rolDropdownContent.style.display === "block") {
            rolDropdownContent.style.display = "none";
        }
    }
});
