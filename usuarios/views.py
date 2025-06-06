from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetConfirmView, PasswordChangeView
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from datetime import timedelta, datetime
from django.utils.crypto import get_random_string
from django.utils.html import strip_tags
from django.db import transaction
import json
from django.http import Http404
from django.db.models import Count, Q
from django import forms

from .models import Usuario, Notificacion, ConfiguracionUsuario, Curso, InvitacionCurso
from pacientes.models import Paciente
from .forms import (
    LoginForm, RegistroUsuarioForm, EditarUsuarioForm, EditarPerfilForm, 
    CursoForm, InvitarEstudiantesForm, InvitarEstudianteForm
)
from signos_vitales.models import SignosVitales
from balance_hidrico.models import BalanceHidrico
from evoluciones.models import Evolucion

def es_administrador(user):
    return user.is_authenticated and user.rol == 'administrador'

def es_docente(user):
    return user.is_authenticated and user.rol == 'docente'

def es_docente_o_admin(user):
    """Verifica si el usuario es docente o administrador"""
    return user.is_authenticated and (user.rol == 'docente' or user.rol == 'administrador')

class CustomLoginView(LoginView):
    template_name = 'usuarios/login_standalone.html'
    form_class = LoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me', False)
        if not remember_me:
            # Si no marca "recordarme", la sesión expirará cuando el usuario cierre el navegador
            self.request.session.set_expiry(0)
        else:
            # Si marca "recordarme", la sesión durará 2 semanas
            self.request.session.set_expiry(1209600)
        
        # Mensaje de bienvenida
        messages.success(self.request, f'¡Bienvenido/a {form.get_user().get_full_name()}!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        # Agregar mensajes de error más descriptivos
        for field, errors in form.errors.items():
            for error in errors:
                if field == '__all__':
                    messages.error(self.request, f'Error: {error}')
                else:
                    messages.error(self.request, f'Error en {field}: {error}')
        
        # Imprimir información de depuración
        print("Form errors:", form.errors)
        print("Request method:", self.request.method)
        print("CSRF token:", self.request.POST.get('csrfmiddlewaretoken'))
                    
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('dashboard')

class RegistroUsuarioView(UserPassesTestMixin, CreateView):
    model = Usuario
    form_class = RegistroUsuarioForm
    template_name = 'usuarios/registro.html'
    success_url = reverse_lazy('lista_usuarios')
    
    def test_func(self):
        return es_administrador(self.request.user)
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Validamos si viene un rol en el POST para mostrar campos específicos
        if self.request.method == 'POST':
            rol = self.request.POST.get('rol')
            print(f"Rol seleccionado en POST: {rol}")
            if rol == 'docente':
                # Si es docente, añadir campos específicos
                form.fields['especialidad'] = forms.CharField(
                    widget=forms.TextInput(attrs={'class': 'form-control'}),
                    required=True,
                    label='Especialidad'
                )
                form.fields['titulo_profesional'] = forms.CharField(
                    widget=forms.TextInput(attrs={'class': 'form-control'}),
                    required=True,
                    label='Título Profesional'
                )
                form.fields['anos_experiencia'] = forms.IntegerField(
                    widget=forms.NumberInput(attrs={'class': 'form-control'}),
                    required=True,
                    min_value=0,
                    initial=0,
                    label='Años de Experiencia'
                )
            elif rol == 'estudiante':
                # Si es estudiante, añadir campos específicos
                form.fields['matricula'] = forms.CharField(
                    widget=forms.TextInput(attrs={'class': 'form-control'}),
                    required=True,
                    label='Matrícula'
                )
                form.fields['ano_ingreso'] = forms.IntegerField(
                    widget=forms.NumberInput(attrs={'class': 'form-control'}),
                    required=True,
                    label='Año de Ingreso'
                )
                form.fields['semestre_actual'] = forms.IntegerField(
                    widget=forms.NumberInput(attrs={'class': 'form-control'}),
                    required=True,
                    label='Semestre Actual'
                )
        return form
    
    def form_valid(self, form):
        try:
            from django.db import connection
            print("Configuración de la base de datos:", connection.settings_dict)
            print("Datos del formulario:", form.cleaned_data)
            
            usuario = form.save(commit=False)
            # Asegurarse de que los campos específicos se guarden correctamente
            rol = form.cleaned_data.get('rol')
            print(f"Rol del usuario a crear: {rol}")
            
            if rol == 'administrador':
                # Si es administrador, asignar permisos completos
                usuario.is_superuser = True
                usuario.is_staff = True
            elif rol == 'docente':
                # Guarda campos de docente
                usuario.especialidad = form.cleaned_data.get('especialidad', '')
                usuario.titulo_profesional = form.cleaned_data.get('titulo_profesional', '')
                usuario.anos_experiencia = form.cleaned_data.get('anos_experiencia', 0)
                # Limpiar campos de estudiante
                usuario.matricula = None
                usuario.ano_ingreso = None
                usuario.semestre_actual = None
            elif rol == 'estudiante':
                # Guarda campos de estudiante
                usuario.matricula = form.cleaned_data.get('matricula', '')
                usuario.ano_ingreso = form.cleaned_data.get('ano_ingreso')
                usuario.semestre_actual = form.cleaned_data.get('semestre_actual')
                # Limpiar campos de docente
                usuario.especialidad = None
                usuario.titulo_profesional = None
                usuario.anos_experiencia = None
            
            print("Intentando guardar usuario...")
            usuario.save()
            print("Usuario guardado exitosamente")
            
            messages.success(self.request, 'Usuario creado exitosamente')
            return super().form_valid(form)
        except Exception as e:
            print("Error al crear usuario:", str(e))
            print("Tipo de error:", type(e).__name__)
            import traceback
            print("Traceback completo:", traceback.format_exc())
            messages.error(self.request, f'Error al crear usuario: {str(e)}')
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        print("Formulario inválido")
        print("Errores del formulario:", form.errors)
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field}: {error}")
        return super().form_invalid(form)

