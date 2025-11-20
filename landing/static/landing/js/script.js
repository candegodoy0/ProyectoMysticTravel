document.addEventListener('DOMContentLoaded', function() {

    // botones para cerrar mensajes
    document.querySelectorAll('.close-message').forEach(button => {
        button.addEventListener('click', () => {
            const messageItem = button.closest('li');
            if (messageItem) messageItem.style.display = 'none';
        });
    });

    const navToggle = document.querySelector('.nav-toggle');
    const nav = document.getElementById('main-navigation');

    if (navToggle && nav) {

        function toggleNav() {
            const isOpen = nav.classList.toggle('nav-open');

            navToggle.setAttribute('aria-expanded', isOpen);

            navToggle.querySelector('i').className =
                isOpen ? 'fas fa-times' : 'fas fa-bars';

            if (isOpen) {
                document.body.classList.add('no-scroll');
            } else {
                document.body.classList.remove('no-scroll');
            }
        }

        navToggle.addEventListener('click', toggleNav);

        // cierra el menu en moviles al hacer clic en un enlace
        document.querySelectorAll('.nav-links a, .nav-links button').forEach(link => {
            link.addEventListener('click', () => {
                if (window.innerWidth <= 992 && nav.classList.contains('nav-open')) {
                    toggleNav();
                }
            });
        });
    }

    const reservaForm = document.getElementById('reserva-form');
    const submitButton = document.getElementById('btn-reserva-submit');
    const loadingMessage = document.getElementById('mensaje-enviando');

    if (reservaForm && submitButton && loadingMessage) {
        reservaForm.addEventListener('submit', function(event) {

            // antes de enviar, verifica que el boton no este ya deshabilitado
            if (submitButton.disabled) {
                // si ya esta deshabilitado, previene el reenvio
                event.preventDefault();
                return;
            }

            // deshabilitar el botón y cambiar su texto
            submitButton.disabled = true;
            submitButton.textContent = 'PROCESANDO SOLICITUD...';

            // mostrar el mensaje de enviando
            loadingMessage.style.display = 'block';

        });
    }
});