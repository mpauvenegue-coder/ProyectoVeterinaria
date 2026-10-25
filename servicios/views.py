from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.db.models.deletion import ProtectedError
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from veterinarios.models import Veterinario
from veterinaria_backend.permisos import validar_permiso
from .models import Servicio
from .serializers import ServicioSerializer

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
def servicios_api(request):
    if request.method == 'GET':
        permiso = validar_permiso(request, 'servicios.view_servicio')
        if permiso:
            return permiso

        servicios = Servicio.objects.select_related('veterinario').all().order_by('nombre')
        tipo = request.query_params.get('tipo')
        veterinario = request.query_params.get('veterinario')
        activo = request.query_params.get('activo')
        buscar = request.query_params.get('buscar')
        ordering = request.query_params.get('ordering')

        if tipo:
            servicios = servicios.filter(tipo__iexact=tipo)

        if veterinario:
            servicios = servicios.filter(veterinario_id=veterinario)

        if activo is not None:
            if activo.lower() not in ['true', 'false']:
                return Response(
                    {'activo': 'Utilice true o false.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            servicios = servicios.filter(activo=activo.lower() == 'true')

        if buscar:
            servicios = servicios.filter(
                Q(nombre__icontains=buscar) |
                Q(descripcion__icontains=buscar) |
                Q(codigo__icontains=buscar)
            )

        if ordering in ['nombre', '-nombre', 'precio', '-precio', 'cupos', '-cupos']:
            servicios = servicios.order_by(ordering)

        return respuesta_paginada(
            servicios,
            ServicioSerializer,
            request.query_params.get('page', 1)
        )

    permiso = validar_permiso(request, 'servicios.add_servicio')
    if permiso:
        return permiso

    serializer = ServicioSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def servicio_detalle_api(request, id):
    try:
        servicio = Servicio.objects.select_related('veterinario').get(id=id)
    except Servicio.DoesNotExist:
        return Response(
            {'error': 'Servicio no encontrado.'},
            status=status.HTTP_404_NOT_FOUND
        )

    if request.method == 'GET':
        permiso = validar_permiso(request, 'servicios.view_servicio')
        if permiso:
            return permiso
        return Response(ServicioSerializer(servicio).data)

    if request.method in ['PUT', 'PATCH']:
        permiso = validar_permiso(request, 'servicios.change_servicio')
        if permiso:
            return permiso

        serializer = ServicioSerializer(servicio, data=request.data, partial=request.method == 'PATCH')
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    permiso = validar_permiso(request, 'servicios.delete_servicio')
    if permiso:
        return permiso

    try:
        servicio.delete()
    except ProtectedError:
        return Response(
            {'error': 'No se puede eliminar porque esta en citas.'},
            status=status.HTTP_409_CONFLICT
        )
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def reportes_servicios_bajo_cupos_api(request):
    permiso = validar_permiso(request, 'servicios.view_servicio')
    if permiso:
        return permiso

    servicios = Servicio.objects.select_related('veterinario').filter(cupos__lte=5, activo=True).order_by('cupos', 'nombre')
    serializer = ServicioSerializer(servicios, many=True)
    return Response({
        'total_registros': servicios.count(),
        'resultados': serializer.data
    })

@api_view(['GET'])
def reportes_servicios_veterinario_api(request, id):
    permiso = validar_permiso(request, 'servicios.view_servicio')
    if permiso:
        return permiso

    try:
        veterinario = Veterinario.objects.get(id=id)
    except Veterinario.DoesNotExist:
        return Response(
            {'error': 'Veterinario no encontrado.'},
            status=status.HTTP_404_NOT_FOUND
        )

    servicios = Servicio.objects.filter(veterinario=veterinario).annotate(
        ventas=Count('detalles_cita')
    ).order_by('nombre')

    return Response({
        'veterinario': veterinario.nombre,
        'total_servicios': servicios.count(),
        'resultados': ServicioSerializer(servicios, many=True).data
    })