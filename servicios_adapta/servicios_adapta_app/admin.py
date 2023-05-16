from django.contrib import admin

# Register your models here.
from servicios_adapta_app.models import Proyecto, Punto, Medicion

admin.site.register(Proyecto)
admin.site.register(Punto)
admin.site.register(Medicion)