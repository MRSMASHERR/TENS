from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views import View
from django.views.generic import DetailView
from django.db.models import Q
from django.utils import timezone
from django.http import HttpResponse, Http404
from datetime import datetime, date

from .models import Paciente, Dispositivo
from .forms import PacienteForm, BusquedaPacienteForm, DispositivoForm, DarDeAltaForm
from usuarios.models import Usuario, Curso
from signos_vitales.models import SignosVitales
from signos_vitales.forms import SignosVitalesForm
from balance_hidrico.models import BalanceHidrico
from balance_hidrico.forms import BalanceHidricoForm
from evoluciones.models import Evolucion
from evoluciones.forms import EvolucionForm
from .utils import generate_ficha_clinica_pdf

@login_required
def registrar_paciente(request, curso_id):
    # Verificar que el usuario tenga acceso al curso
    curso = get_object_or_404(Curso, id=curso_id)
    if not curso.estudiantes.filter(id=request.user.id).exists() and not curso.docente == request.user and request.user.rol != 'administrador':
        raise Http404("No tienes acceso a este curso")

    if request.method == 'POST':
        form = PacienteForm(request.POST, curso=curso)
        if form.is_valid():
            paciente = form.save(commit=False)
            paciente.registrado_por = request.user
            paciente.curso = curso
            
            # Procesar el valor de género otro si es necesario
            if paciente.genero == 'O' and form.cleaned_data.get('genero_otro'):
                paciente.genero_otro = form.cleaned_data.get('genero_otro')
                
            # Procesar el valor de previsión otra si es necesario
            if paciente.prevision == 'OTRAS' and form.cleaned_data.get('prevision_otra'):
                paciente.prevision_otra = form.cleaned_data.get('prevision_otra')
                
            paciente.save()
            messages.success(request, 'Paciente registrado exitosamente')
            return redirect('detalle_curso', curso_id=curso.id)
    else:
        form = PacienteForm(curso=curso)
    
    context = {
        'form': form,
        'curso': curso
    }
    return render(request, 'pacientes/registrar_paciente.html', context)

class ListaPacientesView(LoginRequiredMixin, View):
    def get(self, request, curso_id=None):
        # Obtener parámetros de búsqueda
        busqueda = request.GET.get('busqueda', '')
        form_busqueda = BusquedaPacienteForm(initial={'busqueda': busqueda})
        
        # Filtrar pacientes activos (sin fecha de alta)
        pacientes = Paciente.objects.filter(fecha_alta__isnull=True)
        
        # Si se proporciona curso_id, filtrar por curso
        curso = None
        if curso_id:
            curso = get_object_or_404(Curso, id=curso_id)
            # Los administradores pueden acceder a cualquier curso
            if not curso.estudiantes.filter(id=request.user.id).exists() and not curso.docente == request.user and request.user.rol != 'administrador':
                raise Http404("No tienes acceso a este curso")
            pacientes = pacientes.filter(curso=curso)
        else:
            # Si el usuario es docente, filtrar solo por sus cursos
            if request.user.rol == 'docente':
                cursos_docente = Curso.objects.filter(docente=request.user)
                pacientes = pacientes.filter(curso__in=cursos_docente)
            # Si el usuario es administrador, no filtrar por curso
            elif request.user.rol != 'administrador':
                # Para otros roles (que no sean admin), aplicar filtros normales
                if request.user.rol == 'estudiante':
                    cursos_estudiante = request.user.cursos_inscritos.all()
                    pacientes = pacientes.filter(curso__in=cursos_estudiante)
        
        # Aplicar filtro de búsqueda si existe
        if busqueda:
            pacientes = pacientes.filter(
                Q(nombre__icontains=busqueda) | 
                Q(rut__icontains=busqueda) | 
                Q(sala_cama__icontains=busqueda)
            )
        
        # Agrupar pacientes por curso
        pacientes_por_curso = []
        
        if curso_id:
            # Si tenemos un curso específico, solo mostramos esos pacientes
            pacientes_curso = pacientes.order_by('nombre')
            if pacientes_curso.exists():
                pacientes_por_curso.append((curso, pacientes_curso))
        else:
            # Si el usuario es docente, mostrar solo sus cursos
            if request.user.rol == 'docente':
                cursos_con_pacientes = Curso.objects.filter(docente=request.user, pacientes__in=pacientes).distinct()
            else:
                # Para otros roles, obtener todos los cursos con pacientes
                cursos_con_pacientes = Curso.objects.filter(pacientes__in=pacientes).distinct()
            
            # Pacientes agrupados por cada curso
            for curso in cursos_con_pacientes:
                pacientes_curso = pacientes.filter(curso=curso).order_by('nombre')
                pacientes_por_curso.append((curso, pacientes_curso))
            
            # Pacientes sin curso asignado (solo mostrar si no es docente)
            if request.user.rol != 'docente':
                pacientes_sin_curso = pacientes.filter(curso__isnull=True).order_by('nombre')
                if pacientes_sin_curso.exists():
                    pacientes_por_curso.append((None, pacientes_sin_curso))
        
        # Calcular días de hospitalización para cada paciente
        for _, pacientes_grupo in pacientes_por_curso:
            for paciente in pacientes_grupo:
                paciente.dias_hospitalizacion = (timezone.now().date() - paciente.fecha_ingreso).days
        
        context = {
            'pacientes_por_curso': pacientes_por_curso,
            'form_busqueda': form_busqueda,
            'total_pacientes': pacientes.count(),
            'curso': curso,
            'is_admin': request.user.rol == 'administrador'
        }
        return render(request, 'pacientes/lista_pacientes.html', context)

