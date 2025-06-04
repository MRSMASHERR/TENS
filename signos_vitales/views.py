from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from datetime import datetime, timedelta
import json
from django.urls import reverse
from django.db import transaction
from django.utils.safestring import mark_safe

from .models import SignosVitales
from .forms import SignosVitalesForm
from pacientes.models import Paciente
from usuarios.models import Notificacion

@login_required
def registrar_signos_vitales(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    
    # Verificar si el paciente está dado de alta
    if not paciente.se_pueden_registrar_datos():
        messages.error(request, 'No se pueden registrar datos para pacientes dados de alta')
        return redirect('detalle_paciente', pk=paciente.id)
    
    if request.method == 'POST':
        form = SignosVitalesForm(request.POST)
        if form.is_valid():
            signos = form.save(commit=False)
            signos.paciente = paciente
            signos.registrado_por = request.user
            
            # Verificar si ya existe un registro para esta fecha y hora
            try:
                existente = SignosVitales.objects.get(
                    paciente=paciente,
                    fecha=signos.fecha,
                    hora=signos.hora
                )
                messages.warning(request, f'Ya existe un registro para {signos.fecha} a las {signos.hora}')
                return redirect('detalle_paciente', pk=paciente.id)
            except SignosVitales.DoesNotExist:
                # Guardar el registro con transacción para asegurar consistencia
                with transaction.atomic():
                    signos.save()
                    
                    # Obtener todas las alertas generadas durante la validación
                    alertas = form.get_alertas()
                    
                    if alertas:
                        # Crear mensaje para mostrar al usuario de manera más amigable
                        mensaje_alertas = "Se han detectado las siguientes alertas: "
                        mensaje_alertas += ", ".join(alertas)
                        
                        messages.warning(request, mark_safe(mensaje_alertas))
                        
                        # Crear notificación para el estudiante (usuario actual)
                        texto_notificacion = f"Alertas en signos vitales del paciente {paciente.nombre}"
                        
                        # Crear un mensaje detallado con los valores fuera de rango
                        detalle_notificacion = f"Valores fuera de rango para {paciente.nombre} ({paciente.rut}):\n\n"
                        for alerta in alertas:
                            detalle_notificacion += f"• {alerta}\n"
                        
                        detalle_notificacion += f"\nRegistrados el {signos.fecha} a las {signos.hora}."
                        
                        Notificacion.objects.create(
                            usuario=request.user,
                            titulo=texto_notificacion,
                            mensaje=detalle_notificacion,
                            tipo="WARNING",
                            url=reverse('historial_signos_vitales', args=[paciente.id])
                        )
                        
                        # Si existe un docente asociado al curso, enviar notificación también
                        if paciente.curso and paciente.curso.docente:
                            mensaje_docente = f"{request.user.get_full_name()} ha registrado los siguientes valores fuera de rango para el paciente {paciente.nombre}:\n\n"
                            for alerta in alertas:
                                mensaje_docente += f"• {alerta}\n"
                            
                            mensaje_docente += f"\nPresión arterial: {signos.presion_arterial}"
                            mensaje_docente += f"\nFrecuencia cardíaca: {signos.frecuencia_cardiaca}"
                            mensaje_docente += f"\nSaturación: {signos.saturacion}%"
                            mensaje_docente += f"\nFrecuencia respiratoria: {signos.frecuencia_respiratoria}"
                            mensaje_docente += f"\nTemperatura: {signos.temperatura}°C"
                            
                            if signos.hgt:
                                estado_hgt = signos.get_estado_hgt_display() if signos.estado_hgt else "No especificado"
                                mensaje_docente += f"\nHGT: {signos.hgt} mg/dL ({estado_hgt})"
                            
                            Notificacion.objects.create(
                                usuario=paciente.curso.docente,
                                titulo=texto_notificacion,
                                mensaje=mensaje_docente,
                                tipo="DANGER",
                                url=reverse('historial_signos_vitales', args=[paciente.id])
                            )
                
                messages.success(request, 'Signos vitales registrados exitosamente')
                return redirect('detalle_paciente', pk=paciente.id)
    else:
        form = SignosVitalesForm()
    
    return render(request, 'signos_vitales/registrar_signos.html', {
        'form': form,
        'paciente': paciente
    })

@login_required
def historial_signos_vitales(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    signos_vitales = SignosVitales.objects.filter(paciente=paciente).order_by('-fecha', 'hora')
    
    return render(request, 'signos_vitales/historial_signos.html', {
        'paciente': paciente,
        'signos_vitales': signos_vitales
    })

@login_required
def grafico_signos_vitales(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    
    # Obtener fechas del filtro
    fecha_fin = request.GET.get('fecha_fin')
    fecha_inicio = request.GET.get('fecha_inicio')
    
    # Si no hay fechas, usar últimos 7 días
    if not fecha_fin:
        fecha_fin = datetime.now().date()
    else:
        fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
        
    if not fecha_inicio:
        fecha_inicio = fecha_fin - timedelta(days=7)
    else:
        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
    
    # Filtrar signos vitales por fecha
    signos_vitales = SignosVitales.objects.filter(
        paciente=paciente,
        fecha__range=[fecha_inicio, fecha_fin]
    ).order_by('fecha', 'hora')
    
    # Preparar datos para gráficos
    fechas = []
    fc_data = []
    fr_data = []
    temp_data = []
    sat_data = []
    pa_sistolica = []
    pa_diastolica = []
    hgt_data = []
    
    for sv in signos_vitales:
        fecha_str = f"{sv.fecha.strftime('%Y-%m-%d')} {sv.hora}"
        fechas.append(fecha_str)
        fc_data.append(sv.frecuencia_cardiaca)
        fr_data.append(sv.frecuencia_respiratoria)
        temp_data.append(float(sv.temperatura))
        sat_data.append(sv.saturacion)
        hgt_data.append(sv.hgt if sv.hgt is not None else None)
        
        try:
            sistolica, diastolica = sv.presion_arterial.split('/')
            pa_sistolica.append(int(sistolica))
            pa_diastolica.append(int(diastolica))
        except:
            pa_sistolica.append(None)
            pa_diastolica.append(None)
    
    context = {
        'paciente': paciente,
        'fechas': json.dumps(fechas),
        'fc_data': json.dumps(fc_data),
        'fr_data': json.dumps(fr_data),
        'temp_data': json.dumps(temp_data),
        'sat_data': json.dumps(sat_data),
        'pa_sistolica': json.dumps(pa_sistolica),
        'pa_diastolica': json.dumps(pa_diastolica),
        'hgt_data': json.dumps(hgt_data),
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin
    }
    
    return render(request, 'signos_vitales/grafico_signos.html', context)
