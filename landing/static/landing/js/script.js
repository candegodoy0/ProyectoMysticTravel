document.addEventListener('DOMContentLoaded', function() {

    document.querySelectorAll('.close-message').forEach(button => {
        button.addEventListener('click', () => {
            const messageItem = button.closest('.alert-box');
            if (messageItem) {
                messageItem.style.display = 'none'; // deshabilita la visualizacion
            }
        });
    });

    // menu hamburguesa
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


    // envio formuario reserva (deshabilita el boton al hacer submit)
    const reservaForm = document.getElementById('reserva-form');
    const submitReservaButton = document.getElementById('btn-reserva-submit');
    const mensajeEnviando = document.getElementById('mensaje-enviando');

    if (reservaForm && submitReservaButton) {
        reservaForm.addEventListener('submit', function(event) {

            if (!submitReservaButton.disabled) {
                // deshabilita el boton
                submitReservaButton.disabled = true;

                // se oculta el boton principal
                submitReservaButton.style.display = 'none';


                if (mensajeEnviando) {
                    mensajeEnviando.style.display = 'block';
                    mensajeEnviando.querySelector('p').textContent = 'PROCESANDO SOLICITUD...';
                }

            }
        });
    }

    // envio de formulario de ocntacto (deshabilita el boton al hacer submit)
    const contactoForm = document.getElementById('contacto-form');
    const submitContactoButton = document.getElementById('btn-contacto-submit');

    if (contactoForm && submitContactoButton) {
        contactoForm.addEventListener('submit', function(event) {
            // verifica si el boton ya esta deshabilitado para evitar reenvio
            if (submitContactoButton.disabled) {
                event.preventDefault();
                return;
            }
            // deshabilita y cambia texto
            submitContactoButton.disabled = true;
            submitContactoButton.textContent = 'ENVIANDO MENSAJE...';
        });
    }

});