from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from datetime import date
from pacientes.models import Paciente
from pacientes.forms import DispositivoForm

@login_required
def registrar_dispositivo(request, paciente_id):
    # Obtener paciente y fecha actual para registrar dispositivo
    paciente = get_object_or_404(Paciente, id=paciente_id)
    
    # Verificar si el paciente está dado de alta y el usuario no es administrador
    if not paciente.se_pueden_registrar_datos() and request.user.rol != 'administrador':
        messages.error(request, 'No se pueden registrar datos para pacientes dados de alta')
        return redirect('detalle_paciente', pk=paciente.id)
    
    if request.method == 'POST':
        form = DispositivoForm(request.POST)
        
        # Extraer valores del POST para verificar
        categoria = request.POST.get('categoria')
        
        tipo_campo = None
        if categoria == 'SONDA':
            tipo_campo = 'tipo_sonda'
        elif categoria == 'VIA_AEREA':
            tipo_campo = 'tipo_via_aerea'
        elif categoria == 'VVP':
            tipo_campo = 'tipo_vvp'
        elif categoria == 'DRENAJE':
            tipo_campo = 'tipo_drenaje'
            
        tipo_valor = request.POST.get(tipo_campo) if tipo_campo else None
        fecha_instalacion = request.POST.get('fecha_instalacion')
        
        # Si algún valor esencial está vacío, aplicar valores por defecto
        data = request.POST.copy()
        if categoria and not tipo_valor:
            if categoria == 'SONDA':
                data['tipo_sonda'] = 'FOLEY_FR_16'
            elif categoria == 'VIA_AEREA':
                data['tipo_via_aerea'] = 'CANULA_MAYO'
            elif categoria == 'VVP':
                data['tipo_vvp'] = 'BRANULA_18G'
            elif categoria == 'DRENAJE':
                data['tipo_drenaje'] = 'TORACICO'
            
        # Si no hay fecha, usar la fecha actual
        if not fecha_instalacion:
            data['fecha_instalacion'] = date.today().strftime('%Y-%m-%d')
            
        # Crear nuevo formulario con datos corregidos si fue necesario
        if data != request.POST:
            form = DispositivoForm(data)
        
        if form.is_valid():
            dispositivo = form.save(commit=False)
            dispositivo.paciente = paciente
            dispositivo.registrado_por = request.user
            
            # Guardar el dispositivo
            dispositivo.save()
            
            # Mostrar mensaje sobre la fecha de retiro automático
            if dispositivo.fecha_retiro:
                fecha_retiro = dispositivo.fecha_retiro.strftime('%d/%m/%Y')
                messages.info(
                    request, 
                    f'El dispositivo se retirará automáticamente el {fecha_retiro} '
                    f'({dispositivo.dias_instalacion} días desde la instalación)'
                )
            
            messages.success(request, 'Dispositivo registrado exitosamente')
            return redirect('detalle_paciente', pk=paciente.id)
        else:
            for field, errors in form.errors.items():
                messages.error(request, f"Error en {field}: {', '.join(errors)}")
    else:
        # Establecer valores iniciales para el formulario
        inicial = {
            'categoria': 'SONDA',
            'tipo_sonda': 'FOLEY',
            'fecha_instalacion': date.today(),
            'dias_instalacion': 1
        }
        form = DispositivoForm(initial=inicial)
    
    context = {
        'form': form,
        'paciente': paciente,
        'is_admin': request.user.rol == 'administrador'
    }
    
    return render(request, 'pacientes/registrar_dispositivo.html', context) 