from django.contrib import admin
from .models import (
    Usuario,
    Pais,
    Contribuyente,
    ClasificacionTributaria,
    Evento
)


admin.site.register(Usuario)
admin.site.register(Pais)
admin.site.register(Contribuyente)
admin.site.register(ClasificacionTributaria)
admin.site.register(Evento)