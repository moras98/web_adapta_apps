from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('filtrado-aire/', views.air_data_filter, name='filtrado-aire'),
    path('ruido/', views.menuRuido, name='menu-ruido'),
    path('ruido/filtrado/', views.noise_processing, name='filtrado-ruido'),
    path('ruido/resultados-gvcfcc/', views.resultadosEFFO, name='res-effo'),
    path('ruido/tabla-mediciones/', views.mediciones_view, name='tabla_mediciones'),
    path('ruido/tabla-mediciones/agregar-mediciones/', views.add_medicion, name='agregar-medicion'),
    path('medicion/borrar/<int:medicion_id>/', views.borrar_medicion, name='borrar_medicion'),
    path('experiencia/', views.menuExperiencia, name='menu-experiencia'),
    path('experiencia/razones-sociales', views.experienciaRazones, name='experiencia-razones'),
    path('experiencia/razones-sociales/agregar', views.add_razon, name='experiencia-razones-agregar'),
    path('experiencia/razones-sociales/borrar/<int:razon_id>/', views.borrar_razon, name='borrar_razon'),
    path('experiencia/proyectos', views.experienciaProyectos, name='experiencia-proyectos'),
    path('experiencia/proyectos/agregar', views.add_proyecto, name='experiencia-proyectos-agregar'),
    path('experiencia/proyectos/borrar/<int:proyecto_id>/', views.borrar_proyecto, name='borrar_proyecto'),
    path('experiencia/tabla/', views.experienciaTabla, name='experiencia-tabla'),
    path('experiencia/tabla/agregar', views.add_contrato, name='experiencia-agregar'),
    path('experiencia/tabla/editar/<int:contrato_id>/', views.editar_contrato, name='experiencia-editar'),
    path('experiencia/tabla/editar/guardar_contrato/<int:contrato_id>/', views.guardar_contrato, name='guardar_contrato'),
    path('experiencia/tabla/borrar/<int:contrato_id>/', views.borrar_contrato, name='borrar_contrato'),
    path('login/',views.login_view, name='login'),
    path('experiencia/proyectos_filtrados/', views.proyectos_filtrados, name='proyectos_filtrados'),
]
