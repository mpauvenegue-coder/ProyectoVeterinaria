from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from veterinaria_backend.permisos import validar_permiso
from .models import Veterinario
from .serializers import VeterinarioSerializer

def respuesta_paginada(queryset, serializer_class, page_number):
    paginator = Paginator(queryset, 5)
    page = paginator.get_page(page_number)
    serializer = serializer_class(page.object_list, many=True)
    return Response({
        'pagina_actual': page.number,
        'total_paginas': paginator.num_pages,
        'total_registros': paginator.count,
        'resultados': serializer.data
    })

@api_view(['GET', 'POST'])
def veterinarios_api(request):
    if request.method == 'GET':
        permiso = validar_permiso(request, 'veterinarios.view_veterinario')
        if permiso:
            return permiso

        veterinarios = Veterinario.objects.all().order_by('nombre')
        activo = request.query_params.get('activo')
        buscar = request.query_params.get('buscar')

        if activo is not None:
            if activo.lower() not in ['true', 'false']:
                return Response(
                    {'activo': 'Utilice true o false.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            veterinarios = veterinarios.filter(activo=activo.lower() == 'true')

        if buscar:
            veterinarios = veterinarios.filter(
                Q(nombre__icontains=buscar) |
                Q(identificacion_profesional__icontains=buscar)
            )

        return respuesta_paginada(
            veterinarios,
            VeterinarioSerializer,
            request.query_params.get('page', 1)
        )

    permiso = validar_permiso(request, 'veterinarios.add_veterinario')
    if permiso:
        return permiso

    serializer = VeterinarioSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def veterinario_detalle_api(request, id):
    try:
        veterinario = Veterinario.objects.get(id=id)
    except Veterinario.DoesNotExist:
        return Response(
            {'error': 'Veterinario no encontrado.'},
            status=status.HTTP_404_NOT_FOUND
        )

    if request.method == 'GET':
        permiso = validar_permiso(request, 'veterinarios.view_veterinario')
        if permiso:
            return permiso
        return Response(VeterinarioSerializer(veterinario).data)

    if request.method in ['PUT', 'PATCH']:
        permiso = validar_permiso(request, 'veterinarios.change_veterinario')
        if permiso:
            return permiso

        serializer = VeterinarioSerializer(veterinario, data=request.data, partial=request.method == 'PATCH')
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    permiso = validar_permiso(request, 'veterinarios.delete_veterinario')
    if permiso:
        return permiso

    try:
        veterinario.delete()
    except ProtectedError:
        return Response(
            {'error': 'No se puede eliminar porque tiene servicios asociados.'},
            status=status.HTTP_409_CONFLICT
        )
    return Response(status=status.HTTP_204_NO_CONTENT)