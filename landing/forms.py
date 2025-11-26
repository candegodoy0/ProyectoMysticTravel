import re

from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import Contacto, UsuarioPermitido

# lista de destinos
DESTINO_CHOICES = (
    ('', 'Selecciona un destino...'),
    ('Islandia', 'Islandia'),
    ('Dubai', 'Dubai'),
    ('Egipto', 'Egipto'),
    ('India', 'India'),
    ('Indonesia', 'Indonesia'),
    ('Marruecos', 'Marruecos'),
    ('Tailandia', 'Tailandia'),
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


class EmailValidacionForm(forms.Form):
    #formulario simple que solo contiene el campo de email
        email = forms.EmailField(
        label='Correo Electrónico',
        widget=forms.EmailInput(attrs={'placeholder': 'ejemplo@correo.com'}),
        error_messages={
            'required': 'El email es obligatorio.',
            'invalid': 'Introduce un email válido.'
        }
    )


# --- formulario de validacion de cuenta (solo codigo)
class CodigoValidacionForm(forms.Form):
    codigo = forms.CharField(
        label='Código de Validación',
        max_length=8,
        widget=forms.TextInput(attrs={'placeholder': 'Ingrese el código de 8 dígitos'}),
        error_messages={'required': 'Debe ingresar el código de validación.'}
    )


# --- formulario para edicion de contacto
class ContactoEditForm(ModelForm):


    class Meta:
        model = Contacto
        fields = ['nombre', 'email', 'mensaje', 'categoria']
        labels = {
            'categoria': 'Clasificación de la Solicitud',
            'mensaje': 'Mensaje Completo',
        }
        widgets = {
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'mensaje': forms.Textarea(attrs={'rows': 5}),
        }

class RegistroCompletoForm(UserCreationForm):

    username = forms.EmailField(
        label='Correo Electrónico',
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'annavillegas@live.com.ar'}),
        help_text=''
    )

    nombre = forms.CharField(
        label='Nombre',
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Ej. Ana'}),
        error_messages={'required': 'El nombre es obligatorio.'}
    )
    apellido = forms.CharField(
        label='Apellido',
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Ej. Villegas'}),
        error_messages={'required': 'El apellido es obligatorio.'}
    )

    class Meta(UserCreationForm.Meta):
        # el username se convierte en el email del usuario
        fields = ('username', 'nombre', 'apellido',) + UserCreationForm.Meta.fields[3:]

    def _init_(self, *args, **kwargs):
        super()._init_(*args, **kwargs)
        self.fields['password2'].label = 'Confirmar Contraseña'

    def clean_username(self):
        # se aplica validacion de email al campo que se esta usando como username
        email = self.cleaned_data.get('username')
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise forms.ValidationError('Introduce una dirección de correo electrónico válida.')
        return email