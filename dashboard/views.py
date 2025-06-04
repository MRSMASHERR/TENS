from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Avg, Sum
from django.utils import timezone
from datetime import timedelta

from usuarios.models import Usuario, Curso, Notificacion
from pacientes.models import Paciente
from signos_vitales.models import SignosVitales
from balance_hidrico.models import BalanceHidrico
from evoluciones.models import Evolucion

def es_administrador(user):
    return user.is_authenticated and user.rol == 'administrador'

@login_required
def index(request):
    # Redirigir al administrador a su panel
    if request.user.rol == 'administrador':
        return redirect('admin_dashboard')
        
    # Obtener pacientes del usuario que estén asociados a algún curso
    pacientes = Paciente.objects.filter(registrado_por=request.user, fecha_alta__isnull=True, curso__isnull=False)
    total_pacientes = pacientes.count()
    pacientes_recientes = pacientes.order_by('-fecha_ingreso')[:5]
    
    # Obtener cursos según el rol del usuario
    if request.user.rol == 'docente':
        cursos = request.user.cursos_dictados.all()[:6]  # Limitar a 6 cursos más recientes
    elif request.user.rol == 'estudiante':
        cursos = request.user.cursos_inscritos.all()[:6]  # Limitar a 6 cursos más recientes
    else:
        cursos = []

    total_cursos = len(cursos)

    # Agrupar pacientes por curso
    pacientes_por_curso = []
    
    # Procesamos los pacientes que pertenecen a un curso
    for curso in cursos:
        pacientes_curso = pacientes.filter(curso=curso).order_by('-fecha_ingreso')[:5]
        if pacientes_curso.exists():
            pacientes_por_curso.append({
                'curso': curso,
                'pacientes': pacientes_curso
            })
    
    # Obtener notificaciones no leídas (como objetos, no como contador)
    notificaciones_no_leidas = Notificacion.objects.filter(
        usuario=request.user,
        leida=False
    ).order_by('-fecha_creacion')[:10]  # Limitar a las 10 más recientes

    # También incluir el contador para mostrar en la tarjeta del dashboard
    cantidad_notificaciones = notificaciones_no_leidas.count()

    context = {
        'pacientes_recientes': pacientes_recientes,
        'total_pacientes': total_pacientes,
        'cursos': cursos,
        'total_cursos': total_cursos,
        'notificaciones_no_leidas': notificaciones_no_leidas,
        'cantidad_notificaciones': cantidad_notificaciones,
        'pacientes_por_curso': pacientes_por_curso,
    }

    return render(request, 'dashboard/user_dashboard.html', context)

@login_required
@user_passes_test(es_administrador)
def admin_dashboard(request):
    # Estadísticas generales
    total_usuarios = Usuario.objects.count()
    total_estudiantes = Usuario.objects.filter(rol='estudiante').count()
    total_docentes = Usuario.objects.filter(rol='docente').count()
    total_pacientes = Paciente.objects.count()
    pacientes_activos = Paciente.objects.filter(fecha_alta__isnull=True).count()
    pacientes_dados_alta = Paciente.objects.filter(fecha_alta__isnull=False).count()
    
    # Actividad reciente (últimos 30 días)
    fecha_inicio = timezone.now().date() - timedelta(days=30)
    
    pacientes_nuevos = Paciente.objects.filter(fecha_ingreso__gte=fecha_inicio).count()
    pacientes_altas_recientes = Paciente.objects.filter(fecha_alta__gte=fecha_inicio).count()
    signos_registrados = SignosVitales.objects.filter(fecha__gte=fecha_inicio).count()
    balances_registrados = BalanceHidrico.objects.filter(fecha__gte=fecha_inicio).count()
    evoluciones_registradas = Evolucion.objects.filter(fecha__gte=fecha_inicio).count()
    
    # Limitar los valores para las barras de progreso (máximo 100%)
    barra_signos = min(signos_registrados, 100)
    barra_balances = min(balances_registrados, 100)
    barra_evoluciones = min(evoluciones_registradas, 100)
    barra_pacientes_nuevos = min(pacientes_nuevos, 100)
    barra_pacientes_altas = min(pacientes_altas_recientes, 100)
    
    # Datos para gráficos
    pacientes_por_dia = Paciente.objects.filter(
        fecha_ingreso__gte=fecha_inicio
    ).values('fecha_ingreso').annotate(
        total=Count('id')
    ).order_by('fecha_ingreso')
    
    # Top usuarios más activos
    usuarios_activos = Usuario.objects.annotate(
        num_pacientes=Count('pacientes_registrados'),
        num_evoluciones=Count('evoluciones_registradas')
    ).order_by('-num_pacientes', '-num_evoluciones')[:10]
    
    # Obtener notificaciones no leídas (como objetos, no como contador)
    notificaciones_no_leidas = Notificacion.objects.filter(
        usuario=request.user,
        leida=False
    ).order_by('-fecha_creacion')[:10]  # Limitar a las 10 más recientes
    
    # Añadir el contador para mantener consistencia con user_dashboard
    cantidad_notificaciones = notificaciones_no_leidas.count()
    
    return render(request, 'dashboard/admin_dashboard.html', {
        'total_usuarios': total_usuarios,
        'total_estudiantes': total_estudiantes,
        'total_docentes': total_docentes,
        'total_pacientes': total_pacientes,
        'pacientes_activos': pacientes_activos,
        'pacientes_dados_alta': pacientes_dados_alta,
        'pacientes_nuevos': pacientes_nuevos,
        'pacientes_altas_recientes': pacientes_altas_recientes,
        'signos_registrados': signos_registrados,
        'balances_registrados': balances_registrados,
        'evoluciones_registradas': evoluciones_registradas,
        'barra_signos': barra_signos,
        'barra_balances': barra_balances,
        'barra_evoluciones': barra_evoluciones,
        'barra_pacientes_nuevos': barra_pacientes_nuevos,
        'barra_pacientes_altas': barra_pacientes_altas,
        'pacientes_por_dia': pacientes_por_dia,
        'usuarios_activos': usuarios_activos,
        'notificaciones_no_leidas': notificaciones_no_leidas,
        'cantidad_notificaciones': cantidad_notificaciones
    })
