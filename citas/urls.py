from django.urls import path
from . import views

urlpatterns = [
    path('', views.citas_api, name='citas_api'),
    path('detalles/<int:id>/', views.detalle_cita_detalle_api,name='detalle_cita_detalle_api'),
    path('<int:id>/', views.cita_detalle_api, name='cita_detalle_api'),
    path('<int:id>/detalles/', views.detalles_cita_api,name='detalles_cita_api'),
]