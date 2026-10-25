from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from veterinaria_backend.permisos import validar_permiso
from .models import Propietario
from .serializers import PropietarioSerializer

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
def propietarios_api(request):
    if request.method == 'GET':
        permiso = validar_permiso(request, 'propietarios.view_propietario')
        if permiso:
            return permiso

        propietarios = Propietario.objects.all().order_by('id')
        activo = request.query_params.get('activo')
        buscar = request.query_params.get('buscar')
        ordering = request.query_params.get('ordering')

        if activo is not None:
            if activo.lower() not in ['true', 'false']:
                return Response(
                    {'activo': 'Utilice true o false.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            propietarios = propietarios.filter(activo=activo.lower() == 'true')

        if buscar:
            propietarios = propietarios.filter(
                Q(nombre__icontains=buscar) |
                Q(identificacion__icontains=buscar)
            )

        if ordering in ['nombre', '-nombre', 'id', '-id']:
            propietarios = propietarios.order_by(ordering)

        return respuesta_paginada(
            propietarios,
            PropietarioSerializer,
            request.query_params.get('page', 1)
        )

    permiso = validar_permiso(request, 'propietarios.add_propietario')
    if permiso:
        return permiso

    serializer = PropietarioSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def propietario_detalle_api(request, id):
    try:
        propietario = Propietario.objects.get(id=id)
    except Propietario.DoesNotExist:
        return Response(
            {'error': 'Propietario no encontrado.'},
            status=status.HTTP_404_NOT_FOUND
        )

    if request.method == 'GET':
        permiso = validar_permiso(request, 'propietarios.view_propietario')
        if permiso:
            return permiso
        return Response(PropietarioSerializer(propietario).data)

    if request.method in ['PUT', 'PATCH']:
        permiso = validar_permiso(request, 'propietarios.change_propietario')
        if permiso:
            return permiso

        serializer = PropietarioSerializer(propietario, data=request.data, partial=request.method == 'PATCH')
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    permiso = validar_permiso(request, 'propietarios.delete_propietario')
    if permiso:
        return permiso

    try:
        propietario.delete()
    except ProtectedError:
        return Response(
            {'error': 'No se puede eliminar porque tiene citas asociados.'},
            status=status.HTTP_409_CONFLICT
        )
    return Response(status=status.HTTP_204_NO_CONTENT)