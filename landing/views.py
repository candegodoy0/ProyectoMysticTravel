from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.contrib import messages
from django.http import JsonResponse
import json
from django.urls import reverse
from .forms import ContactoForm, ReservaForm
from .models import Reserva, Contacto
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from rest_framework import viewsets
from .serializers import ReservaSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly

import smtplib
from email.mime.text import MIMEText
import ssl
from django.conf import settings




def es_admin(user):
    """verifica si el usuario esta activo y es admin"""
    return user.is_active and user.is_staff



def enviar_multiples_emails(emails_a_enviar):
    """
    establece una unica conexion con el servidor SMTP para enviar multiples mensajes,
    evitando la latencia de reabrir la conexion en cada email
    emails_a_enviar es una lista de diccionarios: [{'asunto':..., 'destinatario':..., 'html_content':...}]
    """
    if not emails_a_enviar:
        return

    try:
        context = ssl._create_unverified_context()
        with smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT, context=context) as server:
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)

            for email_data in emails_a_enviar:
                msg = MIMEText(email_data["html_content"], "html", "utf-8")
                msg["Subject"] = email_data["asunto"]
                msg["From"] = settings.EMAIL_HOST_USER
                msg["To"] = email_data["destinatario"]

                server.send_message(msg)

    except Exception as e:
        print(f"❌ Error al enviar emails: {e}")


# --- vistas de autenticacion y paneles ---

def registro(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '¡Registro exitoso! Ya puedes acceder a tu cuenta.')
            return redirect('landing:user_panel')  # redirigir al panel de usuario
    else:
        form = UserCreationForm()
    return render(request, 'landing/registro.html', {'form': form})


def iniciar_sesion(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"¡Bienvenido, {user.username}!")

            if user.is_staff:
                return redirect('landing:dashboard')
            else:
                return redirect('landing:user_panel')
        else:
            messages.error(request, 'Nombre de usuario o contraseña incorrectos.')
    else:
        form = AuthenticationForm()
    return render(request, 'landing/login.html', {'form': form})


# panel para administradores (protegido con is_staff)
@user_passes_test(es_admin, login_url='landing:login')
def dashboard(request):
    return render(request, 'landing/dashboard.html')


# panel para usuarios normales (protegido solo con login)
@login_required
def user_panel(request):
    return render(request, 'landing/user_panel.html')


def home(request):
    enviado = False
    nombre_contacto = ''
    form = ContactoForm()

    if request.method == 'POST':
        is_ajax = request.content_type == 'application/json'

        if is_ajax:
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({'success': False, 'errors': 'JSON inválido'}, status=400)
            form = ContactoForm(data)
        else:
            form = ContactoForm(request.POST)

        if form.is_valid():
            nombre = form.cleaned_data['nombre']
            email = form.cleaned_data['email']
            mensaje = form.cleaned_data['mensaje']

            Contacto.objects.create(nombre=nombre, email=email, mensaje=mensaje)

            emails = []

            # envio de emails admin
            html_admin = f"""
            <div style="background:#f5f5f5;padding:20px;">
                <div style="background:white;padding:20px;border-radius:8px;">
                    <h2 style="color:#333;">Nuevo mensaje de contacto</h2>
                    <p><strong>Nombre:</strong> {nombre}</p>
                    <p><strong>Email:</strong> {email}</p>
                    <p><strong>Mensaje:</strong></p>
                    <p>{mensaje}</p>
                </div>
            </div>
            """
            emails.append({
                'asunto': f"Nuevo contacto | Mystic Travel - {nombre}",
                'destinatario': "candela.godoy@lalupitacontenidos.site",
                'html_content': html_admin
            })

            # envio de mails usuario
            html_user = f"""
            <div style="background:#f5f5f5;padding:20px;">
                <div style="background:white;padding:20px;border-radius:8px;">
                    <h2 style="color:#333;">¡Hola {nombre}!</h2>
                    <p>Gracias por ponerte en contacto con <strong>Mystic Travel</strong>.</p>
                    <p>Hemos recibido tu mensaje y te responderemos pronto.</p>
                    <p style="margin-top:20px;">Saludos,<br>Mystic Travel</p>
                </div>
            </div>
            """
            emails.append({
                'asunto': "Confirmación de contacto | Mystic Travel",
                'destinatario': email,
                'html_content': html_user
            })

            enviar_multiples_emails(emails)

            messages.success(request, '¡Gracias por tu mensaje! Te responderemos pronto.')
            nombre_contacto = nombre

            if is_ajax:
                return JsonResponse({'success': True, 'nombre': nombre})

            enviado = True
            form = ContactoForm()

            return redirect('landing:home')


        else:
            if is_ajax:
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    return render(request, 'landing/home.html', {
        'form': form,
        'enviado': enviado,
        'nombre_contacto': nombre_contacto
    })


