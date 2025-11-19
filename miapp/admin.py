from django.contrib import admin
from .models import (
    NaturalezaContribuyente,
    Usuario,
    Pais,
    Contribuyente,
    ClasificacionTributaria
)

admin.site.register(NaturalezaContribuyente)
admin.site.register(Usuario)
admin.site.register(Pais)
admin.site.register(Contribuyente)
admin.site.register(ClasificacionTributaria)
