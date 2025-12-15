from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter
from .views import ReservaViewSet, ContactoViewSet, CMSContenidoUpdateView


router = DefaultRouter()
router.register(r'reservas', ReservaViewSet, basename='reservas')
router.register(r'consultas', ContactoViewSet, basename='contactos')

app_name = 'landing'

urlpatterns = [
    path('', views.home, name='home'),
    path('galeria/', views.galeria, name='galeria'),
    path('galeria/<str:destino>/', views.galeria_destino, name='galeria_destino'),
    path('info/', views.info, name='info'),
    path('reservas/', views.reservas, name='reservas'),

    path('registro/', views.registro_avanzado, name='registro'),
    path('validar-cuenta/', views.validar_cuenta, name='validar_cuenta'),
    path('login/', views.iniciar_sesion_avanzado, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='landing:login'), name='logout'),

    path('reset-password/', auth_views.PasswordResetView.as_view(
        template_name='landing/auth/password_reset_form.html',
        email_template_name='landing/auth/password_reset_email.txt',
        subject_template_name='landing/auth/password_reset_subject.txt',
        success_url='/password-reset-done/'
    ), name='password_reset'),

    path('password-reset-done/', auth_views.PasswordResetDoneView.as_view(
        template_name='landing/auth/password_reset_done.html'
    ), name='password_reset_done'),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='landing/auth/password_reset_confirm.html',
        success_url='/password-reset-complete/'
    ), name='password_reset_confirm'),

    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='landing/auth/password_reset_complete.html'
    ), name='password_reset_complete'),

    path('panel/', views.dashboard, name='dashboard'),
    path('panel/cms/', CMSContenidoUpdateView.as_view(), name='cms_gestor_contenidos'),

    path('listado-reservas/', views.listado_reservas, name='listado_reservas'),
    path('reserva/<int:pk>/', views.reserva_detalle, name='reserva_detalle'),
    path('reserva/<int:pk>/editar/', views.reserva_editar, name='reserva_editar'),
    path('reserva/<int:pk>/eliminar/', views.reserva_eliminar, name='reserva_eliminar'),

    path('listado-solicitudes/', views.listado_solicitudes, name='listado_solicitudes'),
    path('solicitud/<int:pk>/', views.solicitud_detalle, name='solicitud_detalle'),
    path('solicitud/<int:pk>/editar/', views.solicitud_editar, name='solicitud_editar'),
    path('solicitud/<int:pk>/eliminar/', views.solicitud_eliminar, name='solicitud_eliminar'),

    path('api/', include(router.urls)),
]