from django.db import models


# modelo para almacenar las reservas del formulario de reservas
class Reserva(models.Model):
    nombre = models.CharField(max_length=150)
    email = models.EmailField()
    destino = models.CharField(max_length=100)
    viajeros = models.IntegerField()
    mensaje = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"Reserva de {self.nombre} para {self.destino}"


# modelo para almacenar los mensajes del formulario de contacto (SOLICITUDES)
class Contacto(models.Model):
    nombre = models.CharField(max_length=150)
    email = models.EmailField()
    mensaje = models.TextField()
    categoria = models.CharField(max_length=50, blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"Mensaje de Contacto de {self.nombre}"


class UsuarioPermitido(models.Model):
    # tabla de usuarios permitidos
    nombre = models.CharField(max_length=150, verbose_name="Nombre y Apellido")
    email = models.EmailField(unique=True)
    codigo_validacion = models.CharField(max_length=8, unique=True, verbose_name="Código de Validación", null=True,
                                         blank=True)
    usuario_creado = models.BooleanField(default=False)
    debe_ser_staff = models.BooleanField(default=False, verbose_name="¿Debe ser Staff al registrarse?")

    class Meta:
        verbose_name = "Usuario Permitido"
        verbose_name_plural = "Usuarios Permitidos"

    def _str_(self):
        return f"Permitido: {self.nombre} ({self.email})"

#modelo para editar contenido de forma autonoma

class ContenidoPagina(models.Model):

        # se asegura que solo haya una fila de contenido a editar
        seccion_id = models.IntegerField(unique=True, default=1, editable=False)

        # modificar el titulo
        titulo_principal = models.CharField(
            max_length=200,
            verbose_name="Título del Héroe (Banner Principal)",
        )

        # moodificar una seccion de la pagina
        cuerpo_seccion = models.TextField(
            verbose_name="Cuerpo de la Sección 'Acerca de Nosotros'",
        )

        ultima_modificacion = models.DateTimeField(auto_now=True)

        class Meta:
            verbose_name = "Contenido del CMS"
            verbose_name_plural = "Contenidos del CMS"

        def __str__(self):
            return self.titulo_principal