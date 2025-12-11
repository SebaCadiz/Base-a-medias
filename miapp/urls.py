from django.urls import path
from . import views

urlpatterns = [
    # 1. Ruta Raíz: Muestra el formulario de Login/Registro
    # Apuntamos a 'crear_usuario' porque ahí está tu HTML de entrada.
    path('', views.crear_usuario, name='crear_usuario'), 

    # 2. Registro: Apunta a la misma vista para procesar el formulario
    path('registro/', views.crear_usuario, name='registro'),

    # 3. Login MANUAL: Usamos TU función 'login_view' (views.py)
    # Esta función guarda la sesión sin tocar la base de datos.
    path('login/', views.login_view, name='login'),

    # 4. Logout MANUAL: Usamos TU función 'logout_view' (views.py)
    path('logout/', views.logout_view, name='logout'),

    # 5. Página Principal: Solo accesible si estás logueado
    path('inicio/', views.index, name='index'),

    # 6. Pagina solo para Administradores
    path('manejo/', views.manejo , name='manejo'),
    #Manejo de cuenta
    path('manejo/mi-cuenta/', views.configurar_cuenta, name='cuenta'),  
    path('cuenta/eliminar/', views.eliminar_cuenta, name='eliminar_cuenta'),
    # Admin: ver usuarios y sus contribuyentes
    path('usuarios-contribuyentes/', views.usuarios_contribuyentes, name='usuarios_contribuyentes'),
    path('editar/<int:user_id>/', views.editar_usuario, name='editar'),
    path('eliminar/<int:user_id>/', views.eliminar_usuario, name='eliminar'),
    
    # 7. Tributarios
    path('tributarios/', views.manejo_tributarios, name='manejo_tributarios'),
    path('tributarios/editar/<int:contribuyente_id>/', views.editar_tributario, name='editar_tributario'),
    path('tributarios/eliminar/<int:contribuyente_id>/', views.eliminar_tributario, name='eliminar_tributario'),
    path('contribuyentes/crear/', views.crear_contribuyente, name='crear_contribuyente'),
    
    # Ruta para ver las clasificaciones de un contribuyente específico
    path('tributarios/<int:contribuyente_id>/clasificaciones/', views.clasificaciones_por_contribuyente, name='clasificaciones_por_contribuyente'),
    # Clasificaciones: crear / editar / eliminar
    path('tributarios/<int:contribuyente_id>/clasificaciones/crear/', views.crear_clasificacion, name='crear_clasificacion'),
    path('clasificaciones/editar/<int:clasificacion_id>/', views.editar_clasificacion, name='editar_clasificacion'),
    path('clasificaciones/eliminar/<int:clasificacion_id>/', views.eliminar_clasificacion, name='eliminar_clasificacion'),
    path('tributarios/<int:contribuyente_id>/clasificaciones/cargar_masivo/', views.cargar_clasificaciones_masivo, name='cargar_masivo'),
    # Eventos-Pulsar
    path("eventos/", views.lista_eventos, name="lista_eventos"),
        # API de divisas
    path('api/convert/', views.api_convert, name='api_convert'),
    path('api/currencies/', views.api_currencies, name='api_currencies'),
    # Página para el conversor de divisas
    path('divisas/', views.divisas_page, name='divisas'),
    # Página para Preguntas Frecuentes
    path('faq/', views.faq_page, name='faq'),
]

