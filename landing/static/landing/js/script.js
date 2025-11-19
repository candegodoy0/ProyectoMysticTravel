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
});
