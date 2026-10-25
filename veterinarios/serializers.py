from rest_framework import serializers
from .models import Veterinario

class VeterinarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Veterinario
        fields = '__all__'

    def validate_identificacion_profesional(self, value):
        cedula_limpia = value.strip()

        if not cedula_limpia:
            raise serializers.ValidationError(
                'La cedula juridica es obligatoria.'
            )
        return cedula_limpia

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