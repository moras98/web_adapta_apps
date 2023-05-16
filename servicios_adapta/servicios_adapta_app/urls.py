from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('filtrado-aire/', views.air_data_filter, name='filtrado-aire'),
    path('ruido/', views.menuRuido, name='menu-ruido'),
    path('filtrado/', views.noise_processing, name='filtrado-ruido'),
    path('tabla-mediciones/', views.mediciones_view, name='tabla_mediciones'),
    path('agregar-mediciones/', views.add_medicion, name='agregar-medicion'),
    path('login/',views.login_view, name='login'),
]
