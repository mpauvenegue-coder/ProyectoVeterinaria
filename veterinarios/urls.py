from django.urls import path
from . import views

urlpatterns = [
    path('', views.veterinarios_api, name='veterinarios_api'),
    path('<int:id>/', views.veterinario_detalle_api,name='veterinario_detalle_api'),
]