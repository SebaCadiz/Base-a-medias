# Generated migration to update Tributario model structure

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('miapp', '0008_tributario'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tributario',
            name='id_usuario',
        ),
        migrations.RemoveField(
            model_name='tributario',
            name='id_pais',
        ),
        migrations.RemoveField(
            model_name='tributario',
            name='naturaleza_del_contribuyente',
        ),
        migrations.AddField(
            model_name='tributario',
            name='id_contribuyente',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='miapp.contribuyente'),
            preserve_default=False,
        ),
    ]
