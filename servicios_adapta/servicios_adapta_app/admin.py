from django.contrib import admin

# Register your models here.
from servicios_adapta_app.models import Proyecto, Punto, Medicion, experienciaContrato, experienciaRazonSocial, experienciaProyecto, experienciaLocalizaciones, experienciaEmpleado, experienciaRol, ContratoEmpleado

admin.site.register(Proyecto)
admin.site.register(Punto)
admin.site.register(Medicion)
admin.site.register(experienciaContrato)
admin.site.register(experienciaRazonSocial)
admin.site.register(experienciaProyecto)
admin.site.register(experienciaLocalizaciones)
admin.site.register(experienciaEmpleado)
admin.site.register(experienciaRol)
admin.site.register(ContratoEmpleado)
