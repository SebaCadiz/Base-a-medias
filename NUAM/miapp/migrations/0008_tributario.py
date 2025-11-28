# Generated migration for Tributario model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('miapp', '0006_alter_usuario_contraseña'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tributario',
            fields=[
                ('id_tributario', models.AutoField(primary_key=True, serialize=False)),
                ('tipo_de_tributo', models.CharField(max_length=15)),
                ('monto', models.IntegerField()),
                ('actividad_economica', models.CharField(max_length=200)),
                ('codigo_CIIU', models.IntegerField()),
                ('regimen', models.TextField()),
                ('categoria', models.CharField(max_length=40)),
                ('fecha_de_creacion', models.DateField()),
                ('id_pais', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='miapp.pais')),
                ('id_usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='miapp.usuario')),
                ('naturaleza_del_contribuyente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='miapp.naturalezacontribuyente')),
            ],
        ),
    ]
