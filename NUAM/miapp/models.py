from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Evento(models.Model):
    tipo = models.CharField(max_length=100)
    contenido = models.JSONField()
    timestamp = models.DateTimeField(default=timezone.now)
    
    
class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=30)
    apellido = models.CharField(max_length=25)
    mail = models.CharField(max_length=25)
    contraseña = models.CharField(max_length=12)
    rol = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    @property
    def is_active(self):
        # Django necesita saber si el usuario puede entrar. 
        # Devolvemos True siempre para decir "sí, este usuario está activo".
        return True

    @property
    def is_authenticated(self):
        # Esto le dice a Django que este objeto es un usuario real autenticado.
        return True

    @property
    def is_anonymous(self):
        # Esto le dice a Django que NO es un usuario anónimo.
        return False

    # Opcional: Ayuda a Django a saber cuál es el identificador principal si lo necesita
    def get_username(self):
        return self.nombre
    
        
    
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
    situación = models.CharField(max_length=20)
    nombre_comercial = models.CharField(max_length=100)
    actividad_economica = models.CharField(max_length=50)
    identificador_tributario = models.CharField(max_length=30)
    tipo = models.CharField(max_length=20)
    empleados = models.IntegerField()
    categoria = models.CharField(max_length=40)
    def __str__(self):
        return f"Contribuyente {self.id_contribuyente}"

class ClasificacionTributaria(models.Model):
    id_clasificacion = models.AutoField(primary_key=True)
    id_contribuyente = models.ForeignKey(Contribuyente, on_delete=models.CASCADE)
    id_pais = models.ForeignKey(Pais, on_delete=models.CASCADE)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    tipo_de_tributo = models.CharField(max_length=15)
    monto = models.IntegerField()
    codigo_CIIU = models.IntegerField()
    regimen = models.TextField()
    fecha_de_creacion = models.DateField()

    def __str__(self):
        return f"Clasificación {self.id_clasificacion}"

