from django.shortcuts import render

# Create your views here.
from django.core.paginator import Paginator
from django.db.models import Count, Q, Sum
from django.db.models.deletion import ProtectedError
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from propietarios.models import Propietario
from servicios.models import Servicio
from veterinarios.models import Veterinario
from veterinaria_backend.permisos import validar_permiso
from .models import DetalleCita, Cita
from .serializers import DetalleCitaSerializer, CitaSerializer

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
def citas_api(request):
    if request.method == 'GET':
        permiso = validar_permiso(request, 'citas.view_cita')
        if permiso:
            return permiso

        citas = Cita.objects.select_related('propietario').prefetch_related(
            'detalles__servicio',
            'pagos'
        ).all().order_by('-fecha_cita')

        estado = request.query_params.get('estado')
        propietario = request.query_params.get('propietario')
        activo = request.query_params.get('activo')
        ordering = request.query_params.get('ordering')

        if estado:
            citas = citas.filter(estado=estado.upper())

        if propietario:
            citas = citas.filter(propietario_id=propietario)

        if activo is not None:
            if activo.lower() not in ['true', 'false']:
                return Response(
                    {'activo': 'Utilice true o false.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            citas = citas.filter(activo=activo.lower() == 'true')

        if ordering in ['fecha_cita', '-fecha_cita', 'id', '-id']:
            citas = citas.order_by(ordering)

        return respuesta_paginada(
            citas,
            CitaSerializer,
            request.query_params.get('page', 1)
        )

    permiso = validar_permiso(request, 'citas.add_cita')
    if permiso:
        return permiso

    serializer = CitaSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def cita_detalle_api(request, id):
    try:
        cita = Cita.objects.select_related('propietario').prefetch_related(
            'detalles__servicio',
            'pagos'
        ).get(id=id)
    except Cita.DoesNotExist:
        return Response(
            {'error': 'Cita no encontrada.'},
            status=status.HTTP_404_NOT_FOUND
        )

    if request.method == 'GET':
        permiso = validar_permiso(request, 'citas.view_cita')
        if permiso:
            return permiso
        return Response(CitaSerializer(cita).data)

    if request.method in ['PUT', 'PATCH']:
        permiso = validar_permiso(request, 'citas.change_cita')
        if permiso:
            return permiso

        serializer = CitaSerializer(cita, data=request.data, partial=request.method == 'PATCH')
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    permiso = validar_permiso(request, 'citas.delete_cita')
    if permiso:
        return permiso

    if cita.estado == 'PAGADO':
        return Response({'error': 'No se puede eliminar una cita pagada.'}, status=status.HTTP_409_CONFLICT)
    if cita.pagos.exists():
        return Response({'error': 'La cita tiene pagos asociados.'}, status=status.HTTP_409_CONFLICT)
    for detalle in cita.detalles.select_related('servicio'):
        servicio = detalle.servicio
        servicio.cupos += detalle.cantidad
        servicio.save()
    try:
        cita.delete()
    except ProtectedError:
        return Response(
            {'error': 'No se puede eliminar porque tiene pagos asociados.'},
            status=status.HTTP_409_CONFLICT
        )
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET', 'POST'])
def detalles_cita_api(request, id):
    try:
        cita = Cita.objects.get(id=id)
    except Cita.DoesNotExist:
        return Response(
            {'error': 'Cita no encontrada.'},
            status=status.HTTP_404_NOT_FOUND
        )

    if request.method == 'GET':
        permiso = validar_permiso(request, 'citas.view_detallecita')
        if permiso:
            return permiso

        detalles = cita.detalles.select_related('servicio').order_by('id')
        return Response(
            DetalleCitaSerializer(detalles, many=True).data,
            status=status.HTTP_200_OK
        )

    permiso = validar_permiso(request, 'citas.add_detallecita')
    if permiso:
        return permiso

    data = request.data.copy()
    data['cita'] = cita.id
    serializer = DetalleCitaSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def detalle_cita_detalle_api(request, id):
    try:
        detalle = DetalleCita.objects.select_related(
            'cita',
            'servicio'
        ).get(id=id)
    except DetalleCita.DoesNotExist:
        return Response(
            {'error': 'Detalle no encontrado.'},
            status=status.HTTP_404_NOT_FOUND
        )

    if request.method == 'GET':
        permiso = validar_permiso(request, 'citas.view_detallecita')
        if permiso:
            return permiso
        return Response(DetalleCitaSerializer(detalle).data)

    if request.method in ['PUT', 'PATCH']:
        permiso = validar_permiso(request, 'citas.change_detallecita')
        if permiso:
            return permiso

        serializer = DetalleCitaSerializer(detalle, data=request.data, partial=request.method == 'PATCH')
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    permiso = validar_permiso(request, 'citas.delete_detallecita')
    if permiso:
        return permiso

    if detalle.cita.estado in ['PAGADO', 'CANCELADO'] or detalle.cita.pagado() > 0:
        return Response(
            {'error': 'No se puede eliminar un detalle de una cita cerrada.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    servicio = detalle.servicio
    servicio.cupos = servicio.cupos + detalle.cantidad
    servicio.save()
    detalle.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def perfil_api(request):
    if not request.user.is_authenticated:
        return Response(
            {'detail': 'Autenticacion requerida.'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    return Response({
        'id': request.user.id,
        'username': request.user.username,
        'email': request.user.email
    })

@api_view(['GET'])
def sesion_api(request):
    visitas = request.session.get('visitas', 0) + 1
    request.session['visitas'] = visitas

    return Response({
        'visitas': visitas
    })

@api_view(['GET'])
def reportes_resumen_api(request):
    permiso = validar_permiso(request, 'citas.view_cita')
    if permiso:
        return permiso

    from pagos.models import Pago

    total_pagado = Pago.objects.filter(activo=True).aggregate(
        total=Sum('monto')
    )['total'] or 0

    return Response({
        'propietarios': Propietario.objects.count(),
        'veterinarios': Veterinario.objects.count(),
        'servicios': Servicio.objects.count(),
        'citas': Cita.objects.count(),
        'citas_pendientes': Cita.objects.filter(estado='PENDIENTE').count(),
        'citas_pagados': Cita.objects.filter(estado='PAGADO').count(),
        'pagos_activos': str(total_pagado)
    })


@api_view(['GET'])
def reportes_propietarios_atenciones_api(request):
    permiso = validar_permiso(request, 'propietarios.view_propietario')
    if permiso:
        return permiso

    propietarios = Propietario.objects.prefetch_related('citas').annotate(
        total_citas=Count('citas'),
        total_pagado=Sum(
            'citas__pagos__monto',
            filter=Q(citas__pagos__activo=True)
        )
    ).order_by('-total_pagado', 'nombre')

    resultados = []
    for propietario in propietarios:
        resultados.append({
            'id': propietario.id,
            'nombre': propietario.nombre,
            'total_citas': propietario.total_citas,
            'total_pagado': str(propietario.total_pagado or 0)
        })

    return Response(resultados)

@api_view(['GET'])
def reportes_citas_propietario_api(request, id):
    permiso = validar_permiso(request, 'citas.view_cita')
    if permiso:
        return permiso

    try:
        propietario = Propietario.objects.get(id=id)
    except Propietario.DoesNotExist:
        return Response(
            {'error': 'Propietario no encontrado.'},
            status=status.HTTP_404_NOT_FOUND
        )

    citas = Cita.objects.select_related('propietario').prefetch_related(
        'detalles__servicio',
        'pagos'
    ).filter(propietario=propietario).order_by('-fecha_cita')

    return Response({
        'propietario': propietario.nombre,
        'total_registros': citas.count(),
        'resultados': CitaSerializer(citas, many=True).data
    })