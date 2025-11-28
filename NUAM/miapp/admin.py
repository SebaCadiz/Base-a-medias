from django.contrib import admin
from .models import (
    Usuario,
    Pais,
    Contribuyente,
    ClasificacionTributaria
)


admin.site.register(Usuario)
admin.site.register(Pais)
admin.site.register(Contribuyente)
admin.site.register(ClasificacionTributaria)
