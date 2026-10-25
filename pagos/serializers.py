from rest_framework import serializers
from .models import Pago

def actualizar_estado_cita(cita):
    if cita.estado == 'CANCELADO':
        return

    if cita.total() > 0 and cita.saldo() <= 0:
        cita.estado = 'PAGADO'
    else:
        cita.estado = 'PENDIENTE'
    cita.save()

class PagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pago
        fields = '__all__'

    def validate_monto(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                'El monto debe ser mayor que cero.'
            )
        return value

    def validate_referencia(self, value):
        if value:
            referencia_limpia = value.strip()
            if not referencia_limpia:
                return None
            return referencia_limpia
        return value

    def validate(self, data):
        cita = data.get('cita', getattr(self.instance, 'cita', None))
        fecha_pago = data.get('fecha_pago', getattr(self.instance, 'fecha_pago', None))
        monto = data.get('monto', getattr(self.instance, 'monto', None))
        activo = data.get('activo', getattr(self.instance, 'activo', True))

        if cita and cita.estado == 'CANCELADO':
            raise serializers.ValidationError({
                'cita': 'No se puede pagar una cita cancelada.'
            })

        if cita and fecha_pago and fecha_pago < cita.fecha_cita:
            raise serializers.ValidationError({
                'fecha_pago': 'No puede ser anterior a la fecha de la cita.'
            })

        if cita and cita.total() <= 0:
            raise serializers.ValidationError({
                'cita': 'El cita debe tener servicios antes de pagar.'
            })

        if cita and self.instance and self.instance.cita_id != cita.id:
            raise serializers.ValidationError({'cita': 'No se puede cambiar la cita de un pago.'})

        if cita and monto and activo:
            total_pagado = cita.pagado()
            if self.instance and self.instance.activo:
                total_pagado = total_pagado - self.instance.monto

            saldo = cita.total() - total_pagado
            if monto > saldo:
                raise serializers.ValidationError({
                    'monto': 'El pago no puede superar el saldo de la cita.'
                })
        return data

    def create(self, validated_data):
        pago = Pago.objects.create(**validated_data)
        actualizar_estado_cita(pago.cita)
        return pago

    def update(self, instance, validated_data):
        cita_anterior = instance.cita
        pago = super().update(instance, validated_data)
        actualizar_estado_cita(cita_anterior)
        actualizar_estado_cita(pago.cita)
        return pago