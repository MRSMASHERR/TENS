from django.urls import path
from . import views

urlpatterns = [
    path('registrar/<int:paciente_id>/', views.registrar_evolucion, name='registrar_evolucion'),
    path('historial/<int:paciente_id>/', views.historial_evoluciones, name='historial_evoluciones'),
]
 