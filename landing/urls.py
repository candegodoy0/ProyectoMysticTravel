from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views

app_name = 'landing'

urlpatterns = [
    path('', views.home, name='home'),
    path('registro/', views.registro, name='registro'),
    path('login/', views.iniciar_sesion, name='login'),
    path('panel/', views.user_panel, name='user_panel'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', auth_views.LogoutView.as_view(next_page='landing:login'), name='logout'),
    path('galeria/', views.galeria, name='galeria'),
    path('galeria/<str:destino>/', views.galeria_destino, name='galeria_destino'),
    path('info/', views.info, name='info'),
    path('reservas/', views.reservas, name='reservas'),
    path('listado-reservas/', views.listado_reservas, name='listado_reservas'),
    path('reserva/<int:pk>/', views.reserva_detalle, name='reserva_detalle'),
    path('reserva/<int:pk>/editar/', views.reserva_editar, name='reserva_editar'),
    path('reserva/<int:pk>/eliminar/', views.reserva_eliminar, name='reserva_eliminar'),
]