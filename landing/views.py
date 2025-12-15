from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
import json
import requests
import random
from rest_framework import viewsets
from rest_framework.routers import DefaultRouter
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Reserva, Contacto, UsuarioPermitido, ContenidoPagina
from .serializers import ReservaSerializer, ContactoSerializer
from .forms import RegistroCompletoForm, EmailValidacionForm, CodigoValidacionForm, ContactoForm, ReservaForm, \
    ContactoEditForm
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl
from django.conf import settings
from django.db.models import Count
from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse_lazy

def es_admin(user):
    return user.is_active and user.is_staff


def enviar_multiples_emails(emails_a_enviar):
    if not emails_a_enviar:
        return

    try:

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT, context=context, timeout=10) as server:

            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)

            for email_data in emails_a_enviar:
                msg = MIMEMultipart('alternative')
                msg["Subject"] = email_data["asunto"]
                msg["From"] = settings.EMAIL_HOST_USER
                msg["To"] = email_data["destinatario"]

                text_content = email_data["html_content"].replace('<p>', '\n').replace('</p>', '').replace('<h2>',
                                                                                                           '\n').replace(
                    '</h2>', '')

                part1 = MIMEText(text_content, 'plain', "utf-8")
                part2 = MIMEText(email_data["html_content"], 'html', "utf-8")

                msg.attach(part1)
                msg.attach(part2)

                server.sendmail(
                    settings.EMAIL_HOST_USER,
                    email_data["destinatario"],
                    msg.as_string()
                )

    except Exception as e:
        print(f"ERROR DE ENVÍO DE EMAIL (TIMEOUT/FALLO): {e}")


# --- vistas de autenticacion y paneles ---

