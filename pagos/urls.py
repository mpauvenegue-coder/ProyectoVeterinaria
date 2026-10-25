from django.urls import path
from . import views

urlpatterns = [
    path('', views.pagos_api, name='pagos_api'),
    path('<int:id>/', views.pago_detalle_api, name='pago_detalle_api'),
]