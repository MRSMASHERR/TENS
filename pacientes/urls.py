from django.urls import path
from . import views

urlpatterns = [
    path('registrar/<int:curso_id>/', views.registrar_paciente, name='registrar_paciente'),
    path('lista/', views.ListaPacientesView.as_view(), name='lista_pacientes'),
    path('lista/curso/<int:curso_id>/', views.ListaPacientesView.as_view(), name='lista_pacientes_curso'),
    path('lista/readonly/', views.ListaPacientesReadOnlyView.as_view(), name='lista_pacientes_readonly'),
    path('lista/readonly/curso/<int:curso_id>/', views.ListaPacientesReadOnlyView.as_view(), name='lista_pacientes_readonly_curso'),
    path('alta/lista/', views.ListaPacientesAltaView.as_view(), name='lista_pacientes_alta'),
    path('alta/lista/curso/<int:curso_id>/', views.ListaPacientesAltaView.as_view(), name='lista_pacientes_alta_curso'),
    path('alta/lista/readonly/', views.ListaPacientesAltaReadOnlyView.as_view(), name='lista_pacientes_alta_readonly'),
    path('alta/lista/readonly/curso/<int:curso_id>/', views.ListaPacientesAltaReadOnlyView.as_view(), name='lista_pacientes_alta_readonly_curso'),
    path('detalle/<int:pk>/', views.DetallePacienteView.as_view(), name='detalle_paciente'),
    path('detalle/readonly/<int:pk>/', views.DetallePacienteReadOnlyView.as_view(), name='detalle_paciente_readonly'),
    path('editar/<int:pk>/', views.editar_paciente, name='editar_paciente'),
    path('mis-pacientes/', views.mis_pacientes, name='mis_pacientes'),
    path('mis-pacientes/curso/<int:curso_id>/', views.mis_pacientes, name='mis_pacientes_curso'),
    path('alta/<int:pk>/', views.dar_de_alta_paciente, name='dar_de_alta_paciente'),
    path('readmitir/<int:pk>/', views.readmitir_paciente, name='readmitir_paciente'),
    # Dispositivos
    path('<int:paciente_id>/dispositivo/registrar/', views.registrar_dispositivo, name='registrar_dispositivo'),
    path('dispositivo/eliminar/<int:dispositivo_id>/', views.eliminar_dispositivo, name='eliminar_dispositivo'),
    # Ficha clínica
    path('ficha/<int:pk>/', views.descargar_ficha_pdf, name='ficha_clinica'),
] 