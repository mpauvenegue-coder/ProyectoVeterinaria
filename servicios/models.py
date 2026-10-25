from django.db import models
from veterinarios.models import Veterinario

class Servicio(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=200, blank=True)
    tipo = models.CharField(max_length=50)
    veterinario = models.ForeignKey(Veterinario, on_delete=models.PROTECT, related_name='servicios')
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    cupos = models.IntegerField(default=0)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre