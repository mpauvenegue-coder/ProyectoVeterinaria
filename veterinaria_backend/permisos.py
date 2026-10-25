from rest_framework import status
from rest_framework.response import Response

def validar_permiso(request, permiso):
    if not request.user.is_authenticated:
        return Response(
            {'detail': 'Autenticacion requerida.'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    if not request.user.has_perm(permiso):
        return Response(
            {'detail': 'No tiene permiso para realizar esta operacion.'},
            status=status.HTTP_403_FORBIDDEN
        )
    return None
