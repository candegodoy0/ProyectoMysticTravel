from django.contrib import admin
from .models import Reserva, Contacto, UsuarioPermitido

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email', 'destino', 'viajeros', 'fecha_creacion')
    list_filter = ('destino', 'fecha_creacion')
    search_fields = ('nombre', 'email', 'destino')

@admin.register(Contacto)
class ContactoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email', 'fecha_creacion')
    list_filter = ('fecha_creacion',)
    search_fields = ('nombre', 'email')

@admin.register(UsuarioPermitido)
class UsuarioPermitidoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email', 'usuario_creado')
    list_filter = ('usuario_creado',)
    search_fields = ('email', 'nombre')


# Register your models here.