class DetallePacienteView(LoginRequiredMixin, DetailView):
    model = Paciente
    template_name = 'pacientes/detalle_paciente.html'
    context_object_name = 'paciente'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Los administradores tienen acceso a todos los pacientes
        if obj.curso and self.request.user.rol != 'administrador':
            if not obj.curso.estudiantes.filter(id=self.request.user.id).exists() and not obj.curso.docente == self.request.user:
                raise Http404("No tienes acceso a este paciente")
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['curso'] = self.object.curso
        # Indicar si la vista es para un administrador
        context['is_admin'] = self.request.user.rol == 'administrador'
        # Añadir fecha actual para comparaciones en la plantilla
        context['today'] = date.today()
        return context

@login_required
def editar_paciente(request, pk):
    paciente = get_object_or_404(Paciente, pk=pk)
    
    # Verificar acceso al paciente si está asociado a un curso (excepto para administradores)
    if paciente.curso and request.user.rol != 'administrador':
        if not paciente.curso.estudiantes.filter(id=request.user.id).exists() and not paciente.curso.docente == request.user:
            raise Http404("No tienes acceso a este paciente")
    
    if request.method == 'POST':
        form = PacienteForm(request.POST, instance=paciente, curso=paciente.curso)
        if form.is_valid():
            paciente = form.save(commit=False)
            
            # Procesar el valor de género otro si es necesario
            if paciente.genero == 'O' and form.cleaned_data.get('genero_otro'):
                paciente.genero_otro = form.cleaned_data.get('genero_otro')
            elif paciente.genero != 'O':
                paciente.genero_otro = None  # Limpiar el campo si no se selecciona Otro
                
            # Procesar el valor de previsión otra si es necesario
            if paciente.prevision == 'OTRAS' and form.cleaned_data.get('prevision_otra'):
                paciente.prevision_otra = form.cleaned_data.get('prevision_otra')
            elif paciente.prevision != 'OTRAS':
                paciente.prevision_otra = None  # Limpiar el campo si no se selecciona Otras
                
            paciente.save()
            messages.success(request, 'Paciente actualizado exitosamente')
            if paciente.curso:
                return redirect('detalle_curso', curso_id=paciente.curso.id)
            return redirect('detalle_paciente', pk=paciente.pk)
    else:
        form = PacienteForm(instance=paciente, curso=paciente.curso)
    
    return render(request, 'pacientes/editar_paciente.html', {
        'form': form, 
        'paciente': paciente,
        'curso': paciente.curso,
        'is_admin': request.user.rol == 'administrador'
    })