class ListaUsuariosView(UserPassesTestMixin, ListView):
    model = Usuario
    template_name = 'usuarios/lista_usuarios.html'
    context_object_name = 'usuarios'
    
    def test_func(self):
        return es_administrador(self.request.user)

class EditarUsuarioView(UserPassesTestMixin, UpdateView):
    model = Usuario
    form_class = EditarUsuarioForm
    template_name = 'usuarios/editar_usuario.html'
    success_url = reverse_lazy('lista_usuarios')
    
    def test_func(self):
        return es_administrador(self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, 'Usuario actualizado exitosamente')
        return super().form_valid(form)

@login_required
@user_passes_test(es_administrador)
def desactivar_usuario(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    usuario.activo = False
    usuario.save()
    messages.success(request, f'Usuario {usuario.username} desactivado exitosamente')
    return redirect('lista_usuarios')

@login_required
@user_passes_test(es_administrador)
def activar_usuario(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    usuario.activo = True
    usuario.save()
    messages.success(request, f'Usuario {usuario.username} activado exitosamente')
    return redirect('lista_usuarios')

@login_required
@user_passes_test(es_administrador)
def admin_dashboard(request):
    # Período de tiempo para estadísticas (30 días)
    periodo = timezone.now() - timezone.timedelta(days=30)
    
    # Datos generales
    total_usuarios = Usuario.objects.count()
    total_estudiantes = Usuario.objects.filter(rol='estudiante').count()
    total_docentes = Usuario.objects.filter(rol='docente').count()
    
    try:
        from pacientes.models import Paciente, SignosVitales, BalanceHidrico, Evolucion
        
        # Datos de pacientes
        total_pacientes = Paciente.objects.count()
        pacientes_nuevos = Paciente.objects.filter(fecha_registro__gte=periodo).count()
        
        # Estadísticas de actividad
        signos_registrados = SignosVitales.objects.filter(fecha_registro__gte=periodo).count()
        balances_registrados = BalanceHidrico.objects.filter(fecha_registro__gte=periodo).count()
        evoluciones_registradas = Evolucion.objects.filter(fecha_registro__gte=periodo).count()
        
        # Usuarios más activos (combinando datos de pacientes y evoluciones)
        usuarios_activos = Usuario.objects.annotate(
            num_pacientes=Count('pacientes_registrados', filter=Q(pacientes_registrados__fecha_registro__gte=periodo)),
            num_evoluciones=Count('evoluciones', filter=Q(evoluciones__fecha_registro__gte=periodo))
        ).filter(Q(num_pacientes__gt=0) | Q(num_evoluciones__gt=0)).order_by('-num_pacientes', '-num_evoluciones')[:10]
        
    except ImportError:
        # En caso de que no existan los modelos de pacientes
        total_pacientes = 0
        pacientes_nuevos = 0
        signos_registrados = 0
        balances_registrados = 0
        evoluciones_registradas = 0
        usuarios_activos = []
    
    context = {
        'total_usuarios': total_usuarios,
        'total_estudiantes': total_estudiantes,
        'total_docentes': total_docentes,
        'total_pacientes': total_pacientes,
        'pacientes_nuevos': pacientes_nuevos,
        'signos_registrados': signos_registrados,
        'balances_registrados': balances_registrados,
        'evoluciones_registradas': evoluciones_registradas,
        'usuarios_activos': usuarios_activos,
    }
    
    return render(request, 'dashboard/admin_dashboard.html', context)

@login_required
def perfil_usuario(request):
    # Obtener notificaciones no leídas
    notificaciones_no_leidas = request.user.notificaciones.filter(leida=False)
    
    context = {
        'notificaciones_no_leidas': notificaciones_no_leidas,
    }
    return render(request, 'usuarios/perfil.html', context)

@login_required
def editar_perfil(request):
    if request.method == 'POST':
        form = EditarPerfilForm(request.POST, instance=request.user)
        if form.is_valid():
            usuario = form.save(commit=False)
            
            # Asegurarse de que los campos específicos del rol se guarden correctamente
            if usuario.rol == 'docente':
                usuario.especialidad = form.cleaned_data.get('especialidad') or ''
                usuario.titulo_profesional = form.cleaned_data.get('titulo_profesional') or ''
                usuario.anos_experiencia = form.cleaned_data.get('anos_experiencia') or 0
                # Limpiar campos de estudiante
                usuario.matricula = None
                usuario.ano_ingreso = None
                usuario.semestre_actual = None
            elif usuario.rol == 'estudiante':
                usuario.matricula = form.cleaned_data.get('matricula') or ''
                usuario.ano_ingreso = form.cleaned_data.get('ano_ingreso')
                usuario.semestre_actual = form.cleaned_data.get('semestre_actual')
                # Limpiar campos de docente
                usuario.especialidad = None
                usuario.titulo_profesional = None
                usuario.anos_experiencia = None
            
            usuario.save()
            messages.success(request, 'Perfil actualizado exitosamente')
            return redirect('perfil_usuario')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario')
            print("Form errors:", form.errors)  # Debug
    else:
        # Asegurarse de que los campos no sean None al inicializar el formulario
        initial_data = {
            'first_name': request.user.first_name or '',
            'last_name': request.user.last_name or '',
            'email': request.user.email or '',
            'rut': request.user.rut or '',
        }
        
        if request.user.rol == 'docente':
            initial_data.update({
                'especialidad': request.user.especialidad or '',
                'titulo_profesional': request.user.titulo_profesional or '',
                'anos_experiencia': request.user.anos_experiencia or 0,
            })
        elif request.user.rol == 'estudiante':
            initial_data.update({
                'matricula': request.user.matricula or '',
                'ano_ingreso': request.user.ano_ingreso,
                'semestre_actual': request.user.semestre_actual,
            })
        
        form = EditarPerfilForm(instance=request.user, initial=initial_data)
    
    return render(request, 'usuarios/editar_perfil.html', {
        'form': form,
        'user': request.user
    })

@login_required
def mis_notificaciones(request):
    notificaciones = request.user.notificaciones.all()
    notificaciones_no_leidas = notificaciones.filter(leida=False)
    
    # Marcar todas como leídas si se solicita mediante POST
    if request.method == 'POST' and request.POST.get('marcar_todas'):
        notificaciones_no_leidas.update(leida=True)
        messages.success(request, 'Todas las notificaciones han sido marcadas como leídas')
        return redirect('mis_notificaciones')
    
    # Este código legacy para API se mantiene por compatibilidad
    if request.GET.get('marcar_leidas'):
        notificaciones_no_leidas.update(leida=True)
        return JsonResponse({'status': 'success'})
    
    return render(request, 'usuarios/notificaciones.html', {
        'notificaciones': notificaciones,
        'no_leidas': notificaciones_no_leidas.count()
    })

@login_required
def marcar_notificacion_leida(request, notificacion_id):
    notificacion = get_object_or_404(Notificacion, id=notificacion_id, usuario=request.user)
    notificacion.leida = True
    notificacion.save()
    messages.success(request, 'Notificación marcada como leída')
    return redirect('mis_notificaciones')

@login_required
def eliminar_notificacion(request, notificacion_id):
    notificacion = get_object_or_404(Notificacion, id=notificacion_id, usuario=request.user)
    notificacion.delete()
    messages.success(request, 'Notificación eliminada')
    return redirect('mis_notificaciones')

@login_required
def configuracion(request):
    config, created = ConfiguracionUsuario.objects.get_or_create(usuario=request.user)
    
    if request.method == 'POST':
        config.recibir_notificaciones_email = request.POST.get('recibir_notificaciones_email') == 'on'
        config.tema_oscuro = request.POST.get('tema_oscuro') == 'on'
        config.mostrar_acciones_rapidas = request.POST.get('mostrar_acciones_rapidas') == 'on'
        config.save()
        messages.success(request, 'Configuración actualizada exitosamente')
        return redirect('configuracion')
    
    return render(request, 'usuarios/configuracion.html', {'config': config})

@login_required
def acciones_rapidas(request):
    # Obtener las últimas acciones del usuario
    ultimos_pacientes = request.user.pacientes_registrados.all()[:5]
    ultimos_signos = SignosVitales.objects.filter(registrado_por=request.user)[:5]
    ultimos_balances = BalanceHidrico.objects.filter(registrado_por=request.user)[:5]
    ultimas_evoluciones = Evolucion.objects.filter(responsable=request.user)[:5]
    
    return render(request, 'usuarios/acciones_rapidas.html', {
        'ultimos_pacientes': ultimos_pacientes,
        'ultimos_signos': ultimos_signos,
        'ultimos_balances': ultimos_balances,
        'ultimas_evoluciones': ultimas_evoluciones
    })

class CustomPasswordResetView(PasswordResetView):
    template_name = 'usuarios/password_reset_standalone.html'
    email_template_name = 'emails/recuperar_contrasena.html'
    subject_template_name = 'usuarios/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')
    
    def form_valid(self, form):
        """Sobrescribimos el método para establecer el nombre del sitio en el contexto del email
        y capturar errores de envío de correo."""
        email = form.cleaned_data['email']
        context = self.get_context_data()
        context.update({
            'email': email,
            'site_name': settings.SITE_NAME,
        })
        
        # Buscar si el usuario existe
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.filter(email=email).first()
        
        if not user:
            messages.error(self.request, "El correo ingresado no está registrado en el sistema.")
            return self.form_invalid(form)
        
        try:
            # En modo DEBUG, mostrar información detallada
            print(f"\n[DEBUG] Intentando enviar correo a: {email}")
            print(f"[DEBUG] Usuario encontrado: {user.username}")
            print(f"[DEBUG] Configuración SMTP:")
            print(f"  - EMAIL_HOST: {settings.EMAIL_HOST}")
            print(f"  - EMAIL_PORT: {settings.EMAIL_PORT}")
            print(f"  - EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
            print(f"  - EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
            print(f"  - DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
            
            # Generar token y enlace para usarlo en caso de fallo
            from django.contrib.auth.tokens import default_token_generator
            from django.utils.http import urlsafe_base64_encode
            from django.utils.encoding import force_bytes
            
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_url = self.request.build_absolute_uri(
                reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
            )
            
            # Intentar enviar el correo
            form.save(
                request=self.request,
                from_email=settings.DEFAULT_FROM_EMAIL,
                email_template_name=self.email_template_name,
                subject_template_name=self.subject_template_name,
                html_email_template_name=self.email_template_name,
                extra_email_context={'site_name': settings.SITE_NAME}
            )
            
            print(f"[DEBUG] Correo enviado exitosamente a: {email}")
            print(f"[DEBUG] Enlace de reinicio: {reset_url}")
            
            messages.success(self.request, f"Se han enviado instrucciones a {email}")
            return super().form_valid(form)
            
        except Exception as e:
            # Capturar cualquier error en el envío y mostrar en consola
            print(f"\n[ERROR] Error al enviar correo: {str(e)}")
            print(f"[DEBUG] Enlace de reinicio (fallo en envío): {reset_url}")
            
            # En caso de error, mostrar un mensaje al usuario
            messages.warning(
                self.request,
                f"Hubo un problema técnico al enviar el correo. Por favor usa el siguiente enlace temporal o intenta más tarde."
            )
            
            # Añadir el enlace a la sesión para acceder desde la página de confirmación
            self.request.session['reset_url'] = reset_url
            
            # Redirigir a una página especial que muestre el enlace temporal
            return redirect('password_reset_done')

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'usuarios/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'usuarios/password_change.html'
    success_url = reverse_lazy('password_change_done')

def password_reset_done(request):
    """Vista para mostrar la página de confirmación de envío de email de recuperación"""
    # La URL del enlace de reinicio se almacena en la sesión si hubo un error en el envío
    reset_url = request.session.get('reset_url', None)
    # Lo dejamos disponible para la plantilla
    context = {'reset_url': reset_url}
    
    # Si el usuario navega fuera y vuelve, limpiamos la sesión
    if 'reset_url' in request.session and not request.session.get('reset_url_shown', False):
        request.session['reset_url_shown'] = True
    elif 'reset_url' in request.session:
        # En la segunda visita, eliminamos la URL de la sesión por seguridad
        del request.session['reset_url']
        del request.session['reset_url_shown']
    
    return render(request, 'usuarios/password_reset_done_standalone.html', context)

def password_reset_complete(request):
    return render(request, 'usuarios/password_reset_complete.html')

def password_change_done(request):
    return render(request, 'usuarios/password_change_done.html')

@login_required
def mis_pacientes(request):
    pacientes = Paciente.objects.filter(registrado_por=request.user, activo=True).order_by('-fecha_ingreso')
    
    # Estadísticas básicas
    total_pacientes = pacientes.count()
    pacientes_hoy = pacientes.filter(fecha_ingreso=timezone.now().date()).count()
    
    context = {
        'pacientes': pacientes,
        'total_pacientes': total_pacientes,
        'pacientes_hoy': pacientes_hoy,
    }
    
    return render(request, 'usuarios/mis_pacientes.html', context)

@login_required
def lista_cursos(request):
    if request.user.rol == 'administrador':
        cursos = Curso.objects.all()
    elif request.user.rol == 'docente':
        cursos = Curso.objects.filter(docente=request.user)
    else:
        messages.error(request, 'No tienes permisos para acceder a esta vista')
        return redirect('dashboard')
    
    return render(request, 'usuarios/cursos/lista_cursos.html', {
        'cursos': cursos
    })

@login_required
@user_passes_test(es_docente_o_admin)
def crear_curso(request):
    if request.method == 'POST':
        form = CursoForm(request.POST)
        if form.is_valid():
            curso = form.save(commit=False)
            # Si es administrador, puede asignar otro docente (opcional)
            if request.user.rol == 'administrador' and 'docente_id' in request.POST:
                try:
                    docente_id = int(request.POST.get('docente_id'))
                    docente = Usuario.objects.get(id=docente_id, rol='docente')
                    curso.docente = docente
                except (ValueError, Usuario.DoesNotExist):
                    # Si no se proporciona un docente válido, el admin es el docente
                    curso.docente = request.user
            else:
                # Si es docente, siempre se asigna a sí mismo
                curso.docente = request.user
            
            curso.save()
            messages.success(request, 'Curso creado exitosamente')
            return redirect('detalle_curso', curso_id=curso.pk)
    else:
        form = CursoForm()
    
    # Añadir lista de docentes disponibles para administradores
    docentes = []
    if request.user.rol == 'administrador':
        docentes = Usuario.objects.filter(rol='docente', activo=True)
    
    return render(request, 'usuarios/cursos/crear_curso.html', {
        'form': form,
        'docentes': docentes,
        'is_admin': request.user.rol == 'administrador'
    })

@login_required
def detalle_curso(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    
    # Verificar que el usuario tenga acceso al curso
    # Los administradores tienen acceso a todos los cursos
    if request.user.rol != 'administrador' and not curso.estudiantes.filter(id=request.user.id).exists() and not curso.docente == request.user:
        raise Http404("No tienes acceso a este curso")
    
    # Procesar el formulario de invitación si el usuario es el docente o administrador
    if request.method == 'POST' and (request.user == curso.docente or request.user.rol == 'administrador'):
        # Verificar si es una acción de reenviar o cancelar invitación
        action = request.POST.get('action')
        invitacion_id = request.POST.get('invitacion_id')
        
        if action and invitacion_id:
            try:
                invitacion = InvitacionCurso.objects.get(id=invitacion_id, curso=curso)
                
                if action == 'reenviar':
                    # Verificar que no sea un docente
                    usuario = Usuario.objects.filter(email=invitacion.email).first()
                    if usuario and usuario.rol == 'docente':
                        messages.error(request, "No se pueden invitar docentes al curso")
                        return redirect('detalle_curso', curso_id=curso.id)
                        
                    # Actualizar fecha de expiración y reenviar
                    invitacion.fecha_expiracion = timezone.now() + timezone.timedelta(days=7)
                    invitacion.save()
                    enviar_email_invitacion(request, invitacion)
                    messages.success(request, f"Se ha reenviado la invitación a {invitacion.email}")
                    
                elif action == 'cancelar':
                    # Eliminar la invitación
                    email = invitacion.email
                    invitacion.delete()
                    messages.success(request, f"Se ha cancelado la invitación a {email}")
                
                return redirect('detalle_curso', curso_id=curso.id)
            except InvitacionCurso.DoesNotExist:
                messages.error(request, "La invitación no existe")
        
        # Si no es una acción, procesamos el formulario normal
        form = InvitarEstudianteForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            
            # Verificar si el usuario ya existe
            usuario_existente = Usuario.objects.filter(email=email).first()
            
            if usuario_existente:
                # Verificar que no sea un docente
                if usuario_existente.rol == 'docente':
                    messages.error(request, "No se pueden invitar docentes al curso")
                    return redirect('detalle_curso', curso_id=curso.id)
                    
                # Verificar si ya está en el curso
                if curso.estudiantes.filter(pk=usuario_existente.pk).exists():
                    messages.info(request, f"El usuario {email} ya está en el curso")
                else:
                    # Añadir al curso si ya tiene cuenta
                    curso.estudiantes.add(usuario_existente)
                    # Enviar notificación interna
                    enviar_notificacion_curso(usuario_existente, curso)
                    messages.success(request, f"Se ha añadido a {email} al curso")
            else:
                # Verificar si ya hay una invitación pendiente
                invitacion_existente = InvitacionCurso.objects.filter(
                    curso=curso, email=email, aceptada=False
                ).first()
                
                if invitacion_existente and not invitacion_existente.esta_expirada():
                    messages.info(request, f"Ya existe una invitación pendiente para {email}")
                else:
                    # Si existe pero está expirada, la eliminamos
                    if invitacion_existente:
                        invitacion_existente.delete()
                    
                    # Crear nueva invitación
                    invitacion = InvitacionCurso.objects.create(
                        curso=curso,
                        email=email,
                        enviada_por=request.user
                    )
                    
                    # Enviar correo electrónico con la invitación
                    enviar_email_invitacion(request, invitacion)
                    messages.success(request, f"Se ha enviado una invitación a {email}")
            
            # Redirigir para evitar reenvío del formulario
            return redirect('detalle_curso', curso_id=curso.id)
    else:
        form = InvitarEstudianteForm()
    
    # Obtener los pacientes del usuario en este curso
    mis_pacientes = Paciente.objects.filter(
        curso=curso,
        registrado_por=request.user
    )
    
    # Obtener los pacientes recientes del usuario (últimos 5)
    mis_pacientes_recientes = mis_pacientes.order_by('-fecha_ingreso')[:5]
    
    # Obtener el total de pacientes del curso
    total_pacientes_curso = Paciente.objects.filter(curso=curso).count()
    
    # Obtener actividad reciente del curso (últimas 10 actividades)
    actividad_reciente = []
    
    # Obtener últimos pacientes registrados
    pacientes_recientes = Paciente.objects.filter(curso=curso).order_by('-fecha_ingreso')[:5]
    for paciente in pacientes_recientes:
        actividad_reciente.append({
            'titulo': f'Nuevo paciente registrado',
            'descripcion': f'{paciente.registrado_por.get_full_name()} registró a {paciente.nombre}',
            'fecha': paciente.fecha_ingreso
        })
    
    # Obtener últimas evoluciones
    evoluciones_recientes = Evolucion.objects.filter(
        paciente__curso=curso
    ).order_by('-fecha', '-hora')[:5]
    
    for evolucion in evoluciones_recientes:
        actividad_reciente.append({
            'titulo': f'Nueva evolución registrada',
            'descripcion': f'{evolucion.responsable.get_full_name()} registró una evolución para {evolucion.paciente.nombre}',
            'fecha': evolucion.fecha
        })
    
    # Ordenar actividad reciente por fecha
    actividad_reciente = sorted(
        actividad_reciente,
        key=lambda x: x['fecha'],
        reverse=True
    )[:10]
    
    # Obtener invitaciones pendientes si el usuario es el docente o administrador
    invitaciones_pendientes = []
    if request.user == curso.docente or request.user.rol == 'administrador':
        invitaciones_pendientes = InvitacionCurso.objects.filter(
            curso=curso, 
            aceptada=False
        ).exclude(
            fecha_expiracion__lt=timezone.now()
        ).order_by('-fecha_envio')
    
    # Obtener contadores para estadísticas
    signos_vitales_count = SignosVitales.objects.filter(
        paciente__curso=curso
    ).count()
    
    evoluciones_count = Evolucion.objects.filter(
        paciente__curso=curso
    ).count()
    
    context = {
        'curso': curso,
        'form': form,
        'mis_pacientes_count': mis_pacientes.count(),
        'mis_pacientes_recientes': mis_pacientes_recientes,
        'total_pacientes_curso': total_pacientes_curso,
        'actividad_reciente': actividad_reciente,
        'invitaciones_pendientes': invitaciones_pendientes,
        'is_admin': request.user.rol == 'administrador',
        'signos_vitales_count': signos_vitales_count,
        'evoluciones_count': evoluciones_count
    }
    
    return render(request, 'usuarios/cursos/detalle_curso.html', context)

@login_required
def aceptar_invitacion(request, token):
    """Vista para aceptar una invitación y registrarse si es necesario"""
    try:
        invitacion = InvitacionCurso.objects.get(token=token, aceptada=False)
    except InvitacionCurso.DoesNotExist:
        messages.error(request, "La invitación no existe o ya ha sido utilizada")
        return redirect('login')
    
    # Verificar si la invitación ha expirado
    if invitacion.esta_expirada():
        messages.error(request, "La invitación ha expirado")
        return redirect('login')
    
    # Verificar si el usuario ya está autenticado
    if request.user.is_authenticated:
        # Si el email del usuario no coincide con el de la invitación
        if request.user.email != invitacion.email:
            logout(request)
            messages.info(request, f"Debe iniciar sesión con la cuenta asociada a {invitacion.email} o registrarse con ese correo")
            return redirect('registro', token=token)
        
        # Añadir al curso si el email coincide
        invitacion.curso.estudiantes.add(request.user)
        invitacion.aceptada = True
        invitacion.save()
        
        messages.success(request, f"Has sido añadido al curso {invitacion.curso.nombre}")
        return redirect('detalle_curso', curso_id=invitacion.curso.id)
    
    # Si no está autenticado, verificar si existe un usuario con ese email
    usuario_existente = Usuario.objects.filter(email=invitacion.email).first()
    
    if usuario_existente:
        # Si ya existe una cuenta, redirigir al login
        messages.info(request, f"Ya existe una cuenta con el correo {invitacion.email}. Inicie sesión para aceptar la invitación.")
        return redirect('login')
    else:
        # Si no existe, redirigir al registro
        return redirect('registro', token=token)

@login_required
def mis_cursos(request):
    if request.user.rol == 'docente':
        cursos = request.user.cursos_dictados.all()
    else:
        cursos = request.user.cursos_inscritos.all()
    
    return render(request, 'usuarios/cursos/lista_cursos.html', {
        'cursos': cursos
    })

@login_required
def actualizar_configuracion(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            setting = data.get('setting')
            value = data.get('value')
            
            config = ConfiguracionUsuario.objects.get_or_create(usuario=request.user)[0]
            
            if hasattr(config, setting):
                setattr(config, setting, value)
                config.save()
                
                # Si es el tema oscuro, actualizar la sesión
                if setting == 'tema_oscuro':
                    request.session['tema_oscuro'] = value
                
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'Configuración no válida'})
                
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Datos inválidos'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

@login_required
def invitar_estudiantes(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    
    # Verificar que el usuario sea el docente del curso
    if request.user != curso.docente:
        messages.error(request, "Solo el docente del curso puede enviar invitaciones")
        return redirect('detalle_curso', curso_id=curso.id)
    
    if request.method == 'POST':
        form = InvitarEstudiantesForm(request.POST)
        if form.is_valid():
            emails = form.cleaned_data['emails']
            invitados_count = 0
            ya_en_curso_count = 0
            ya_invitados_count = 0
            docentes_count = 0
            
            with transaction.atomic():
                for email in emails:
                    # Verificar si el usuario ya existe
                    usuario_existente = Usuario.objects.filter(email=email).first()
                    
                    if usuario_existente:
                        # Verificar que no sea un docente
                        if usuario_existente.rol == 'docente':
                            docentes_count += 1
                            continue
                            
                        # Verificar si ya está en el curso
                        if curso.estudiantes.filter(pk=usuario_existente.pk).exists():
                            ya_en_curso_count += 1
                            continue
                        
                        # Añadir al curso si ya tiene cuenta
                        curso.estudiantes.add(usuario_existente)
                        
                        # Enviar notificación interna
                        enviar_notificacion_curso(usuario_existente, curso)
                        
                        invitados_count += 1
                    else:
                        # Verificar si ya hay una invitación pendiente para este email
                        invitacion_existente = InvitacionCurso.objects.filter(
                            curso=curso, email=email, aceptada=False
                        ).first()
                        
                        if invitacion_existente:
                            if not invitacion_existente.esta_expirada():
                                ya_invitados_count += 1
                                continue
                            else:
                                # Si está expirada, la eliminamos para crear una nueva
                                invitacion_existente.delete()
                        
                        # Crear nueva invitación
                        invitacion = InvitacionCurso.objects.create(
                            curso=curso,
                            email=email,
                            enviada_por=request.user
                        )
                        
                        # Enviar correo electrónico con la invitación
                        enviar_email_invitacion(request, invitacion)
                        
                        invitados_count += 1
            
            # Mostrar mensajes según los resultados
            if invitados_count > 0:
                messages.success(request, f"Se han enviado {invitados_count} invitaciones correctamente")
            
            if ya_en_curso_count > 0:
                messages.info(request, f"{ya_en_curso_count} usuarios ya están en el curso")
                
            if ya_invitados_count > 0:
                messages.info(request, f"{ya_invitados_count} usuarios ya tenían invitaciones pendientes")
                
            if docentes_count > 0:
                messages.error(request, f"No se pudieron invitar {docentes_count} docentes al curso")
                
            return redirect('detalle_curso', curso_id=curso.id)
    else:
        form = InvitarEstudiantesForm()
    
    return render(request, 'usuarios/invitar_estudiantes.html', {
        'form': form,
        'curso': curso
    })

def enviar_notificacion_curso(usuario, curso):
    """Envía una notificación interna al usuario de que ha sido añadido a un curso"""
    from .models import Notificacion  # Import aquí para evitar importación circular
    
    Notificacion.objects.create(
        usuario=usuario,
        titulo=f"Has sido añadido al curso: {curso.nombre}",
        mensaje=f"El docente {curso.docente.get_full_name()} te ha añadido al curso {curso.nombre}. Puedes acceder desde la sección de cursos.",
        tipo="INFO",
        url=reverse('detalle_curso', args=[curso.id])
    )

def enviar_email_invitacion(request, invitacion):
    """Envía un correo electrónico con la invitación al curso"""
    context = {
        'invitacion': invitacion,
        'curso': invitacion.curso,
        'docente': invitacion.curso.docente,
        'base_url': request.build_absolute_uri('/')[:-1],  # URL base sin la barra final
        'registro_url': request.build_absolute_uri(
            reverse('aceptar_invitacion', args=[str(invitacion.token)])
        ),
    }
    
    # Preparar el correo
    html_message = render_to_string('emails/invitacion_curso.html', context)
    plain_message = strip_tags(html_message)
    
    # Enviar correo
    send_mail(
        subject=f'Invitación al curso: {invitacion.curso.nombre}',
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[invitacion.email],
        html_message=html_message,
        fail_silently=False,
    )

def registro_con_invitacion(request, token):
    """Vista para registrarse a partir de una invitación"""
    try:
        invitacion = InvitacionCurso.objects.get(token=token, aceptada=False)
    except InvitacionCurso.DoesNotExist:
        messages.error(request, "La invitación no existe o ya ha sido utilizada")
        return redirect('login')
    
    if invitacion.esta_expirada():
        messages.error(request, "La invitación ha expirado")
        return redirect('login')
    
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.email = invitacion.email  # Asegurar que el email sea el de la invitación
            usuario.save()
            
            # Añadir al curso
            invitacion.curso.estudiantes.add(usuario)
            invitacion.aceptada = True
            invitacion.save()
            
            # Iniciar sesión automáticamente
            login(request, usuario)
            
            messages.success(request, f"Cuenta creada y añadido al curso {invitacion.curso.nombre}")
            return redirect('detalle_curso', curso_id=invitacion.curso.id)
    else:
        # Inicializar con el email de la invitación
        form = RegistroUsuarioForm(initial={'email': invitacion.email})
    
    return render(request, 'usuarios/registro.html', {
        'form': form,
        'invitacion': invitacion
    })

@login_required
@user_passes_test(es_administrador)
def verificar_estado_admin(request):
    """
    Vista para verificar el estado actual de los permisos de los administradores.
    Muestra un resumen de los administradores y sus permisos actuales.
    """
    # Obtener todos los usuarios con rol administrador
    administradores = Usuario.objects.filter(rol='administrador')
    
    # Información sobre cada administrador
    admin_info = []
    
    for admin in administradores:
        admin_info.append({
            'username': admin.username,
            'nombre_completo': admin.get_full_name(),
            'is_superuser': admin.is_superuser,
            'is_staff': admin.is_staff,
            'is_active': admin.is_active,
            'activo': admin.activo,
            'necesita_actualizar': not (admin.is_superuser and admin.is_staff and admin.is_active and admin.activo)
        })
    
    # Información para el template
    context = {
        'administradores': admin_info,
        'total_admins': len(admin_info),
        'admins_ok': sum(1 for admin in admin_info if not admin['necesita_actualizar']),
        'admins_pendientes': sum(1 for admin in admin_info if admin['necesita_actualizar']),
    }
    
    return render(request, 'usuarios/verificar_estado_admin.html', context)

@login_required
@user_passes_test(es_administrador)
def configurar_permisos_admin(request):
    """
    Vista para configurar todos los permisos necesarios para los administradores.
    Establece a todos los usuarios con rol 'administrador' como superusuarios,
    staff y les da permisos completos.
    """
    # Obtener todos los usuarios con rol administrador
    administradores = Usuario.objects.filter(rol='administrador')
    
    # Contador para mostrar mensaje
    actualizados = 0
    
    # Actualizar cada administrador
    for admin in administradores:
        actualizado = False
        
        # Verificar y actualizar permisos de superusuario y staff
        if not admin.is_superuser:
            admin.is_superuser = True
            actualizado = True
            
        if not admin.is_staff:
            admin.is_staff = True
            actualizado = True
            
        # Asegurar que estén activados
        if not admin.activo:
            admin.activo = True
            actualizado = True
            
        # Asegurar que estén activos en el sistema de autenticación de Django
        if not admin.is_active:
            admin.is_active = True
            actualizado = True
            
        # Guardar los cambios si hubo alguna modificación
        if actualizado:
            admin.save()
            actualizados += 1
    
    if actualizados > 0:
        messages.success(request, f'Se han actualizado {actualizados} administradores con permisos completos.')
    else:
        messages.info(request, 'Todos los administradores ya tienen permisos completos.')
    
    return redirect('admin_dashboard')

@login_required
def editar_curso(request, curso_id):
    """Vista para editar un curso, con diferentes permisos según el rol del usuario"""
    curso = get_object_or_404(Curso, id=curso_id)
    
    # Verificar permisos para editar (docente del curso o administrador)
    if not (request.user == curso.docente or request.user.rol == 'administrador'):
        messages.error(request, "No tienes permisos para editar este curso")
        return redirect('detalle_curso', curso_id=curso.id)
    
    if request.method == 'POST':
        # Si es docente, solo puede editar nombre y descripción
        if request.user == curso.docente and request.user.rol != 'administrador':
            # Crear una copia de los datos POST y limitarlos a los campos permitidos
            data = request.POST.copy()
            # Mantener los valores originales para campos que no puede editar
            data['codigo'] = curso.codigo
            
            form = CursoForm(data, instance=curso)
            # Validar manualmente solo los campos permitidos
            if form.is_valid():
                # Solo actualizar nombre y descripción
                curso.nombre = form.cleaned_data['nombre']
                curso.descripcion = form.cleaned_data['descripcion']
                curso.save()
                messages.success(request, "Curso actualizado exitosamente")
                return redirect('detalle_curso', curso_id=curso.id)
        else:
            # Si es administrador, puede editar todos los campos
            form = CursoForm(request.POST, instance=curso)
            if form.is_valid():
                form.save()
                messages.success(request, "Curso actualizado exitosamente")
                return redirect('detalle_curso', curso_id=curso.id)
    else:
        form = CursoForm(instance=curso)
    
    # Si es docente, marcar como solo lectura los campos que no puede editar
    readonly_fields = []
    if request.user == curso.docente and request.user.rol != 'administrador':
        readonly_fields = ['codigo']
    
    context = {
        'form': form,
        'curso': curso,
        'readonly_fields': readonly_fields,
        'is_admin': request.user.rol == 'administrador'
    }
    
    return render(request, 'usuarios/cursos/editar_curso.html', context)
