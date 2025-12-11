# Migración para agregar registros iniciales de países

from django.db import migrations

def agregar_paises(apps, schema_editor):
    Pais = apps.get_model('miapp', 'Pais')
    
    # Crear tres registros de países
    Pais.objects.create(pais_nom='Chile', moneda='CLP', sis_de_imp='SII')
    Pais.objects.create(pais_nom='Peru', moneda='PEN', sis_de_imp='SUNAT')
    Pais.objects.create(pais_nom='Colombia', moneda='COP', sis_de_imp='DIAN')

def revertir_paises(apps, schema_editor):
    Pais = apps.get_model('miapp', 'Pais')
    Pais.objects.filter(pais_nom__in=['Chile', 'Peru', 'Colombia']).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('miapp', '0006_alter_usuario_contraseña'),
    ]

    operations = [
        migrations.RunPython(agregar_paises, revertir_paises),
    ]
