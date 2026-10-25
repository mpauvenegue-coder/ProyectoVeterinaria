from rest_framework import serializers
from .models import Servicio

class ServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servicio
        fields = '__all__'

    def validate_codigo(self, value):
        codigo_limpio = value.strip()

        if not codigo_limpio:
            raise serializers.ValidationError(
                'El codigo es obligatorio.'
            )
        return codigo_limpio

    def validate_nombre(self, value):
        nombre_limpio = value.strip()

        if len(nombre_limpio) < 3:
            raise serializers.ValidationError(
                'El nombre debe tener al menos 3 caracteres.'
            )
        return nombre_limpio

    def validate_tipo(self, value):
        tipo_limpia = value.strip()

        if not tipo_limpia:
            raise serializers.ValidationError(
                'La tipo es obligatoria.'
            )
        return tipo_limpia

    def validate_precio(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                'El precio debe ser mayor que cero.'
            )
        return value

    def validate_cupos(self, value):
        if value < 0:
            raise serializers.ValidationError(
                'Los cupos no pueden ser negativo.'
            )
        return value

    def validate(self, data):
        veterinario = data.get(
            'veterinario',
            getattr(self.instance, 'veterinario', None)
        )

        if self.instance and 'cupos' in data and data['cupos'] < 0:
            raise serializers.ValidationError({'cupos': 'No puede ser negativo.'})

        if veterinario and not veterinario.activo:
            raise serializers.ValidationError({
                'veterinario': 'No se puede usar un veterinario inactivo.'
            })
        return data