from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Evolucion
from .forms import EvolucionForm
from pacientes.models import Paciente

@login_required
def registrar_evolucion(request, paciente_id):
    # Obtener paciente y fecha actual para registrar evolución
    paciente = get_object_or_404(Paciente, id=paciente_id)
    
    # Verificar si el paciente está dado de alta y el usuario no es administrador
    if not paciente.se_pueden_registrar_datos() and request.user.rol != 'administrador':
        messages.error(request, 'No se pueden registrar datos para pacientes dados de alta')
        return redirect('detalle_paciente', pk=paciente.id)
    
    if request.method == 'POST':
        form = EvolucionForm(request.POST)
        if form.is_valid():
            evolucion = form.save(commit=False)
            evolucion.paciente = paciente
            evolucion.responsable = request.user
            evolucion.save()
            messages.success(request, 'Evolución registrada exitosamente')
            return redirect('detalle_paciente', pk=paciente.id)
    else:
        form = EvolucionForm()
    
    return render(request, 'evoluciones/registrar_evolucion.html', {
        'form': form,
        'paciente': paciente
    })

@login_required
def historial_evoluciones(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    evoluciones = Evolucion.objects.filter(paciente=paciente).order_by('-fecha', '-hora')
    
    # Diferenciar entre evoluciones de estudiantes y docentes
    evoluciones_estudiantes = evoluciones.filter(responsable__rol='estudiante')
    evoluciones_docentes = evoluciones.filter(responsable__rol='docente')
    
    return render(request, 'evoluciones/historial_evoluciones.html', {
        'paciente': paciente,
        'evoluciones': evoluciones,
        'evoluciones_estudiantes': evoluciones_estudiantes,
        'evoluciones_docentes': evoluciones_docentes
    })
