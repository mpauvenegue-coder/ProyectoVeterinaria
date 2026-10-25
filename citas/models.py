from decimal import Decimal
from django.db import models

from propietarios.models import Propietario
from servicios.models import Servicio

class Cita(models.Model):
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('PAGADO', 'Pagado'),
        ('CANCELADO', 'Cancelado'),
    ]

    propietario = models.ForeignKey(Propietario, on_delete=models.PROTECT, related_name='citas')
    servicios = models.ManyToManyField(Servicio, through='DetalleCita', related_name='citas')
    nombre_mascota = models.CharField(max_length=100, default="Sin registrar")
    especie_mascota = models.CharField(max_length=50, default="Sin registrar")
    fecha_cita = models.DateField()
    fecha_atencion = models.DateField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')
    observacion = models.CharField(max_length=200, blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f'Cita {self.id} - {self.propietario}'

    def total(self):
        total = Decimal('0.00')
        for detalle in self.detalles.all():
            total += detalle.subtotal()
        return total

    def pagado(self):
        total = Decimal('0.00')
        for pago in self.pagos.filter(activo=True):
            total += pago.monto
        return total

    def saldo(self):
        return self.total() - self.pagado()

class DetalleCita(models.Model):
    cita = models.ForeignKey(Cita, on_delete=models.CASCADE, related_name='detalles')
    servicio = models.ForeignKey(Servicio, on_delete=models.PROTECT, related_name='detalles_cita')
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['cita', 'servicio'],
                name='detalle_unico_cita_servicio'
            )
        ]

    def __str__(self):
        return f'{self.servicio} x {self.cantidad}'

    def subtotal(self):
        return self.precio_unitario * self.cantidad