document.addEventListener('DOMContentLoaded', function() {
    const editForm = document.getElementById('reserva-edit-form');
    const formContainer = document.querySelector('.reserva-form');

    if (editForm) {
        editForm.addEventListener('submit', function(e) {
            e.preventDefault();

            // se obtienen datos del formulario
            const formData = new FormData(editForm);
            const jsonData = {};
            formData.forEach((value, key) => {
                jsonData[key] = value;
            });

            // se obtiene la url de la vista
            const url = editForm.action;

            // obtener el token csrf para seguridad
            const csrfToken = jsonData['csrfmiddlewaretoken'];

            // realizar la peticion fetch/ajax
            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify(jsonData)
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(errorData => {
                        throw new Error(JSON.stringify(errorData));
                    });
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {

                    // mostrar mensaje de exito
                    const successMsg = document.createElement('div');
                    successMsg.className = 'mensaje-ok';
                    successMsg.textContent = '¡Reserva actualizada! Redirigiendo...';
                    formContainer.prepend(successMsg);

                    // redireccionar al detalle
                    setTimeout(() => {
                        window.location.href = data.redirect_url;
                    }, 1500);

                } else if (data.errors) {
                    // manejo de errores de validacion
                    alert('Error de validación: Por favor revisa los campos.');console.error('Errores de validación:', data.errors);
                }
            })
            .catch(error => {
                console.error('Error al modificar la reserva:', error);
                alert('Ocurrió un error al intentar guardar los cambios.');
            });
        });
    }
});
