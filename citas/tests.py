from datetime import date
from django.contrib.auth.models import Group, Permission, User
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from propietarios.models import Propietario
from pagos.models import Pago
from citas.models import DetalleCita, Cita
from servicios.models import Servicio
from veterinarios.models import Veterinario

class ProyectoVeterinariaTests(APITestCase):

    def setUp(self):
        self.admin = User.objects.create_superuser(username='admin', password='admin123', email='admin@veterinaria.test')
        self.recepcionista = User.objects.create_user(username='recepcionista', password='recepcionista123')
        self.consulta = User.objects.create_user(username='consulta', password='consulta123')
        self.token_admin = Token.objects.create(user=self.admin)
        self.token_recepcionista = Token.objects.create(user=self.recepcionista)
        self.token_consulta = Token.objects.create(user=self.consulta)
        apps = ['propietarios', 'veterinarios', 'servicios', 'citas', 'pagos']
        grupo_recepcionista = Group.objects.create(name='Recepcionistas')
        permisos_recepcionista = Permission.objects.filter(content_type__app_label__in=apps).exclude(codename__startswith='delete_')
        grupo_recepcionista.permissions.set(permisos_recepcionista)
        self.recepcionista.groups.add(grupo_recepcionista)
        grupo_consulta = Group.objects.create(name='Consulta')
        permisos_consulta = Permission.objects.filter(content_type__app_label__in=apps, codename__startswith='view_')
        grupo_consulta.permissions.set(permisos_consulta)
        self.consulta.groups.add(grupo_consulta)
        self.propietario_modelo = Propietario.objects.create(identificacion='101110111', nombre='Maria Lopez', telefono='88889999', email='maria@correo.test')
        self.veterinario_modelo = Veterinario.objects.create(identificacion_profesional='3101123456', nombre='Dra. Ana Solis', telefono='22223333', email='veterinaria@central.test')
        self.servicio_modelo = Servicio.objects.create(codigo='CON01', nombre='Consulta general', descripcion='Revision veterinaria general', tipo='Consulta', veterinario=self.veterinario_modelo, precio='1000.00', cupos=20)

    def crear_cita_con_detalle(self):
        cita = Cita.objects.create(propietario=self.propietario_modelo, fecha_cita=date(2026, 10, 12), fecha_atencion=date(2026, 10, 13))
        DetalleCita.objects.create(cita=cita, servicio=self.servicio_modelo, cantidad=2, precio_unitario='1000.00')
        return cita

    def test_crear_propietario(self):
        data = {'identificacion': '202220222', 'nombre': 'Carlos Mora', 'telefono': '87776666', 'email': 'carlos@correo.test'}
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_admin.key)
        response = self.client.post('/api/propietarios/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Propietario.objects.count(), 2)

    def test_actualizar_servicio(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_admin.key)
        response = self.client.patch(f'/api/servicios/{self.servicio_modelo.id}/', {'cupos': 30}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.servicio_modelo.refresh_from_db()
        self.assertEqual(self.servicio_modelo.cupos, 30)

    def test_listado_servicios_paginado(self):
        for numero in range(6):
            Servicio.objects.create(codigo=f'CAF{numero}', nombre=f'Vacuna {numero}', descripcion='Vacuna preventiva', tipo='Preventivo', veterinario=self.veterinario_modelo, precio='1500.00', cupos=10)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_consulta.key)
        response = self.client.get('/api/servicios/?page=1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()['resultados']), 5)

    def test_filtro_servicios_tipo_veterinario(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_consulta.key)
        response = self.client.get(f'/api/servicios/?tipo=Consulta&veterinario={self.veterinario_modelo.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['total_registros'], 1)

    def test_busqueda_propietarios(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_consulta.key)
        response = self.client.get('/api/propietarios/?buscar=Maria')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['total_registros'], 1)

    def test_crear_cita(self):
        data = {'propietario': self.propietario_modelo.id, 'fecha_cita': '2026-10-12', 'fecha_atencion': '2026-10-14', 'estado': 'PENDIENTE'}
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_recepcionista.key)
        response = self.client.post('/api/citas/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Cita.objects.count(), 1)

    def test_crear_detalle_resta_cupos(self):
        cita = Cita.objects.create(propietario=self.propietario_modelo, fecha_cita='2026-10-12', fecha_atencion='2026-10-14')
        data = {'servicio': self.servicio_modelo.id, 'cantidad': 3, 'precio_unitario': '1000.00'}
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_recepcionista.key)
        response = self.client.post(f'/api/citas/{cita.id}/detalles/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.servicio_modelo.refresh_from_db()
        self.assertEqual(self.servicio_modelo.cupos, 17)

    def test_pago_marca_cita_pagado(self):
        cita = self.crear_cita_con_detalle()
        data = {'cita': cita.id, 'fecha_pago': '2026-10-12', 'monto': '2000.00', 'metodo': 'EFECTIVO'}
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_recepcionista.key)
        response = self.client.post('/api/pagos/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        cita.refresh_from_db()
        self.assertEqual(cita.estado, 'PAGADO')

    def test_precio_negativo_retorna_400(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_admin.key)
        response = self.client.patch(f'/api/servicios/{self.servicio_modelo.id}/', {'precio': '-10.00'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cupos_negativo_retorna_400(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_admin.key)
        response = self.client.patch(f'/api/servicios/{self.servicio_modelo.id}/', {'cupos': -1}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_fecha_atencion_anterior_retorna_400(self):
        data = {'propietario': self.propietario_modelo.id, 'fecha_cita': '2026-10-12', 'fecha_atencion': '2026-10-10'}
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_recepcionista.key)
        response = self.client.post('/api/citas/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_propietario_inactivo_retorna_400(self):
        self.propietario_modelo.activo = False
        self.propietario_modelo.save()
        data = {'propietario': self.propietario_modelo.id, 'fecha_cita': '2026-10-12', 'fecha_atencion': '2026-10-14'}
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_recepcionista.key)
        response = self.client.post('/api/citas/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cupos_insuficiente_retorna_400(self):
        cita = Cita.objects.create(propietario=self.propietario_modelo, fecha_cita='2026-10-12', fecha_atencion='2026-10-14')
        data = {'servicio': self.servicio_modelo.id, 'cantidad': 99, 'precio_unitario': '1000.00'}
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_recepcionista.key)
        response = self.client.post(f'/api/citas/{cita.id}/detalles/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_pago_supera_saldo_retorna_400(self):
        cita = self.crear_cita_con_detalle()
        data = {'cita': cita.id, 'fecha_pago': '2026-10-12', 'monto': '3000.00', 'metodo': 'SINPE'}
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_recepcionista.key)
        response = self.client.post('/api/pagos/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_sin_token_retorna_401(self):
        response = self.client.get('/api/propietarios/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_consulta_no_puede_crear_retorna_403(self):
        data = {'identificacion': '303330333', 'nombre': 'Ana Perez', 'telefono': '81112222'}
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_consulta.key)
        response = self.client.post('/api/propietarios/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_recepcionista_no_puede_eliminar_retorna_403(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_recepcionista.key)
        response = self.client.delete(f'/api/servicios/{self.servicio_modelo.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_eliminar_propietario_con_cita_retorna_409(self):
        self.crear_cita_con_detalle()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_admin.key)
        response = self.client.delete(f'/api/propietarios/{self.propietario_modelo.id}/')
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_reporte_resumen(self):
        cita = self.crear_cita_con_detalle()
        Pago.objects.create(cita=cita, fecha_pago='2026-10-12', monto='2000.00', metodo='EFECTIVO')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_admin.key)
        response = self.client.get('/api/reportes/resumen/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['citas'], 1)
