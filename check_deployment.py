#!/usr/bin/env python
"""
Script para verificar la configuración del despliegue en Render
"""
import os
import sys
import django
from pathlib import Path

# Configurar Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_medico.settings')
django.setup()

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import execute_from_command_line

User = get_user_model()

def check_environment():
    """Verificar variables de entorno críticas"""
    print("🔍 Verificando variables de entorno...")
    
    critical_vars = [
        'DJANGO_SECRET_KEY',
        'DEBUG',
        'USE_FIREBASE',
    ]
    
    for var in critical_vars:
        value = os.environ.get(var)
        if value:
            print(f"✅ {var}: {'*' * len(value) if 'SECRET' in var else value}")
        else:
            print(f"❌ {var}: No definida")
    
    print()

def check_database():
    """Verificar configuración de base de datos"""
    print("🗄️ Verificando configuración de base de datos...")
    
    print(f"Base de datos: {settings.DATABASES['default']['ENGINE']}")
    print(f"Nombre: {settings.DATABASES['default']['NAME']}")
    print(f"Usar Firebase: {getattr(settings, 'USE_FIREBASE', False)}")
    
    try:
        # Intentar hacer una consulta simple
        user_count = User.objects.count()
        print(f"✅ Usuarios en base de datos: {user_count}")
    except Exception as e:
        print(f"❌ Error al conectar con la base de datos: {e}")
    
    print()

def check_static_files():
    """Verificar configuración de archivos estáticos"""
    print("📁 Verificando archivos estáticos...")
    
    print(f"STATIC_URL: {settings.STATIC_URL}")
    print(f"STATIC_ROOT: {settings.STATIC_ROOT}")
    print(f"STATICFILES_STORAGE: {settings.STATICFILES_STORAGE}")
    
    static_root = Path(settings.STATIC_ROOT)
    if static_root.exists():
        print(f"✅ STATIC_ROOT existe: {static_root}")
    else:
        print(f"❌ STATIC_ROOT no existe: {static_root}")
    
    print()

def check_security_settings():
    """Verificar configuración de seguridad"""
    print("🔒 Verificando configuración de seguridad...")
    
    print(f"DEBUG: {settings.DEBUG}")
    print(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
    print(f"CSRF_COOKIE_SECURE: {settings.CSRF_COOKIE_SECURE}")
    print(f"SESSION_COOKIE_SECURE: {settings.SESSION_COOKIE_SECURE}")
    print(f"CSRF_TRUSTED_ORIGINS: {settings.CSRF_TRUSTED_ORIGINS}")
    
    if hasattr(settings, 'CORS_ALLOWED_ORIGINS'):
        print(f"CORS_ALLOWED_ORIGINS: {settings.CORS_ALLOWED_ORIGINS}")
    
    print()

def check_middleware():
    """Verificar middleware"""
    print("⚙️ Verificando middleware...")
    
    for i, middleware in enumerate(settings.MIDDLEWARE):
        print(f"{i+1}. {middleware}")
    
    print()

def check_installed_apps():
    """Verificar aplicaciones instaladas"""
    print("📱 Verificando aplicaciones instaladas...")
    
    for i, app in enumerate(settings.INSTALLED_APPS):
        print(f"{i+1}. {app}")
    
    print()

def check_superuser():
    """Verificar si existe un superusuario"""
    print("👤 Verificando superusuarios...")
    
    try:
        superusers = User.objects.filter(is_superuser=True)
        if superusers.exists():
            print(f"✅ Superusuarios encontrados: {superusers.count()}")
            for user in superusers:
                print(f"   - {user.username} ({user.email})")
        else:
            print("❌ No se encontraron superusuarios")
            print("   Ejecuta: python manage.py createsuperuser")
    except Exception as e:
        print(f"❌ Error al verificar superusuarios: {e}")
    
    print()

def run_migrations():
    """Ejecutar migraciones pendientes"""
    print("🔄 Ejecutando migraciones...")
    
    try:
        execute_from_command_line(['manage.py', 'migrate', '--verbosity=0'])
        print("✅ Migraciones completadas")
    except Exception as e:
        print(f"❌ Error en migraciones: {e}")
    
    print()

def collect_static():
    """Recolectar archivos estáticos"""
    print("📦 Recolectando archivos estáticos...")
    
    try:
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput', '--verbosity=0'])
        print("✅ Archivos estáticos recolectados")
    except Exception as e:
        print(f"❌ Error al recolectar archivos estáticos: {e}")
    
    print()

def main():
    """Función principal"""
    print("🚀 Verificación de despliegue del Sistema Médico")
    print("=" * 50)
    
    check_environment()
    check_database()
    check_static_files()
    check_security_settings()
    check_middleware()
    check_installed_apps()
    check_superuser()
    
    # Solo ejecutar en desarrollo
    if settings.DEBUG:
        run_migrations()
        collect_static()
    
    print("✅ Verificación completada")

if __name__ == '__main__':
    main() 