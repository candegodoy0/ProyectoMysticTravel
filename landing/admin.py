from django.contrib import admin
from .models import Reserva, Contacto

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


from django.contrib import admin

# Register your models here.
