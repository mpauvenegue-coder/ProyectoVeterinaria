from rest_framework import serializers

from .models import Propietario

class PropietarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Propietario
        fields = '__all__'

    def validate_identificacion(self, value):
        identificacion_limpia = value.strip()

        if not identificacion_limpia:
            raise serializers.ValidationError(
                'La identificacion es obligatoria.'
            )
        return identificacion_limpia

    def validate_nombre(self, value):
        nombre_limpio = value.strip()

        if len(nombre_limpio) < 3:
            raise serializers.ValidationError(
                'El nombre debe tener al menos 3 caracteres.'
            )
        return nombre_limpio

    def validate_telefono(self, value):
        telefono_limpio = value.strip()

        if len(telefono_limpio) < 8:
            raise serializers.ValidationError(
                'El telefono debe tener al menos 8 digitos.'
            )
        return telefono_limpio