@login_required
def mis_pacientes(request, curso_id=None):
    # Si se proporciona curso_id, mostrar solo los pacientes de ese curso
    if curso_id:
        curso = get_object_or_404(Curso, id=curso_id)
        if not curso.estudiantes.filter(id=request.user.id).exists() and not curso.docente == request.user and request.user.rol != 'administrador':
            raise Http404("No tienes acceso a este curso")
        pacientes = Paciente.objects.filter(curso=curso).order_by('-fecha_ingreso')
    else:
        # Si el usuario es admin, mostrar todos los pacientes
        if request.user.rol == 'administrador':
            pacientes = Paciente.objects.all().order_by('-fecha_ingreso')
        # Si el usuario es docente, mostrar pacientes de sus cursos
        elif request.user.rol == 'docente':
            cursos = Curso.objects.filter(docente=request.user)
            pacientes = Paciente.objects.filter(curso__in=cursos).order_by('-fecha_ingreso')
        # Si el usuario es estudiante, mostrar pacientes de cursos inscritos
        elif request.user.rol == 'estudiante':
            cursos = request.user.cursos_inscritos.all()
            pacientes = Paciente.objects.filter(curso__in=cursos).order_by('-fecha_ingreso')
        # Fallback: pacientes registrados por el usuario sin curso
        else:
            pacientes = Paciente.objects.filter(registrado_por=request.user, curso__isnull=True).order_by('-fecha_ingreso')
    
    context = {
        'pacientes': pacientes,
        'total_pacientes': pacientes.count(),
        'pacientes_activos': pacientes.filter(activo=True).count(),
        'curso': curso if curso_id else None,
        'is_admin': request.user.rol == 'administrador'
    }
    
    return render(request, 'pacientes/mis_pacientes.html', context)