def galeria(request):
    destinos = [
        {'nombre': 'Islandia', 'slug': 'islandia', 'imagenes_count': 6},
        {'nombre': 'Dubái', 'slug': 'dubai', 'imagenes_count': 7},
        {'nombre': 'Egipto', 'slug': 'egipto', 'imagenes_count': 7},
        {'nombre': 'India', 'slug': 'india', 'imagenes_count': 6},
        {'nombre': 'Indonesia', 'slug': 'indonesia', 'imagenes_count': 7},
        {'nombre': 'Marruecos', 'slug': 'marruecos', 'imagenes_count': 5},
        {'nombre': 'Tailandia', 'slug': 'tailandia', 'imagenes_count': 7},
    ]
    return render(request, 'landing/galeria.html', {'destinos': destinos})


def galeria_destino(request, destino):
    destinos_data = {
        'islandia': {'imagenes': 6, 'desc': 'Tierra de fuego y hielo...'},
        'dubai': {'imagenes': 7, 'desc': 'Un oasis de lujo en el desierto...'},
        'egipto': {'imagenes': 7, 'desc': 'Viaje a la cuna de la civilización...'},
        'india': {'imagenes': 6, 'desc': 'Un caleidoscopio de cultura y espiritualidad...'},
        'indonesia': {'imagenes': 7, 'desc': 'Playas paradisíacas y selvas frondosas...'},
        'marruecos': {'imagenes': 5, 'desc': 'Un mundo de zocos vibrantes...'},
        'tailandia': {'imagenes': 7, 'desc': 'Templos dorados y playas exóticas...'},
    }

    if destino not in destinos_data:
        return render(request, 'landing/404.html')

    data = destinos_data[destino]
    imagenes_range = range(1, data['imagenes'] + 1)

    return render(request, 'landing/galeria_destino.html', {
        'imagenes_range': imagenes_range,
        'destino': destino,
        'descripcion': data['desc']
    })


def info(request):
    return render(request, 'landing/info.html')


