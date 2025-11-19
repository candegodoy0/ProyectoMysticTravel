document.addEventListener('DOMContentLoaded', function() {
    const deleteForm = document.getElementById('reserva-delete-form');

    if (deleteForm) {
        deleteForm.addEventListener('submit', function(e) {
            e.preventDefault();

            if (!confirm("¿Estás realmente seguro de eliminar esta reserva? Esta acción es irreversible.")) {
                return;
            }

            // se obtiene datos y url
            const url = deleteForm.action;
            const csrfToken = deleteForm.querySelector('[name="csrfmiddlewaretoken"]').value;

            // se realiza la peticion fetch/ajax
            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                // el cuerpo puede estar vacio o llevar un indicador de eliminacion
                body: JSON.stringify({ action: 'delete' })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {

                    // manejo del exito
                    alert(`¡Reserva de ${data.nombre_eliminado} eliminada correctamente!`);

                    // redirigir al listado
                    window.location.href = data.redirect_url;
                } else {
                    // manejo del error
                    alert('Error al intentar eliminar la reserva.');
                    console.error('Error del servidor:', data.error || 'Eliminación fallida.');
                }
            })
            .catch(error => {
                console.error('Error de conexión:', error);
                alert('Ocurrió un error de red al intentar eliminar.');
            });
        });
    }
});
