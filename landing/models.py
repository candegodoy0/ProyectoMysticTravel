from django.db import models

# modelo para almacenar las reservas del formulario de reservas
class Reserva(models.Model):
    nombre = models.CharField(max_length=150)
    email = models.EmailField()
    destino = models.CharField(max_length=100)
    viajeros = models.IntegerField()
    mensaje = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reserva de {self.nombre} para {self.destino}"

# modelo para almacenar los mensajes del formulario de contacto (SOLICITUDES)
class Contacto(models.Model):
    nombre = models.CharField(max_length=150)
    email = models.EmailField()
    mensaje = models.TextField()
    categoria = models.CharField(max_length=50, blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Mensaje de Contacto de {self.nombre}"

class UsuarioPermitido(models.Model):
    #tabla de usuarios permitidos
    nombre = models.CharField(max_length=150, verbose_name="Nombre y Apellido")
    email = models.EmailField(unique=True)
    codigo_validacion = models.CharField(max_length=8, unique=True, verbose_name="Código de Validación")
    usuario_creado = models.BooleanField(default=False)

    def __str__(self):
        return f"Permitido: {self.nombre} ({self.email})"