from django.contrib import admin

# Register your models here.
from servicios_adapta_app.models import Proyecto, Punto, Medicion, experiencia_Categoria, experiencia_Cliente, experiencia_Contacto, experiencia_Contrato, experiencia_Localizacion, experiencia_Proyecto

admin.site.register(Proyecto)
admin.site.register(Punto)
admin.site.register(Medicion)
admin.site.register(experiencia_Cliente)
admin.site.register(experiencia_Contacto)
admin.site.register(experiencia_Categoria)
admin.site.register(experiencia_Localizacion)
admin.site.register(experiencia_Proyecto)
admin.site.register(experiencia_Contrato)