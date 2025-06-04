from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import BalanceHidrico
from .forms import BalanceHidricoForm
from pacientes.models import Paciente

# Create your views here.

@login_required
def registrar_balance(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    
    # Verificar si el paciente está dado de alta y el usuario no es administrador
    if not paciente.se_pueden_registrar_datos() and request.user.rol != 'administrador':
        messages.error(request, 'No se pueden registrar datos para pacientes dados de alta')
        return redirect('detalle_paciente', pk=paciente.id)
    
    if request.method == 'POST':
        form = BalanceHidricoForm(request.POST)
        if form.is_valid():
            balance = form.save(commit=False)
            balance.paciente = paciente
            balance.registrado_por = request.user
            
            # Verificar si ya existe un registro para esta fecha y hora
            try:
                existente = BalanceHidrico.objects.get(
                    paciente=paciente,
                    fecha=balance.fecha,
                    hora=balance.hora
                )
                messages.warning(request, f'Ya existe un registro para {balance.fecha} a las {balance.hora}')
                return redirect('detalle_paciente', pk=paciente.id)
            except BalanceHidrico.DoesNotExist:
                balance.save()
                messages.success(request, 'Balance hídrico registrado exitosamente')
                return redirect('detalle_paciente', pk=paciente.id)
    else:
        form = BalanceHidricoForm()
    
    return render(request, 'balance_hidrico/registrar_balance.html', {
        'form': form,
        'paciente': paciente
    })

@login_required
def historial_balance(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    balances = BalanceHidrico.objects.filter(paciente=paciente).order_by('-fecha', 'hora')
    
    # Calcular balance total del día
    balances_por_dia = {}
    for balance in balances:
        fecha = balance.fecha
        if fecha not in balances_por_dia:
            balances_por_dia[fecha] = {
                'ingresos': 0,
                'egresos': 0,
                'balance': 0
            }
        
        balances_por_dia[fecha]['ingresos'] += balance.total_ingresos
        balances_por_dia[fecha]['egresos'] += balance.total_egresos
        balances_por_dia[fecha]['balance'] += balance.balance_total
    
    return render(request, 'balance_hidrico/historial_balance.html', {
        'paciente': paciente,
        'balances': balances,
        'balances_por_dia': balances_por_dia
    })
