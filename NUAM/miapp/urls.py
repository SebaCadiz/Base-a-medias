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
    path('editar/<int:user_id>/', views.editar_usuario, name='editar'),
    path('eliminar/<int:user_id>/', views.eliminar_usuario, name='eliminar'),
]