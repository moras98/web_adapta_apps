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
    path('login/',views.login_view, name='login'),
]
