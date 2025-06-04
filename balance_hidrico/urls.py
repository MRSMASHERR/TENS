from django.urls import path
from . import views

urlpatterns = [
    path('registrar/<int:paciente_id>/', views.registrar_balance, name='registrar_balance'),
    path('historial/<int:paciente_id>/', views.historial_balance, name='historial_balance'),
] 