from django.urls import path
from . import views

urlpatterns = [
    path('', views.propietarios_api, name='propietarios_api'),
    path('<int:id>/', views.propietario_detalle_api, name='propietario_detalle_api'),
]
