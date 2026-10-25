from django.db import models

class Propietario(models.Model):
    identificacion = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    activo = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre