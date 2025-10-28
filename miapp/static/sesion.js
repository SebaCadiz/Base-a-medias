        var modal = document.getElementById("createUserModal");
        var btn = document.getElementById("openModalBtn");
        var span = document.getElementsByClassName("close-btn")[0];

        // Cuando el usuario hace clic en el botón, abre el modal
        btn.onclick = function() {
            modal.style.display = "block";
        }

        // Cuando el usuario hace clic en (x), cierra el modal
        span.onclick = function() {
            modal.style.display = "none";
        }

        // Cuando el usuario hace clic fuera del contenido del modal, lo cierra
        window.onclick = function(event) {
            if (event.target == modal) {
                modal.style.display = "none";
            }
        }