@login_required
def registrar_dispositivo(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    
    # Verificar si el paciente está dado de alta y el usuario no es administrador
    if paciente.fecha_alta and request.user.rol != 'administrador':
        messages.error(request, "No se pueden registrar dispositivos en pacientes dados de alta")
        return redirect('detalle_paciente', pk=paciente.id)
    
    if request.method == 'POST':
        form = DispositivoForm(request.POST)
        print(f"Datos del formulario POST: {request.POST}")
        
        # Extraer valores del POST para verificar
        categoria = request.POST.get('categoria')
        print(f"POST: categoría={categoria}")
        
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
        print(f"POST: {tipo_campo}={tipo_valor}")
        
        fecha_instalacion = request.POST.get('fecha_instalacion')
        print(f"POST: fecha_instalacion={fecha_instalacion}")
        
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
            print(f"Aplicado valor por defecto para {tipo_campo}")
            
        # Si no hay fecha, usar la fecha actual
        if not fecha_instalacion:
            data['fecha_instalacion'] = date.today().strftime('%Y-%m-%d')
            print(f"Aplicada fecha de instalación por defecto: {data['fecha_instalacion']}")
            
        # Crear nuevo formulario con datos corregidos si fue necesario
        if data != request.POST:
            form = DispositivoForm(data)
        
        if form.is_valid():
            dispositivo = form.save(commit=False)
            dispositivo.paciente = paciente
            dispositivo.registrado_por = request.user
            
            # Log para depuración
            print(f"GUARDANDO: Categoría: {dispositivo.categoria}")
            if dispositivo.categoria == 'SONDA':
                print(f"GUARDANDO: Tipo de sonda: {dispositivo.tipo_sonda}")
            elif dispositivo.categoria == 'VIA_AEREA':
                print(f"GUARDANDO: Tipo de vía aérea: {dispositivo.tipo_via_aerea}")
            elif dispositivo.categoria == 'VVP':
                print(f"GUARDANDO: Tipo de VVP: {dispositivo.tipo_vvp}")
            elif dispositivo.categoria == 'DRENAJE':
                print(f"GUARDANDO: Tipo de drenaje: {dispositivo.tipo_drenaje}")
            
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
            print(f"Errores en el formulario: {form.errors}")
            for field, errors in form.errors.items():
                messages.error(request, f"Error en {field}: {', '.join(errors)}")
    else:
        # Establecer valores iniciales para el formulario
        inicial = {
            'categoria': 'SONDA',
            'tipo_sonda': 'FOLEY_FR_16',
            'fecha_instalacion': date.today(),
            'dias_instalacion': 1
        }
        form = DispositivoForm(initial=inicial)
        print(f"Formulario creado con valores iniciales: {inicial}")
    
    context = {
        'form': form,
        'paciente': paciente,
        'is_admin': request.user.rol == 'administrador'
    }
    
    return render(request, 'pacientes/registrar_dispositivo.html', context)

@login_required
def eliminar_dispositivo(request, dispositivo_id):
    dispositivo = get_object_or_404(Dispositivo, id=dispositivo_id)
    paciente_id = dispositivo.paciente.id
    dispositivo.delete()
    messages.success(request, 'Dispositivo eliminado exitosamente')
    return redirect('detalle_paciente', pk=paciente_id)

@login_required
def descargar_ficha_pdf(request, pk):
    """Vista para descargar la ficha clínica de un paciente en formato PDF."""
    paciente = get_object_or_404(Paciente, pk=pk)
    
    # Obtener fecha para filtrar (por defecto es hoy)
    fecha_str = request.GET.get('fecha')
    if fecha_str:
        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            fecha = datetime.now().date()
    else:
        fecha = datetime.now().date()
    
    # Obtener los datos necesarios para generar el PDF filtrados por fecha
    signos_vitales = SignosVitales.objects.filter(paciente=paciente, fecha=fecha).order_by('hora')
    balances = BalanceHidrico.objects.filter(paciente=paciente, fecha=fecha).order_by('hora')
    evoluciones = Evolucion.objects.filter(paciente=paciente, fecha=fecha).order_by('-hora')
    
    # Si es una solicitud para descargar
    if request.GET.get('download') == 'true':
        # Generar el PDF
        pdf_buffer = generate_ficha_clinica_pdf(paciente, signos_vitales, balances, evoluciones)
        
        # Crear la respuesta HTTP con el PDF
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="ficha_clinica_{paciente.rut}_{fecha}.pdf"'
        
        return response
    
    # Si es solo vista previa, obtener fechas disponibles
    fechas_disponibles = set()
    
    # Obtener fechas únicas de registros
    fechas_signos = SignosVitales.objects.filter(paciente=paciente).values_list('fecha', flat=True).distinct()
    fechas_balance = BalanceHidrico.objects.filter(paciente=paciente).values_list('fecha', flat=True).distinct()
    fechas_evolucion = Evolucion.objects.filter(paciente=paciente).values_list('fecha', flat=True).distinct()
    
    # Combinar todas las fechas en un solo conjunto
    for fecha_registro in list(fechas_signos) + list(fechas_balance) + list(fechas_evolucion):
        fechas_disponibles.add(fecha_registro)
    
    # Convertir a lista y ordenar
    fechas_disponibles = sorted(list(fechas_disponibles), reverse=True)
    
    # Renderizar la vista previa
    return render(request, 'pacientes/vista_previa_ficha.html', {
        'paciente': paciente,
        'signos_vitales': signos_vitales,
        'balances': balances,
        'evoluciones': evoluciones,
        'fecha_seleccionada': fecha,
        'fechas_disponibles': fechas_disponibles
    })

@login_required
def dar_de_alta_paciente(request, pk):
    """Vista para dar de alta a un paciente"""
    paciente = get_object_or_404(Paciente, pk=pk)
    
    # Verificar acceso al paciente si está asociado a un curso (excepto administradores)
    if paciente.curso and request.user.rol != 'administrador':
        if not paciente.curso.estudiantes.filter(id=request.user.id).exists() and not paciente.curso.docente == request.user:
            raise Http404("No tienes acceso a este paciente")
    
    # Si el paciente ya está dado de alta, redirigir
    if paciente.fecha_alta:
        messages.info(request, f'El paciente {paciente.nombre} ya fue dado de alta el {paciente.fecha_alta}')
        return redirect('detalle_paciente', pk=paciente.pk)
    
    if request.method == 'POST':
        form = DarDeAltaForm(request.POST)
        if form.is_valid():
            form.dar_de_alta(paciente)
            messages.success(request, f'El paciente {paciente.nombre} ha sido dado de alta exitosamente')
            if paciente.curso:
                return redirect('lista_pacientes_curso', curso_id=paciente.curso.id)
            return redirect('mis_pacientes')
    else:
        form = DarDeAltaForm()
    
    context = {
        'form': form,
        'paciente': paciente,
        'is_admin': request.user.rol == 'administrador'
    }
    return render(request, 'pacientes/dar_de_alta.html', context)

@login_required
def readmitir_paciente(request, pk):
    """Vista para readmitir a un paciente que fue dado de alta"""
    paciente = get_object_or_404(Paciente, pk=pk)
    
    # Verificar acceso al paciente si está asociado a un curso (excepto administradores)
    if paciente.curso and request.user.rol != 'administrador':
        if not paciente.curso.estudiantes.filter(id=request.user.id).exists() and not paciente.curso.docente == request.user:
            raise Http404("No tienes acceso a este paciente")
    
    # Sólo los administradores pueden readmitir pacientes
    if request.user.rol != 'administrador':
        messages.error(request, "Solo los administradores pueden readmitir pacientes")
        return redirect('detalle_paciente', pk=paciente.pk)
    
    # Si el paciente no está dado de alta, redirigir
    if not paciente.fecha_alta:
        messages.info(request, f'El paciente {paciente.nombre} no está dado de alta')
        return redirect('detalle_paciente', pk=paciente.pk)
    
    if request.method == 'POST':
        paciente.readmitir()
        messages.success(request, f'El paciente {paciente.nombre} ha sido readmitido exitosamente')
        if paciente.curso:
            return redirect('lista_pacientes_curso', curso_id=paciente.curso.id)
        return redirect('mis_pacientes')
    
    context = {
        'paciente': paciente,
        'is_admin': request.user.rol == 'administrador'
    }
    return render(request, 'pacientes/readmitir.html', context)

class ListaPacientesAltaView(LoginRequiredMixin, View):
    def get(self, request, curso_id=None):
        # Obtener parámetros de búsqueda
        busqueda = request.GET.get('busqueda', '')
        form_busqueda = BusquedaPacienteForm(initial={'busqueda': busqueda})
        
        # Filtrar pacientes con fecha de alta (dados de alta)
        pacientes = Paciente.objects.filter(fecha_alta__isnull=False)
        
        # Si se proporciona curso_id, filtrar por curso
        curso = None
        if curso_id:
            curso = get_object_or_404(Curso, id=curso_id)
            if not curso.estudiantes.filter(id=request.user.id).exists() and not curso.docente == request.user:
                raise Http404("No tienes acceso a este curso")
            pacientes = pacientes.filter(curso=curso)
        else:
            # Si el usuario es docente, filtrar solo por sus cursos
            if request.user.rol == 'docente':
                cursos_docente = Curso.objects.filter(docente=request.user)
                pacientes = pacientes.filter(curso__in=cursos_docente)
        
        # Aplicar filtro de búsqueda si existe
        if busqueda:
            pacientes = pacientes.filter(
                Q(nombre__icontains=busqueda) | 
                Q(rut__icontains=busqueda) | 
                Q(sala_cama__icontains=busqueda)
            )
        
        # Agrupar pacientes por curso
        pacientes_por_curso = []
        
        if curso_id:
            # Si tenemos un curso específico, solo mostramos esos pacientes
            pacientes_curso = pacientes.order_by('nombre')
            if pacientes_curso.exists():
                pacientes_por_curso.append((curso, pacientes_curso))
        else:
            # Si el usuario es docente, mostrar solo sus cursos
            if request.user.rol == 'docente':
                cursos_con_pacientes = Curso.objects.filter(docente=request.user, pacientes__in=pacientes).distinct()
            else:
                # Para otros roles, obtener todos los cursos con pacientes
                cursos_con_pacientes = Curso.objects.filter(pacientes__in=pacientes).distinct()
            
            # Pacientes agrupados por cada curso
            for curso in cursos_con_pacientes:
                pacientes_curso = pacientes.filter(curso=curso).order_by('nombre')
                pacientes_por_curso.append((curso, pacientes_curso))
            
            # Pacientes sin curso asignado (solo mostrar si no es docente)
            if request.user.rol != 'docente':
                pacientes_sin_curso = pacientes.filter(curso__isnull=True).order_by('nombre')
                if pacientes_sin_curso.exists():
                    pacientes_por_curso.append((None, pacientes_sin_curso))
        
        # Calcular días de hospitalización para cada paciente
        for _, pacientes_grupo in pacientes_por_curso:
            for paciente in pacientes_grupo:
                if paciente.fecha_alta:
                    paciente.dias_hospitalizacion = (paciente.fecha_alta - paciente.fecha_ingreso).days
                else:
                    paciente.dias_hospitalizacion = (timezone.now().date() - paciente.fecha_ingreso).days
        
        context = {
            'pacientes_por_curso': pacientes_por_curso,
            'form_busqueda': form_busqueda,
            'total_pacientes': pacientes.count(),
            'curso': curso
        }
        return render(request, 'pacientes/lista_pacientes_alta.html', context)

class ListaPacientesReadOnlyView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Vista de solo lectura para listar pacientes activos"""
    
    def test_func(self):
        return self.request.user.rol == 'administrador'
    
    def get(self, request, curso_id=None):            
        # Obtener parámetros de búsqueda
        busqueda = request.GET.get('busqueda', '')
        form_busqueda = BusquedaPacienteForm(initial={'busqueda': busqueda})
        
        # Filtrar pacientes activos (sin fecha de alta)
        pacientes = Paciente.objects.filter(fecha_alta__isnull=True)
        
        # Si se proporciona curso_id, filtrar por curso
        curso = None
        if curso_id:
            curso = get_object_or_404(Curso, id=curso_id)
            pacientes = pacientes.filter(curso=curso)
        
        # Aplicar filtro de búsqueda si existe
        if busqueda:
            pacientes = pacientes.filter(
                Q(nombre__icontains=busqueda) | 
                Q(rut__icontains=busqueda) | 
                Q(sala_cama__icontains=busqueda)
            )
        
        # Agrupar pacientes por curso
        pacientes_por_curso = []
        
        if curso_id:
            # Si tenemos un curso específico, solo mostramos esos pacientes
            pacientes_curso = pacientes.order_by('nombre')
            if pacientes_curso.exists():
                pacientes_por_curso.append((curso, pacientes_curso))
        else:
            # Agrupamos por todos los cursos
            # Primero, obtenemos todos los cursos que tienen pacientes asignados
            cursos_con_pacientes = Curso.objects.filter(pacientes__in=pacientes).distinct()
            
            # Pacientes agrupados por cada curso
            for curso in cursos_con_pacientes:
                pacientes_curso = pacientes.filter(curso=curso).order_by('nombre')
                pacientes_por_curso.append((curso, pacientes_curso))
            
            # Pacientes sin curso asignado
            pacientes_sin_curso = pacientes.filter(curso__isnull=True).order_by('nombre')
            if pacientes_sin_curso.exists():
                pacientes_por_curso.append((None, pacientes_sin_curso))
        
        # Calcular días de hospitalización para cada paciente
        for _, pacientes_grupo in pacientes_por_curso:
            for paciente in pacientes_grupo:
                paciente.dias_hospitalizacion = (timezone.now().date() - paciente.fecha_ingreso).days
        
        context = {
            'pacientes_por_curso': pacientes_por_curso,
            'form_busqueda': form_busqueda,
            'total_pacientes': pacientes.count(),
            'curso': curso,
            'readonly': True,
            'is_admin': self.request.user.rol == 'administrador'
        }
        return render(request, 'pacientes/lista_pacientes.html', context)

class ListaPacientesAltaReadOnlyView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Vista de solo lectura para listar pacientes dados de alta"""
    
    def test_func(self):
        return self.request.user.rol == 'administrador'
    
    def get(self, request, curso_id=None):
        # Obtener parámetros de búsqueda
        busqueda = request.GET.get('busqueda', '')
        form_busqueda = BusquedaPacienteForm(initial={'busqueda': busqueda})
        
        # Filtrar pacientes con fecha de alta (dados de alta)
        pacientes = Paciente.objects.filter(fecha_alta__isnull=False)
        
        # Si se proporciona curso_id, filtrar por curso
        curso = None
        if curso_id:
            curso = get_object_or_404(Curso, id=curso_id)
            pacientes = pacientes.filter(curso=curso)
        
        # Aplicar filtro de búsqueda si existe
        if busqueda:
            pacientes = pacientes.filter(
                Q(nombre__icontains=busqueda) | 
                Q(rut__icontains=busqueda) | 
                Q(sala_cama__icontains=busqueda)
            )
        
        # Agrupar pacientes por curso
        pacientes_por_curso = []
        
        if curso_id:
            # Si tenemos un curso específico, solo mostramos esos pacientes
            pacientes_curso = pacientes.order_by('nombre')
            if pacientes_curso.exists():
                pacientes_por_curso.append((curso, pacientes_curso))
        else:
            # Agrupamos por todos los cursos
            # Primero, obtenemos todos los cursos que tienen pacientes dados de alta
            cursos_con_pacientes = Curso.objects.filter(pacientes__in=pacientes).distinct()
            
            # Pacientes agrupados por cada curso
            for curso in cursos_con_pacientes:
                pacientes_curso = pacientes.filter(curso=curso).order_by('nombre')
                pacientes_por_curso.append((curso, pacientes_curso))
            
            # Pacientes sin curso asignado
            pacientes_sin_curso = pacientes.filter(curso__isnull=True).order_by('nombre')
            if pacientes_sin_curso.exists():
                pacientes_por_curso.append((None, pacientes_sin_curso))
        
        # Calcular días de hospitalización para cada paciente
        for _, pacientes_grupo in pacientes_por_curso:
            for paciente in pacientes_grupo:
                if paciente.fecha_alta:
                    paciente.dias_hospitalizacion = (paciente.fecha_alta - paciente.fecha_ingreso).days
                else:
                    paciente.dias_hospitalizacion = (timezone.now().date() - paciente.fecha_ingreso).days
        
        context = {
            'pacientes_por_curso': pacientes_por_curso,
            'form_busqueda': form_busqueda,
            'total_pacientes': pacientes.count(),
            'curso': curso,
            'readonly': True,
            'is_admin': self.request.user.rol == 'administrador'
        }
        return render(request, 'pacientes/lista_pacientes_alta.html', context)

class DetallePacienteReadOnlyView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Vista de solo lectura para detalles de paciente"""
    model = Paciente
    template_name = 'pacientes/detalle_paciente.html'
    context_object_name = 'paciente'

    def test_func(self):
        return self.request.user.rol == 'administrador'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['curso'] = self.object.curso
        context['readonly'] = True
        context['is_admin'] = self.request.user.rol == 'administrador'
        # Añadir fecha actual para comparaciones en la plantilla
        context['today'] = date.today()
        return context

class RegistroSignosVitalesView(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        self.paciente = get_object_or_404(Paciente, pk=kwargs['paciente_id'])
        # Los administradores pueden registrar signos vitales incluso en pacientes dados de alta
        if self.paciente.fecha_alta and request.user.rol != 'administrador':
            messages.error(request, "No se pueden registrar signos vitales en pacientes dados de alta")
            return redirect('detalle_paciente', pk=self.paciente.id)
        return super().dispatch(request, *args, **kwargs)
        
    def get(self, request, *args, **kwargs):
        form = SignosVitalesForm()
        return render(request, 'pacientes/registro_signos_vitales.html', {
            'form': form,
            'paciente': self.paciente,
            'is_admin': request.user.rol == 'administrador'
        })
        
    def post(self, request, *args, **kwargs):
        form = SignosVitalesForm(request.POST)
        if form.is_valid():
            signos_vitales = form.save(commit=False)
            signos_vitales.paciente = self.paciente
            signos_vitales.registrado_por = request.user
            signos_vitales.save()
            messages.success(request, "Signos vitales registrados exitosamente")
            return redirect('detalle_paciente', pk=self.paciente.id)
        
        return render(request, 'pacientes/registro_signos_vitales.html', {
            'form': form,
            'paciente': self.paciente,
            'is_admin': request.user.rol == 'administrador'
        })

class RegistroBalanceView(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        self.paciente = get_object_or_404(Paciente, pk=kwargs['paciente_id'])
        # Los administradores pueden registrar balances incluso en pacientes dados de alta
        if self.paciente.fecha_alta and request.user.rol != 'administrador':
            messages.error(request, "No se pueden registrar balances en pacientes dados de alta")
            return redirect('detalle_paciente', pk=self.paciente.id)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = BalanceHidricoForm()
        return render(request, 'pacientes/registro_balance.html', {
            'form': form,
            'paciente': self.paciente,
            'is_admin': request.user.rol == 'administrador'
        })
        
    def post(self, request, *args, **kwargs):
        form = BalanceHidricoForm(request.POST)
        if form.is_valid():
            balance = form.save(commit=False)
            balance.paciente = self.paciente
            balance.registrado_por = request.user
            balance.save()
            messages.success(request, "Balance registrado exitosamente")
            return redirect('detalle_paciente', pk=self.paciente.id)
        
        return render(request, 'pacientes/registro_balance.html', {
            'form': form,
            'paciente': self.paciente,
            'is_admin': request.user.rol == 'administrador'
        })

class RegistroEvolucionView(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        self.paciente = get_object_or_404(Paciente, pk=kwargs['paciente_id'])
        # Los administradores pueden registrar evoluciones incluso en pacientes dados de alta
        if self.paciente.fecha_alta and request.user.rol != 'administrador':
            messages.error(request, "No se pueden registrar evoluciones en pacientes dados de alta")
            return redirect('detalle_paciente', pk=self.paciente.id)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = EvolucionForm()
        return render(request, 'pacientes/registro_evolucion.html', {
            'form': form,
            'paciente': self.paciente,
            'is_admin': request.user.rol == 'administrador'
        })

    def post(self, request, *args, **kwargs):
        form = EvolucionForm(request.POST)
        if form.is_valid():
            evolucion = form.save(commit=False)
            evolucion.paciente = self.paciente
            evolucion.registrado_por = request.user
            evolucion.save()
            messages.success(request, "Evolución registrada exitosamente")
            return redirect('detalle_paciente', pk=self.paciente.id)
        
        return render(request, 'pacientes/registro_evolucion.html', {
            'form': form,
            'paciente': self.paciente,
            'is_admin': request.user.rol == 'administrador'
        })

class RegistroDispositivoView(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        self.paciente = get_object_or_404(Paciente, pk=kwargs['paciente_id'])
        # Los administradores pueden registrar dispositivos incluso en pacientes dados de alta
        if self.paciente.fecha_alta and request.user.rol != 'administrador':
            messages.error(request, "No se pueden registrar dispositivos en pacientes dados de alta")
            return redirect('detalle_paciente', pk=self.paciente.id)
        return super().dispatch(request, *args, **kwargs)
        
    def get(self, request, *args, **kwargs):
        form = DispositivoForm()
        return render(request, 'pacientes/registro_dispositivo.html', {
            'form': form,
            'paciente': self.paciente,
            'is_admin': request.user.rol == 'administrador'
        })
        
    def post(self, request, *args, **kwargs):
        form = DispositivoForm(request.POST)
        if form.is_valid():
            dispositivo = form.save(commit=False)
            dispositivo.paciente = self.paciente
            dispositivo.registrado_por = request.user
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
            return redirect('detalle_paciente', pk=self.paciente.id)
        
        return render(request, 'pacientes/registro_dispositivo.html', {
            'form': form,
            'paciente': self.paciente,
            'is_admin': request.user.rol == 'administrador'
        })
