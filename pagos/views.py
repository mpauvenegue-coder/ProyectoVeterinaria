from django.core.paginator import Paginator
from django.db.models.deletion import ProtectedError
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from veterinaria_backend.permisos import validar_permiso
from .models import Pago
from .serializers import PagoSerializer, actualizar_estado_cita

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
def pagos_api(request):
    if request.method == 'GET':
        permiso = validar_permiso(request, 'pagos.view_pago')
        if permiso:
            return permiso

        pagos = Pago.objects.select_related('cita','cita__propietario').all().order_by('-fecha_pago')
        cita = request.query_params.get('cita')
        metodo = request.query_params.get('metodo')
        activo = request.query_params.get('activo')

        if cita:
            pagos = pagos.filter(cita_id=cita)

        if metodo:
            pagos = pagos.filter(metodo=metodo.upper())

        if activo is not None:
            if activo.lower() not in ['true', 'false']:
                return Response(
                    {'activo': 'Utilice true o false.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            pagos = pagos.filter(activo=activo.lower() == 'true')

        return respuesta_paginada(
            pagos,
            PagoSerializer,
            request.query_params.get('page', 1)
        )

    permiso = validar_permiso(request, 'pagos.add_pago')
    if permiso:
        return permiso

    serializer = PagoSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def pago_detalle_api(request, id):
    try:
        pago = Pago.objects.select_related('cita').get(id=id)
    except Pago.DoesNotExist:
        return Response(
            {'error': 'Pago no encontrado.'},
            status=status.HTTP_404_NOT_FOUND
        )

    if request.method == 'GET':
        permiso = validar_permiso(request, 'pagos.view_pago')
        if permiso:
            return permiso
        return Response(PagoSerializer(pago).data)

    if request.method in ['PUT', 'PATCH']:
        permiso = validar_permiso(request, 'pagos.change_pago')
        if permiso:
            return permiso

        serializer = PagoSerializer(pago, data=request.data, partial=request.method == 'PATCH')
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    permiso = validar_permiso(request, 'pagos.delete_pago')
    if permiso:
        return permiso

    try:
        cita = pago.cita
        pago.delete()
        actualizar_estado_cita(cita)
    except ProtectedError:
        return Response(
            {'error': 'No se puede eliminar este pago.'},
            status=status.HTTP_409_CONFLICT
        )
    return Response(status=status.HTTP_204_NO_CONTENT)