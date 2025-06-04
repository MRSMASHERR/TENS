from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'rut', 'rol', 'activo', 'es_paciente')
    list_filter = ('rol', 'activo', 'es_paciente')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'rut')
    ordering = ('username',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información Personal', {'fields': ('first_name', 'last_name', 'email', 'rut')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Configuración Adicional', {'fields': ('rol', 'activo', 'es_paciente')}),
        ('Fechas Importantes', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'rut', 'rol', 'activo', 'es_paciente'),
        }),
    )

admin.site.register(Usuario, CustomUserAdmin)
