from django.db import models
from citas.models import Cita

class Pago(models.Model):
    METODOS = [
        ('EFECTIVO', 'Efectivo'),
        ('SINPE', 'Sinpe'),
        ('TARJETA', 'Tarjeta'),
    ]

    cita = models.ForeignKey(Cita, on_delete=models.PROTECT, related_name='pagos')
    fecha_pago = models.DateField()
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    metodo = models.CharField(max_length=20, choices=METODOS, default='EFECTIVO')
    referencia = models.CharField(max_length=50, unique=True, null=True, blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f'Pago {self.id} - {self.cita}'