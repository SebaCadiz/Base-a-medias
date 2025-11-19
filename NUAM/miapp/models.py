from django.db import models
from django.contrib.auth.models import User

class NaturalezaContribuyente(models.Model):
    naturaleza_del_contribuyente = models.IntegerField(primary_key=True)
    tipo = models.CharField(max_length=20)
    empleados = models.IntegerField()

    def __str__(self):
        return f"{self.naturaleza_del_contribuyente} - {self.tipo}"
    
class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=30)
    apellido = models.CharField(max_length=25)
    mail = models.CharField(max_length=253)
    contraseña = models.CharField(max_length=15)
    rol = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"
    
class Pais(models.Model):
    id_pais = models.AutoField(primary_key=True)
    pais_nom = models.CharField(max_length=15)
    moneda = models.CharField(max_length=3)
    sis_de_imp = models.CharField(max_length=15)

    def __str__(self):
        return self.moneda


class Contribuyente(models.Model):
    id_contribuyente = models.AutoField(primary_key=True)
    id_pais = models.ForeignKey(Pais, on_delete=models.CASCADE)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    naturaleza_del_contribuyente = models.ForeignKey(
        NaturalezaContribuyente,
        on_delete=models.CASCADE
    )
    situación = models.CharField(max_length=20)

    def __str__(self):
        return f"Contribuyente {self.id_contribuyente}"


class ClasificacionTributaria(models.Model):
    id_clasificacion = models.AutoField(primary_key=True)
    id_contribuyente = models.ForeignKey(Contribuyente, on_delete=models.CASCADE)
    id_pais = models.ForeignKey(Pais, on_delete=models.CASCADE)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    tipo_de_tributo = models.CharField(max_length=15)
    monto = models.IntegerField()
    actividad_economica = models.CharField(max_length=200)
    codigo_CIIU = models.IntegerField()
    regimen = models.TextField()
    categoria = models.CharField(max_length=40)
    fecha_de_creacion = models.DateField()

    def __str__(self):
        return f"Clasificación {self.id_clasificacion}"
