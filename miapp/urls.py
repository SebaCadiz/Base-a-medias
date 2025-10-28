
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views 

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', auth_views.LoginView.as_view(template_name='crear_usuario.html' ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('crear/', views.CrearUsuario, name='crear_usuario'),
    # --- MANTENEDOR (CRUD) DE CALIFICACIONES TRIBUTARIAS ---

    # 1. READ (Leer/Listar) - La página principal del mantenedor
    path('clasificacion/', views.lista_de_calificaciones, name='clasificacion_lista'),
    
    # 2. CREATE (Crear) - La página para añadir uno nuevo
    path('clasificacion/crear/', views.clasificacion_crear, name='clasificacion_crear'),
    
    # 3. UPDATE (Actualizar) - La página para editar uno existente
    # <int:pk> es el ID del item que queremos editar (ej: /clasificacion/editar/5/)
    path('clasificacion/editar/<int:pk>/', views.clasificacion_editar, name='clasificacion_editar'),
    
    # 4. DELETE (Borrar) - La página para confirmar la eliminación
    path('clasificacion/eliminar/<int:pk>/', views.clasificacion_eliminar, name='clasificacion_eliminar'),
]
