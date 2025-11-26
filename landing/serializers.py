from rest_framework import serializers
from .models import Reserva, Contacto

class ReservaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reserva
        fields = ['id', 'nombre', 'email', 'destino', 'viajeros', 'mensaje', 'fecha_creacion']
        read_only_fields = ['id', 'fecha_creacion']

class ContactoSerializer(serializers.ModelSerializer):
            class Meta:
                model = Contacto
                fields = ['id', 'nombre', 'email', 'mensaje', 'categoria', 'fecha_creacion']
                read_only_fields = ['id', 'fecha_creacion', 'categoria']