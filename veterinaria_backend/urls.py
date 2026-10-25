"""
URL configuration for veterinaria_backend project.
"""

from django.contrib import admin
from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token

from citas.views import (
    perfil_api,
    reportes_resumen_api,
    reportes_propietarios_atenciones_api,
    reportes_citas_propietario_api,
    sesion_api,
)
from servicios.views import (
    reportes_servicios_bajo_cupos_api,
    reportes_servicios_veterinario_api,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', obtain_auth_token, name='api_token'),
    path('api/perfil/', perfil_api, name='perfil_api'),
    path('api/sesion/', sesion_api, name='sesion_api'),

    path('api/propietarios/', include('propietarios.urls')),
    path('api/veterinarios/', include('veterinarios.urls')),
    path('api/servicios/', include('servicios.urls')),
    path('api/citas/', include('citas.urls')),
    path('api/pagos/', include('pagos.urls')),

    path('api/reportes/resumen/', reportes_resumen_api,
         name='reportes_resumen_api'),
    path('api/reportes/propietarios-atenciones/', reportes_propietarios_atenciones_api,
         name='reportes_propietarios_atenciones_api'),
    path('api/reportes/servicios-bajo-cupos/',
         reportes_servicios_bajo_cupos_api,
         name='reportes_servicios_bajo_cupos_api'),
    path('api/reportes/citas-propietario/<int:id>/',
         reportes_citas_propietario_api,
         name='reportes_citas_propietario_api'),
    path('api/reportes/servicios-veterinario/<int:id>/',
         reportes_servicios_veterinario_api,
         name='reportes_servicios_veterinario_api'),
]