def reservas(request):
    enviado = False
    nombre = ''

    if request.method == 'POST':
        form = ReservaForm(request.POST)

        if form.is_valid():
            # crear la reserva
            reserva = Reserva.objects.create(
                nombre=form.cleaned_data['nombre'],
                email=form.cleaned_data['email'],
                destino=form.cleaned_data['destino'],
                viajeros=form.cleaned_data['viajeros'],
                mensaje=form.cleaned_data['mensaje'],
            )

            emails = []

            # envio de emails admin
            html_admin = f"""
            <div style="background:#f5f5f5;padding:20px;">
                <div style="background:white;padding:20px;border-radius:8px;">
                    <h2 style="color:#333;">Nueva solicitud de reserva</h2>
                    <p><strong>Nombre:</strong> {reserva.nombre}</p>
                    <p><strong>Correo:</strong> {reserva.email}</p>
                    <p><strong>Destino:</strong> {reserva.destino}</p>
                    <p><strong>Viajeros:</strong> {reserva.viajeros}</p>
                    <p><strong>Mensaje:</strong></p>
                    <p>{reserva.mensaje}</p>
                </div>
            </div>
            """
            emails.append({
                'asunto': f"Nueva reserva | {reserva.destino} - {reserva.nombre}",
                'destinatario': "candela.godoy@lalupitacontenidos.site",
                'html_content': html_admin
            })

            # envio de email usuario
            html_user = f"""
            <div style="background:#f5f5f5;padding:20px;">
                <div style="background:white;padding:20px;border-radius:8px;">
                    <h2 style="color:#333;">¡Gracias {reserva.nombre}!</h2>
                    <p>Recibimos tu solicitud de reserva para <strong>{reserva.destino}</strong>.</p>
                    <p>Nos pondremos en contacto a la brevedad.</p>
                     <p>Saludos,</p>
                     <p>El Equipo de Mystic Travel</p>

                </div>
            </div>
            """
            emails.append({
                'asunto': "Confirmación de reserva | Mystic Travel",
                'destinatario': reserva.email,
                'html_content': html_user
            })

            enviar_multiples_emails(emails)

            messages.success(request, f"¡Reserva para {reserva.destino} creada con éxito!")

            return redirect('landing:reservas')

    else:
        form = ReservaForm()

    return render(request, 'landing/reservas.html', {
        'form': form,
        'enviado': enviado,
        'nombre': nombre
    })


# vistas protegidas para admin
@user_passes_test(es_admin, login_url='landing:login')
def listado_reservas(request):
    reservas = Reserva.objects.all().order_by('-fecha_creacion')
    return render(request, 'landing/listado_reservas.html', {'reservas': reservas})


@user_passes_test(es_admin, login_url='landing:login')
def reserva_detalle(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    return render(request, 'landing/reserva_detalle.html', {'reserva': reserva})


@user_passes_test(es_admin, login_url='landing:login')
def reserva_editar(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    is_ajax = request.content_type == 'application/json'

    if request.method == 'POST':
        data = json.loads(request.body) if is_ajax else request.POST
        form = ReservaForm(data)
        if form.is_valid():
            reserva.nombre = form.cleaned_data['nombre']
            reserva.email = form.cleaned_data['email']
            reserva.destino = form.cleaned_data['destino']
            reserva.viajeros = form.cleaned_data['viajeros']
            reserva.mensaje = form.cleaned_data['mensaje']
            reserva.save()

            if is_ajax:
                return JsonResponse(
                    {'success': True, 'redirect_url': reverse('landing:reserva_detalle', args=[reserva.pk])})

            messages.success(request, "Reserva actualizada con éxito.")
            return redirect('landing:reserva_detalle', pk=reserva.pk)

        else:
            if is_ajax:
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    form = ReservaForm(initial={
        'nombre': reserva.nombre,
        'email': reserva.email,
        'destino': reserva.destino,
        'viajeros': reserva.viajeros,
        'mensaje': reserva.mensaje
    })

    return render(request, 'landing/reserva_editar.html', {'form': form, 'reserva': reserva})


@user_passes_test(es_admin, login_url='landing:login')
def reserva_eliminar(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    is_ajax = request.content_type == 'application/json'

    if request.method == 'POST':
        nombre_eliminado = reserva.nombre
        reserva.delete()

        if is_ajax:
            return JsonResponse({'success': True, 'redirect_url': reverse('landing:listado_reservas')})

        messages.success(request, f"La reserva de {nombre_eliminado} fue eliminada.")
        return redirect('landing:listado_reservas')

    return render(request, 'landing/reserva_confirm_delete.html', {'reserva': reserva})


class ReservaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Reserva.objects.all().order_by('-fecha_creacion')
    serializer_class = ReservaSerializer


from rest_framework.routers import DefaultRouter

router = DefaultRouter()