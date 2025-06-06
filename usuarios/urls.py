from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Autenticación
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('password_reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', views.password_reset_done, name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', views.password_reset_complete, name='password_reset_complete'),
    path('password_change/', views.CustomPasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', views.password_change_done, name='password_change_done'),
    
    # Gestión de usuarios
    path('registro/', views.RegistroUsuarioView.as_view(), name='registro_usuario'),
    path('lista/', views.ListaUsuariosView.as_view(), name='lista_usuarios'),
    path('editar/<int:pk>/', views.EditarUsuarioView.as_view(), name='editar_usuario'),
    path('desactivar/<int:pk>/', views.desactivar_usuario, name='desactivar_usuario'),
    path('activar/<int:pk>/', views.activar_usuario, name='activar_usuario'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # Perfil y configuración
    path('perfil/', views.perfil_usuario, name='perfil_usuario'),
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),
    path('notificaciones/', views.mis_notificaciones, name='mis_notificaciones'),
    path('notificaciones/<int:notificacion_id>/leida/', views.marcar_notificacion_leida, name='marcar_notificacion_leida'),
    path('notificaciones/<int:notificacion_id>/eliminar/', views.eliminar_notificacion, name='eliminar_notificacion'),
    path('configuracion/', views.configuracion, name='configuracion'),
    path('configuracion/actualizar/', views.actualizar_configuracion, name='actualizar_configuracion'),
    path('acciones-rapidas/', views.acciones_rapidas, name='acciones_rapidas'),
    
    # Cursos
    path('cursos/', views.mis_cursos, name='mis_cursos'),
    path('cursos/lista/', views.lista_cursos, name='lista_cursos'),
    path('cursos/crear/', views.crear_curso, name='crear_curso'),
    path('cursos/<int:curso_id>/', views.detalle_curso, name='detalle_curso'),
    path('cursos/<int:curso_id>/invitar/', views.invitar_estudiantes, name='invitar_estudiantes'),
    path('invitacion/<uuid:token>/', views.aceptar_invitacion, name='aceptar_invitacion'),
    path('registro/<uuid:token>/', views.registro_con_invitacion, name='registro_con_invitacion'),
    
    # URLs de administración de usuarios
    path('usuarios/lista/', views.ListaUsuariosView.as_view(), name='lista_usuarios'),
    path('usuarios/registrar/', views.RegistroUsuarioView.as_view(), name='registro_usuario'),
    path('usuarios/editar/<int:pk>/', views.EditarUsuarioView.as_view(), name='editar_usuario'),
    path('usuarios/desactivar/<int:pk>/', views.desactivar_usuario, name='desactivar_usuario'),
    path('usuarios/activar/<int:pk>/', views.activar_usuario, name='activar_usuario'),
    path('usuarios/configurar-permisos-admin/', views.configurar_permisos_admin, name='configurar_permisos_admin'),
    path('usuarios/verificar-estado-admin/', views.verificar_estado_admin, name='verificar_estado_admin'),
    
    # URLs de perfil - CORREGIDO: vista 'perfil' no existe, se usa 'perfil_usuario'
    path('perfil/', views.perfil_usuario, name='perfil'),
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),
    
    # URLs de notificaciones - CORREGIDO: vista 'notificaciones' no existe, se usa 'mis_notificaciones'
    path('notificaciones/', views.mis_notificaciones, name='notificaciones'),
    path('notificaciones/marcar-leida/<int:pk>/', views.marcar_notificacion_leida, name='marcar_notificacion_leida'),
    # CORREGIDO: 'marcar_todas_leidas' no existe, modificado para usar el POST en mis_notificaciones
    
    # URLs de cursos
    path('cursos/editar/<int:curso_id>/', views.editar_curso, name='editar_curso'),  # Corregido: ahora usa la vista editar_curso
    path('cursos/detalle/<int:curso_id>/', views.detalle_curso, name='detalle_curso'),
    path('cursos/invitar/<int:curso_id>/', views.invitar_estudiantes, name='invitar_estudiantes'),
    path('cursos/invitacion/<str:codigo>/', views.aceptar_invitacion, name='aceptar_invitacion'),
    path('verificar-correo/', views.verificar_configuracion_correo, name='verificar_configuracion_correo'),
] 