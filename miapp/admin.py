from django.contrib import admin
from .models import Moneda, Pais, CalificacionTributaria, TasaDeCambio

# Register your models here.
admin.site.register(Moneda)
admin.site.register(Pais)
admin.site.register(CalificacionTributaria)
admin.site.register(TasaDeCambio)