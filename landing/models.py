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

# modelo para almacenar los mensajes del formulario de contacto
class Contacto(models.Model):
    nombre = models.CharField(max_length=150)
    email = models.EmailField()
    mensaje = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"Mensaje de Contacto de {self.nombre}"