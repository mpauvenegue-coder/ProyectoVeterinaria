from rest_framework import serializers
from .models import DetalleCita, Cita

class CitaSerializer(serializers.ModelSerializer):
    total = serializers.SerializerMethodField()
    pagado = serializers.SerializerMethodField()
    saldo = serializers.SerializerMethodField()

    class Meta:
        model = Cita
        fields = [
            'id', 'propietario', 'nombre_mascota', 'especie_mascota', 'fecha_cita', 'fecha_atencion',
            'estado', 'observacion', 'activo',
            'total', 'pagado', 'saldo'
        ]

    def get_total(self, obj):
        return str(obj.total())

    def get_pagado(self, obj):
        return str(obj.pagado())

    def get_saldo(self, obj):
        return str(obj.saldo())

    def validate(self, data):
        fecha_cita = data.get('fecha_cita', getattr(self.instance, 'fecha_cita', None))
        fecha_atencion = data.get('fecha_atencion', getattr(self.instance, 'fecha_atencion', None))
        propietario = data.get('propietario', getattr(self.instance, 'propietario', None))
        estado = data.get('estado', getattr(self.instance, 'estado', 'PENDIENTE'))

        for campo in ['nombre_mascota', 'especie_mascota']:
            if campo in data and not data[campo].strip():
                raise serializers.ValidationError({campo: 'No puede estar vacio.'})

        if fecha_cita and fecha_atencion and fecha_atencion < fecha_cita:
            raise serializers.ValidationError({
                'fecha_atencion': 'No puede ser anterior a la fecha de cita.'
            })

        if propietario and not propietario.activo:
            raise serializers.ValidationError({
                'propietario': 'No se puede crear un cita para un propietario inactivo.'
            })

        if estado == 'PAGADO' and not self.instance:
            raise serializers.ValidationError({
                'estado': 'Un cita nuevo no puede nacer como pagado.'
            })

        if self.instance and self.instance.estado in ['PAGADO', 'CANCELADO'] and any(campo != 'estado' for campo in data):
            raise serializers.ValidationError({'estado': 'No se puede modificar una cita cerrada.'})

        if self.instance and estado == 'PAGADO' and (self.instance.total() <= 0 or self.instance.saldo() > 0):
            raise serializers.ValidationError({
                'estado': 'No se puede marcar pagado con saldo pendiente.'
            })

        if self.instance and estado == 'CANCELADO' and self.instance.pagado() > 0:
            raise serializers.ValidationError({
                'estado': 'No se puede cancelar un cita con pagos activos.'
            })

        if self.instance and self.instance.estado in ['PAGADO', 'CANCELADO'] and estado != self.instance.estado:
            raise serializers.ValidationError({'estado': 'Una cita cerrada no se puede reabrir.'})
        return data

class DetalleCitaSerializer(serializers.ModelSerializer):
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = DetalleCita
        fields = [
            'id', 'cita', 'servicio', 'cantidad',
            'precio_unitario', 'subtotal'
        ]

    def get_subtotal(self, obj):
        return str(obj.subtotal())

    def validate_cantidad(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                'La cantidad debe ser mayor que cero.'
            )
        return value

    def validate_precio_unitario(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                'El precio unitario debe ser mayor que cero.'
            )
        return value

    def validate(self, data):
        cita = data.get('cita', getattr(self.instance, 'cita', None))
        servicio = data.get( 'servicio', getattr(self.instance, 'servicio', None))
        cantidad = data.get('cantidad', getattr(self.instance, 'cantidad', None))

        if cita and cita.estado in ['PAGADO', 'CANCELADO']:
            raise serializers.ValidationError({
                'cita': 'No se puede modificar un cita cerrado.'
            })

        if cita and cita.pagado() > 0:
            raise serializers.ValidationError({'cita': 'No se pueden modificar servicios con pagos registrados.'})

        if servicio and not servicio.activo:
            raise serializers.ValidationError({
                'servicio': 'No se puede vender un servicio inactivo.'
            })

        if cita and servicio:
            detalles = DetalleCita.objects.filter(cita=cita, servicio=servicio)
            if self.instance:
                detalles = detalles.exclude(id=self.instance.id)
            if detalles.exists():
                raise serializers.ValidationError(
                    'El servicio ya existe en este cita.'
                )

        cantidad_actual = 0
        if self.instance and servicio and self.instance.servicio_id == servicio.id:
            cantidad_actual = self.instance.cantidad

        if servicio and cantidad and cantidad > servicio.cupos + cantidad_actual:
            raise serializers.ValidationError({
                'cantidad': 'No hay cupos suficiente para este servicio.'
            })
        return data

    def create(self, validated_data):
        servicio = validated_data['servicio']
        cantidad = validated_data['cantidad']
        servicio.cupos = servicio.cupos - cantidad
        servicio.save()
        return DetalleCita.objects.create(**validated_data)

    def update(self, instance, validated_data):
        servicio_anterior = instance.servicio
        servicio_anterior.cupos = servicio_anterior.cupos + instance.cantidad
        servicio_anterior.save()

        servicio = validated_data.get('servicio', instance.servicio)
        cantidad = validated_data.get('cantidad', instance.cantidad)
        servicio.cupos = servicio.cupos - cantidad
        servicio.save()

        return super().update(instance, validated_data)