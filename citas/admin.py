from django.contrib import admin

from .models import DetalleCita, Cita

admin.site.register(Cita)
admin.site.register(DetalleCita)