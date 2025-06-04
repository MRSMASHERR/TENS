from django.urls import path
from . import views

urlpatterns = [
    path('registrar/<int:paciente_id>/', views.registrar_signos_vitales, name='registrar_signos_vitales'),
    path('historial/<int:paciente_id>/', views.historial_signos_vitales, name='historial_signos_vitales'),
    path('grafico/<int:paciente_id>/', views.grafico_signos_vitales, name='grafico_signos_vitales'),
] 