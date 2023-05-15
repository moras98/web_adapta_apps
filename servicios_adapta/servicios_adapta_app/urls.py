from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('filtrado-aire/', views.air_data_filter, name='filtrado-aire'),
    path('filtrado-ruido/', views.noise_processing, name='filtrado-ruido'),
    path('login/',views.login_view, name='login'),
]