def registro_avanzado(request):
    if request.user.is_authenticated:
        return redirect('landing:dashboard')

    if request.method == 'POST':
        form = RegistroCompletoForm(request.POST)

        if form.is_valid():
            email_ingresado = form.cleaned_data.get('username')
            nombre_completo = f"{form.cleaned_data.get('nombre')} {form.cleaned_data.get('apellido')}"

            try:
                permitido = UsuarioPermitido.objects.get(email=email_ingresado)
            except UsuarioPermitido.DoesNotExist:
                messages.error(request, 'Acceso restringido. No estás autorizado a usar el sistema.')
                return render(request, 'landing/auth/registro.html', {'form': form})

            if permitido.usuario_creado:
                messages.warning(request, 'Este email ya fue registrado. Inicia sesión.')
                return render(request, 'landing/auth/registro.html', {'form': form})

            permitido.nombre = nombre_completo
            codigo_generado = ''.join(random.choices('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=8))
            permitido.codigo_validacion = codigo_generado
            permitido.save()

            validation_url = request.build_absolute_uri(
                reverse('landing:validar_cuenta')
            )

            asunto = "Validación de Cuenta - Mystic Travel"
            html_content = f"""
            <div style="padding:20px; text-align:center;">
                <h2>¡Hola {permitido.nombre}!</h2>
                <p>Usa este código para activar tu cuenta:</p>
                <h1 style="color:#007bff; background:#e9ecef; padding:10px; border-radius:5px; display:inline-block;">{permitido.codigo_validacion}</h1>
                <p>Haz clic para validar:</p>
                <a href="{validation_url}" style="background:#007bff; color:white; padding:10px 20px; text-decoration:none; border-radius:5px;">Validar Cuenta Ahora</a>
            </div>
            """

            emails_a_enviar = [{
                'asunto': asunto,
                'destinatario': permitido.email,
                'html_content': html_content
            }]

            if settings.DEBUG:
                enviar_multiples_emails(emails_a_enviar)

            user = form.save(commit=False)
            user.is_active = False
            user.first_name = form.cleaned_data.get('nombre')
            user.last_name = form.cleaned_data.get('apellido')
            user.save()

            messages.success(request, 'Te llegará un correo para validar tu cuenta. Revísalo.')
            return redirect('landing:validar_cuenta')

        pass
    else:
        form = RegistroCompletoForm()

    return render(request, 'landing/auth/registro.html', {'form': form})


def validar_cuenta(request):
    if request.user.is_authenticated:
        return redirect('landing:dashboard')

    email_form = EmailValidacionForm(request.POST or None)
    codigo_form = CodigoValidacionForm(request.POST or None)

    if request.method == 'POST':
        if email_form.is_valid() and codigo_form.is_valid():
            email = email_form.cleaned_data['email']
            codigo = codigo_form.cleaned_data['codigo']

            try:
                permitido = UsuarioPermitido.objects.get(email=email, codigo_validacion=codigo)
            except UsuarioPermitido.DoesNotExist:
                messages.error(request, 'El correo o el código de validación son incorrectos.')
                return redirect('landing:validar_cuenta')

            try:
                user = User.objects.get(username=email, is_active=False)
                user.is_active = True

                if permitido.debe_ser_staff:
                    user.is_staff = True

                user.save()

                permitido.usuario_creado = True
                permitido.codigo_validacion = None
                permitido.save()

                messages.success(request, 'Cuenta validada con éxito! Ya puedes iniciar sesión.')
                return redirect('landing:login')

            except User.DoesNotExist:
                messages.error(request, 'Error: El usuario asociado no fue encontrado. Intenta iniciar sesión.')
                return redirect('landing:login')
        else:
            messages.error(request, 'Revisa los campos ingresados.')

    return render(request, 'landing/auth/validar_cuenta.html', {
        'email_form': email_form,
        'codigo_form': codigo_form
    })


def iniciar_sesion_avanzado(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()

            if not user.is_active:
                messages.warning(request, 'Tu cuenta no ha sido validada. Revisa tu correo.')

                class SpanishAuthenticationForm(AuthenticationForm):
                    def _init_(self, *args, **kwargs):
                        super()._init_(*args, **kwargs)
                        self.fields['username'].label = 'Correo Electrónico'
                        self.fields['password'].label = 'Contraseña'

                form = SpanishAuthenticationForm(request, data=request.POST)
                return render(request, 'landing/auth/login.html', {'form': form})

            login(request, user)
            messages.success(request, f"¡Bienvenido, {user.username}!")

            return redirect('landing:dashboard')
        else:
            messages.error(request, 'Correo Electrónico o contraseña incorrectos.')
    else:
        class SpanishAuthenticationForm(AuthenticationForm):
            def _init_(self, *args, **kwargs):
                super()._init_(*args, **kwargs)
                self.fields['username'].label = 'Correo Electrónico'
                self.fields['password'].label = 'Contraseña'

        form = SpanishAuthenticationForm()
    return render(request, 'landing/auth/login.html', {'form': form})


@login_required
def dashboard(request):
    return render(request, 'landing/admin/dashboard.html')


@login_required
def user_panel(request):
    messages.info(request, "Sesión activa, redirigido a Dashboard.")
    return redirect('landing:dashboard')


def clasificar_mensaje(mensaje):
    mensaje_lower = mensaje.lower()

    comercial = ["precio", "costo", "tarifa", "compra"]
    tecnica = ["soporte", "error", "problema", "ayuda"]
    rrhh = ["trabajo", "cv", "empleo", "linkedin"]

    if any(keyword in mensaje_lower for keyword in comercial):
        return "Consulta Comercial"
    elif any(keyword in mensaje_lower for keyword in tecnica):
        return "Consulta Técnica"
    elif any(keyword in mensaje_lower for keyword in rrhh):
        return "Consulta de RRHH"
    else:
        return "Consulta General"


def home(request):
    enviado = False
    nombre_contacto = ''

    # recupera datos del formulario si hubo errores en una sesion anterior
    initial_data = request.session.pop('contacto_form_data', None)
    initial_errors = request.session.pop('contacto_form_errors', None)

    if initial_data:
        form = ContactoForm(initial_data)
        if not form.is_valid():
            form._errors = initial_errors if initial_errors else {}

    else:
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

            categoria = clasificar_mensaje(mensaje)

            Contacto.objects.create(
                nombre=nombre,
                email=email,
                mensaje=mensaje,
                categoria=categoria
            )

            emails = []

            # email para el administrador
            html_admin = f"""
            <div style="background:#f5f5f5;padding:20px;">
                <div style="background:white;padding:20px;border-radius:8px;">
                    <h2 style="color:#333;">Nueva Solicitud de Contacto</h2>
                    <p><strong>Nombre:</strong> {nombre}</p>
                    <p><strong>Email:</strong> {email}</p>
                    <p><strong>Clasificación:</strong> {categoria}</p>
                    <p><strong>Mensaje:</strong></p>
                    <p>{mensaje}</p>
                </div>
            </div>
            """
            emails.append({
                'asunto': f"Nuevo Contacto | Mystic Travel - {nombre}",
                'destinatario': "candela.godoy@lalupitacontenidos.site",
                'html_content': html_admin
            })

            # email para el usuario
            html_user = f"""
                            <div style="background:#f5f5f5;padding:20px;">
                                <div style="background:white;padding:20px;border-radius:8px;">

                                    <div style="text-align: center; padding-bottom: 20px;">
                                        <img src="https://proyectomystictravel.onrender.com/static/images/logo-email.png" 
                                             alt="Logo Mystic Travel" 
                                             style="max-width: 150px; height: auto; border: 0;">
                                    </div>

                                    <h2>¡Hola {nombre}!</h2>
                                    <p>Hemos recibido tu mensaje correctamente. Tu consulta fue clasificada como: <strong>{categoria}</strong>.</p>
                        <p>Nuestro equipo te responderá a la brevedad.</p>
                        <hr style="border: none; border-top: 1px solid #eee; margin: 15px 0;">
                        <p style="font-size: 0.9em; color: #666;">Detalles de tu mensaje:</p>
                        <blockquote style="margin: 0; padding-left: 10px; border-left: 2px solid #007bff; color: #555;">{mensaje}</blockquote>
                    </div>
                </div>
                """
            emails.append({
                'asunto': f"Confirmación de Contacto | Mystic Travel - {categoria}",
                'destinatario': email,
                'html_content': html_user
            })

            if settings.DEBUG:
                enviar_multiples_emails(emails)

            messages.success(request, '¡Gracias por tu mensaje! Te responderemos pronto.')
            nombre_contacto = nombre

            if is_ajax:
                return JsonResponse({'success': True, 'nombre': nombre})

            enviado = True
            form = ContactoForm()

            # redireccion al home con el hash para enfocarse en la seccion
            return redirect(reverse('landing:home') + '#contacto')


        else:  # si la validacion falla
            if is_ajax:
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)

            # guarad los datos y errores en la sesion para mostrarlos tras la redireccion
            request.session['contacto_form_data'] = request.POST.dict()
            request.session['contacto_form_errors'] = form.errors.get_json_data()

            for field, errors in form.errors.items():
                if field == 'nombre':
                    continue

                field_label = form.fields[field].label if form.fields[field].label else field.capitalize()

                for error in errors:
                    messages.error(request, f"Error en {field_label}: {error}")
                    break

            # redireccion al home para mostrar errores de sesion
            return redirect(reverse('landing:home') + '#contacto')

    try:
        contenido_cms = ContenidoPagina.objects.get(seccion_id=1)
    except ContenidoPagina.DoesNotExist:
        contenido_cms = None

    context = {
        'form': form,
        'enviado': enviado,
        'nombre_contacto': nombre_contacto,
        'hay_errores': bool(initial_errors),
        'contenido_cms': contenido_cms,
    }

    return render(request, 'landing/public/home.html', context)

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
    return render(request, 'landing/public/galeria.html', {'destinos': destinos})


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
        return render(request, 'landing/public/404.html')

    data = destinos_data[destino]
    imagenes_range = range(1, data['imagenes'] + 1)

    return render(request, 'landing/public/galeria_destino.html', {
        'imagenes_range': imagenes_range,
        'destino': destino,
        'descripcion': data['desc']
    })


def info(request):
    tasa_cambio = None
    api_error = False
    data_externa = None

    API_RATES_URL = "https://open.er-api.com/v6/latest/USD"

    try:
        response = requests.get(API_RATES_URL, timeout=15, verify=False)
        response.raise_for_status()
        data = response.json()

        if data.get('result') == 'success' and 'rates' in data:
            moneda_destino = 'EUR'
            tasa_eur = data['rates'].get(moneda_destino)

            if tasa_eur:
                tasa_cambio = {
                    'moneda_base': 'USD',
                    'moneda_destino': 'EUR',
                    'valor': round(tasa_eur, 3),
                    'actualizacion': data.get('time_last_update_utc', 'Desconocida')
                }

        if not tasa_cambio:
            api_error = True

    except requests.exceptions.RequestException as e:
        api_error = True
        print(f"Error al consumir la API externa (Tasas de Cambio): {e}")
        messages.error(request, "Error de conexión con el servicio de tasas de cambio.")

    API_COUNTRY_URL = "https://restcountries.com/v3.1/name/argentina"

    try:
        response_country = requests.get(API_COUNTRY_URL, timeout=15, verify=False)
        response_country.raise_for_status()
        country_data = response_country.json()

        if country_data and isinstance(country_data, list) and country_data[0]:
            country = country_data[0]

            idiomas = ', '.join(country.get('languages', {}).values())

            data_externa = {
                'pais': country.get('name', {}).get('common', 'Desconocido'),
                'capital': country.get('capital', ['Desconocida'])[0],
                'poblacion': f"{country.get('population', 0):,}".replace(',', '.'),
                'idiomas': idiomas,
                'moneda': list(country.get('currencies', {}).keys())[0] if country.get('currencies') else 'Desconocida'
            }

    except requests.exceptions.RequestException as e:
        print(f"Error al consumir la API externa (Datos de País): {e}")

    return render(request, 'landing/public/info.html', {
        'tasa_cambio': tasa_cambio,
        'api_error': api_error,
        'data_externa': data_externa,
    })


def reservas(request):
    enviado = False
    nombre = ''

    if request.method == 'POST':
        form = ReservaForm(request.POST)

        if form.is_valid():
            nombre = form.cleaned_data['nombre']
            email = form.cleaned_data['email']
            destino = form.cleaned_data['destino']
            viajeros = form.cleaned_data['viajeros']
            mensaje = form.cleaned_data['mensaje']

            try:
                reserva = form.save()

                emails = []

                # contenido del email para el admin
                html_admin = f"""
                <div style="background:#f5f5f5;padding:20px;">
                    <div style="background:white;padding:20px;border-radius:8px;">
                        <h2 style="color:#333;">NUEVA SOLICITUD DE RESERVA</h2>
                        <p><strong>Nombre:</strong> {nombre}</p>
                        <p><strong>Email:</strong> {email}</p>
                        <p><strong>Destino:</strong> {destino}</p>
                        <p><strong>Viajeros:</strong> {viajeros}</p>
                        <p><strong>Mensaje:</strong></p>
                        <p>{mensaje if mensaje else 'Sin mensaje adicional.'}</p>
                    </div>
                </div>
                """
                emails.append({
                    'asunto': f"NUEVA RESERVA | Mystic Travel - {nombre}",
                    'destinatario': "candela.godoy@lalupitacontenidos.site",
                    'html_content': html_admin
                })

                # contenid del email para el usuario
                html_user = f"""
                                <div style="background:#f5f5f5;padding:20px;">
                                    <div style="background:white;padding:20px;border-radius:8px;">

                                        <div style="text-align: center; padding-bottom: 20px;">
                                            <img src="https://proyectomystictravel.onrender.com/static/images/logo-email.png" 
                                                 alt="Logo Mystic Travel" 
                                                 style="max-width: 150px; height: auto; border: 0;">
                                        </div>

                                        <h2>¡Hola {nombre}!</h2>
                                        <p>¡Tu aventura ha comenzado! Recibimos tu solicitud de reserva para {destino}.</p>
                                        <p>Nuestro equipo te contactará en breve para finalizar los detalles.</p>
                                        <p style="margin-top:20px; font-size: 0.8em; color: #666;">Detalles: {viajeros} viajeros.</p>
                                    </div>
                                </div>
                                """
                emails.append({
                    'asunto': f"Confirmación de Reserva | Mystic Travel - {destino}",
                    'destinatario': email,
                    'html_content': html_user
                })

                if settings.DEBUG:
                    enviar_multiples_emails(emails)

                messages.success(request, f"¡Gracias por tu interés, {nombre}! Tu solicitud fue enviada con éxito.")

                return redirect('landing:reservas')

            except Exception as e:
                print("====================================")
                print("  !!! ERROR CRÍTICO AL PROCESAR RESERVA !!! ")

                print(f"Tipo de Error: {e.__class__.__name__}")
                print(f"Mensaje: {e}")
                print("====================================")

                messages.error(request, "Error interno al procesar la reserva. Revisar la consola del servidor.")
                return redirect('landing:reservas')

        else:
            messages.error(request, "Por favor, corrige los errores del formulario.")
            form = ReservaForm(request.POST)

    else:
        form = ReservaForm()

    return render(request, 'landing/public/reservas.html', {
        'form': form,
        'enviado': enviado,
        'nombre': nombre
    })


# --- vistas protegidas para staff (reservas) ---
@user_passes_test(es_admin, login_url='landing:login')
def listado_reservas(request):
    reservas = Reserva.objects.all().order_by('-fecha_creacion')
    return render(request, 'landing/admin/listado_reservas.html', {'reservas': reservas})


@user_passes_test(es_admin, login_url='landing:login')
def reserva_detalle(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    return render(request, 'landing/admin/reserva_detalle.html', {'reserva': reserva})


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

    return render(request, 'landing/admin/reserva_editar.html', {'form': form, 'reserva': reserva})


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

    return render(request, 'landing/admin/reserva_confirm_delete.html', {'reserva': reserva})


# --- vistas protegidas para staff (solicitudes / contacto) ---
@user_passes_test(es_admin, login_url='landing:login')
def listado_solicitudes(request):
    solicitudes = Contacto.objects.all().order_by('-fecha_creacion')
    total_solicitudes = solicitudes.count()

    estadisticas_por_categoria_queryset = Contacto.objects \
        .values('categoria') \
        .annotate(total=Count('categoria')) \
        .order_by('-total')

    estadisticas_corregidas = []
    for item in estadisticas_por_categoria_queryset:
        if item['categoria'] is None:
            item['categoria'] = 'Consulta General'
        estadisticas_corregidas.append(item)

    context = {
        'solicitudes': solicitudes,
        'total_solicitudes': total_solicitudes,
        'estadisticas_por_categoria': estadisticas_corregidas,
    }
    return render(request, 'landing/admin/listado_solicitudes.html', context)


@user_passes_test(es_admin, login_url='landing:login')
def solicitud_detalle(request, pk):
    solicitud = get_object_or_404(Contacto, pk=pk)
    return render(request, 'landing/admin/solicitud_detalle.html', {'solicitud': solicitud})


@user_passes_test(es_admin, login_url='landing:login')
def solicitud_editar(request, pk):
    solicitud = get_object_or_404(Contacto, pk=pk)

    if request.method == 'POST':
        form = ContactoEditForm(request.POST, instance=solicitud)
        if form.is_valid():
            form.save()
            messages.success(request, f"La solicitud #{pk} fue actualizada con éxito.")
            return redirect('landing:solicitud_detalle', pk=pk)
        else:
            messages.error(request, "Error al editar la solicitud. Revisa los campos.")
    else:
        form = ContactoEditForm(instance=solicitud)

    return render(request, 'landing/admin/solicitud_editar.html', {'form': form, 'solicitud': solicitud})


@user_passes_test(es_admin, login_url='landing:login')
def solicitud_eliminar(request, pk):
    solicitud = get_object_or_404(Contacto, pk=pk)

    if request.method == 'POST':
        nombre = solicitud.nombre
        solicitud.delete()
        messages.success(request, f"La solicitud #{pk} de {nombre} fue eliminada.")
        return redirect('landing:listado_solicitudes')

    return render(request, 'landing/admin/solicitud_confirm_delete.html', {'solicitud': solicitud})


# --- vistas de api rest framework ---

class ReservaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Reserva.objects.all().order_by('-fecha_creacion')
    serializer_class = ReservaSerializer


class ContactoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Contacto.objects.all().order_by('-fecha_creacion')
    serializer_class = ContactoSerializer
    http_method_names = ['get']


router = DefaultRouter()
router.register(r'reservas', ReservaViewSet)
router.register(r'contactos', ContactoViewSet)


class CMSContenidoUpdateView(UserPassesTestMixin, UpdateView):
    model = ContenidoPagina
    fields = ['titulo_principal', 'cuerpo_seccion']
    template_name = 'landing/admin/cms_gestor_contenidos.html'
    success_url = reverse_lazy('landing:cms_gestor_contenidos')

    # solo staff/admin puede editar el contenido
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

    # se asegura que siempre se edite la unica instancia (pk=1 o seccion_id=1)
    def get_object(self, queryset=None):
        try:
            return ContenidoPagina.objects.get(seccion_id=1)
        except ContenidoPagina.DoesNotExist:
            return ContenidoPagina.objects.create(
                seccion_id=1,
                titulo_principal="¡Bienvenido a Mystic Travel!",
                cuerpo_seccion="Contenido inicial de la sección Acerca de Nosotros."
            )