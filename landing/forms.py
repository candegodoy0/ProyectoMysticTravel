import re

from django import forms
from django.core.exceptions import ValidationError

# lista de destinos
DESTINO_CHOICES = (
    ('', 'Selecciona un destino...'),
    ('Islandia', 'Islandia'),
    ('Dubai', 'Dubai'),
    ('Egipto', 'Egipto'),
    ('India', 'India'),
    ('Indonesia', 'Indonesia'),
    ('Marruecos', 'Marruecos'),
    ('Tailandia', 'Tailandia'), # Agregado Tailandia
)


# formulario de reservas
class ReservaForm(forms.Form):
    nombre = forms.CharField(
        label='Nombre Completo:',
        widget=forms.TextInput(attrs={'placeholder': 'Ej. Maria Pérez'}),
        error_messages={'required': 'Por favor, ingresa tu nombre completo.'}
    )

    email = forms.EmailField(
        label='Correo Electrónico:',
        widget=forms.EmailInput(attrs={'placeholder': 'ejemplo@correo.com'}),
        error_messages={
            'required': 'El email es obligatorio.',
            'invalid': 'Introduce una dirección de correo electrónico válida.'
        }
    )

    destino = forms.ChoiceField(
        label='Destino de Interés:',
        choices=DESTINO_CHOICES,
        error_messages={
            'required': 'Por favor, selecciona un destino de la lista.',
        }
    )

    viajeros = forms.IntegerField(
        label='Cantidad de Viajeros:',
        widget=forms.NumberInput(attrs={'placeholder': 'Ej. 5'}),
        error_messages={
            'required': 'Este campo es obligatorio.',
            'invalid': 'Por favor, introduce solo números (cantidad de personas).'
        }
    )

    mensaje = forms.CharField(
        label='Mensaje Adicional o Fechas Estimadas:',
        widget=forms.Textarea(attrs={'rows': 4}),
        required=False
    )

    # validacion personalizada, solo letras y espacios en el nombre
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        # EL patron que usas es correcto, maneja acentos y Ñ/ñ
        patron_letras_espacios = r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$'

        if nombre and not re.match(patron_letras_espacios, nombre):
            raise forms.ValidationError('El nombre solo debe contener letras y espacios.')

        return nombre

    # validacion personalizada, cantidad de viajeros debe ser positiva
    def clean_viajeros(self):
        viajeros = self.cleaned_data.get('viajeros')

        if viajeros is not None and viajeros <= 0:
            raise forms.ValidationError('La cantidad de viajeros debe ser mayor a cero.')

        return viajeros


# formulario de contacto
class ContactoForm(forms.Form):
    nombre = forms.CharField(
        label='Tu Nombre:',
        widget=forms.TextInput(attrs={'placeholder': 'Ej. María López'}),
        error_messages={'required': 'Por favor, ingresa tu nombre.'}
    )

    email = forms.EmailField(
        label='Correo Electrónico:',
        widget=forms.EmailInput(attrs={'placeholder': 'ejemplo@correo.com'}),
        error_messages={
            'required': 'El email es obligatorio.',
            'invalid': 'Introduce un email válido.'
        }
    )

    mensaje = forms.CharField(
        label='Tu Mensaje:',
        widget=forms.Textarea(attrs={
            'placeholder': '¿En qué podemos ayudarte?',
            'rows': 4
        }),
        error_messages={'required': 'Por favor, escribe un mensaje.'}
    )

    # validacion personalizada, solo letras y espacios en el nombre
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        patron_letras_espacios = r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$'

        if nombre and not re.match(patron_letras_espacios, nombre):
            raise forms.ValidationError('El nombre solo debe contener letras y espacios.')

        return nombre