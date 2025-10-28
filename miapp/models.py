from django.db import models
from django.contrib.auth.models import User

class Usuario(models.Model):
    id_usuario = models.CharField(primary_key=True, max_length=10)
    Usu_nombre = models.CharField(max_length=40, null=True, blank=True)
    Usu_contraseña = models.CharField(max_length=20, null=True, blank=True)
    Usu_email = models.CharField(max_length=60, null=True, blank=True)
    Usu_telefono = models.CharField(max_length=24, null=True, blank=True)

    class Meta:
        db_table = 'USUARIO'
    def __str__(self):
        return self.Usu_nombre or f"Usuario {self.id_usuario}"
    
class Moneda(models.Model):
    """
    Almacena las monedas (Peso Chileno, Sol Peruano, etc.)
    """
    nombre = models.CharField(max_length=50, unique=True, 
                              help_text="Nombre oficial (ej: Peso Chileno)")
    codigo = models.CharField(max_length=3, unique=True, 
                              help_text="Código ISO (ej: CLP)")

    class Meta:
        verbose_name = "Moneda"
        verbose_name_plural = "Monedas"

    def __str__(self):
        # Corregido con DOS guiones bajos
        return f"{self.nombre} ({self.codigo})"


class Pais(models.Model):
    """
    Almacena los países (Chile, Perú, Colombia)
    y los vincula a su moneda oficial.
    """
    nombre = models.CharField(max_length=50, unique=True)
    codigo_iso = models.CharField(max_length=3, unique=True, 
                                  help_text="Código ISO (ej: CHL)")
    
    # --- Relación ---
    # Cada país tiene una moneda oficial
    moneda = models.ForeignKey(Moneda, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "País"
        verbose_name_plural = "Países"

    def __str__(self):
        return self.nombre



class CalificacionTributaria(models.Model):
    """
    ESTA ES LA TABLA PARA TU MANTENEDOR.
    Almacena las tasas de impuestos (ej: IVA, Impuesto Específico)
    y las vincula a un país.
    """
    nombre = models.CharField(max_length=100, 
                              help_text="Nombre de la calificación (ej: IVA General)")
    descripcion = models.TextField(blank=True, null=True)
    
    # Usamos DecimalField para tasas y factores. Es más preciso.
    # Ej: 0.19 para el 19%
    tasa_o_factor = models.DecimalField(
        max_digits=10, 
        decimal_places=5,
        help_text="El valor numérico de la tasa (ej: 0.19 para 19%)"
    ) 
    
    # --- Relación ---
    # Esta calificación pertenece a un país.
    pais = models.ForeignKey(Pais, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Calificación Tributaria"
        verbose_name_plural = "Calificaciones Tributarias"
        # Evita que crees dos "IVA General" para el mismo país
        unique_together = ('nombre', 'pais')

    def __str__(self):
        return f"{self.nombre} ({self.pais.nombre})"



class TasaDeCambio(models.Model):
    """
    ESTA ES LA TABLA PARA TU CONVERSOR.
    Almacena la tasa de cambio entre dos monedas.
    """
    # Ej: CLP
    moneda_origen = models.ForeignKey(Moneda, related_name='tasas_origen', 
                                      on_delete=models.CASCADE)
    # Ej: PEN
    moneda_destino = models.ForeignKey(Moneda, related_name='tasas_destino', 
                                      on_delete=models.CASCADE)
    
    # Tasa: 1 unidad de 'moneda_origen' vale X unidades de 'moneda_destino'
    tasa = models.DecimalField(max_digits=15, decimal_places=6)
    
    # Guarda la fecha y hora de la última actualización
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Tasa de Cambio"
        verbose_name_plural = "Tasas de Cambio"
        # Solo puede haber una tasa de CLP a PEN
        unique_together = ('moneda_origen', 'moneda_destino')

    def __str__(self):
        return f"1 {self.moneda_origen.codigo} = {self.tasa} {self.moneda_destino.codigo}"

