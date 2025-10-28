from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('miapp.urls')),
    path('crear/', include('miapp.urls') ),
    path('eliminar/', include('miapp.urls') ),
    path('modific/', include('miapp.urls') ),
]
