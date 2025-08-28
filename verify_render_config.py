#!/usr/bin/env python
"""
Script para verificar la configuración específica de Render
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

def check_render_environment():
    """Verificar variables de entorno específicas de Render"""
    print("🔍 Verificando configuración de Render...")
    print("=" * 50)
    
    # Variables críticas para Render
    critical_vars = {
        'DJANGO_SECRET_KEY': 'Clave secreta de Django',
        'DEBUG': 'Modo debug',
        'DATABASE_URL': 'URL de base de datos PostgreSQL',
        'USE_FIREBASE': 'Usar Firebase',
        'CSRF_TRUSTED_ORIGINS': 'Orígenes confiables CSRF',
        'CORS_ALLOWED_ORIGINS': 'Orígenes permitidos CORS',
    }
    
    for var, description in critical_vars.items():
        value = os.environ.get(var)
        if value:
            if 'SECRET' in var or 'PASSWORD' in var:
                print(f"✅ {var}: {'*' * 10} ({description})")
            else:
                print(f"✅ {var}: {value} ({description})")
        else:
            print(f"❌ {var}: NO DEFINIDA ({description})")
    
    print()

def check_database_config():
    """Verificar configuración de base de datos"""
    print("🗄️ Verificando configuración de base de datos...")
    
    database_url = os.environ.get('DATABASE_URL')
    debug = os.environ.get('DEBUG', 'False') == 'True'
    
    if database_url and not debug:
        print(f"✅ Usando PostgreSQL en producción")
        print(f"   URL: {database_url[:50]}...")
    else:
        print(f"✅ Usando SQLite en desarrollo")
        print(f"   Archivo: {settings.DATABASES['default']['NAME']}")
    
    print()

def check_security_config():
    """Verificar configuración de seguridad"""
    print("🔒 Verificando configuración de seguridad...")
    
    print(f"DEBUG: {settings.DEBUG}")
    print(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
    print(f"CSRF_COOKIE_SECURE: {settings.CSRF_COOKIE_SECURE}")
    print(f"SESSION_COOKIE_SECURE: {settings.SESSION_COOKIE_SECURE}")
    
    if hasattr(settings, 'CSRF_TRUSTED_ORIGINS'):
        print(f"CSRF_TRUSTED_ORIGINS: {settings.CSRF_TRUSTED_ORIGINS}")
    else:
        print("❌ CSRF_TRUSTED_ORIGINS no configurado")
    
    if hasattr(settings, 'CORS_ALLOWED_ORIGINS'):
        print(f"CORS_ALLOWED_ORIGINS: {settings.CORS_ALLOWED_ORIGINS}")
    else:
        print("❌ CORS_ALLOWED_ORIGINS no configurado")
    
    print()

def check_firebase_config():
    """Verificar configuración de Firebase"""
    print("🔥 Verificando configuración de Firebase...")
    
    firebase_vars = [
        'FIREBASE_API_KEY',
        'FIREBASE_AUTH_DOMAIN',
        'FIREBASE_PROJECT_ID',
        'FIREBASE_STORAGE_BUCKET',
        'FIREBASE_MESSAGING_SENDER_ID',
        'FIREBASE_DATABASE_URL',
    ]
    
    use_firebase = os.environ.get('USE_FIREBASE', 'False') == 'True'
    print(f"USE_FIREBASE: {use_firebase}")
    
    if use_firebase:
        for var in firebase_vars:
            value = os.environ.get(var)
            if value:
                print(f"✅ {var}: Configurado")
            else:
                print(f"❌ {var}: No configurado")
    else:
        print("ℹ️ Firebase no está habilitado")
    
    print()

def check_static_files():
    """Verificar configuración de archivos estáticos"""
    print("📁 Verificando archivos estáticos...")
    
    print(f"STATIC_URL: {settings.STATIC_URL}")
    print(f"STATIC_ROOT: {settings.STATIC_ROOT}")
    print(f"STATICFILES_STORAGE: {settings.STATICFILES_STORAGE}")
    
    static_root = Path(settings.STATIC_ROOT)
    if static_root.exists():
        print(f"✅ STATIC_ROOT existe")
    else:
        print(f"❌ STATIC_ROOT no existe")
    
    print()

def generate_render_commands():
    """Generar comandos recomendados para Render"""
    print("🚀 Comandos recomendados para Render:")
    print("=" * 50)
    
    print("\n📦 Build Command:")
    print("pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate && python init_render.py")
    
    print("\n▶️ Start Command:")
    print("gunicorn sistema_medico.wsgi:application")
    
    print("\n🔧 Variables de entorno faltantes:")
    missing_vars = []
    
    if not os.environ.get('CSRF_TRUSTED_ORIGINS'):
        missing_vars.append('CSRF_TRUSTED_ORIGINS=https://tens.onrender.com')
    
    if not os.environ.get('CORS_ALLOWED_ORIGINS'):
        missing_vars.append('CORS_ALLOWED_ORIGINS=https://tens.onrender.com')
    
    if not os.environ.get('USE_FIREBASE'):
        missing_vars.append('USE_FIREBASE=True')
    
    if missing_vars:
        for var in missing_vars:
            print(f"   {var}")
    else:
        print("   ✅ Todas las variables están configuradas")
    
    print()

def main():
    """Función principal"""
    check_render_environment()
    check_database_config()
    check_security_config()
    check_firebase_config()
    check_static_files()
    generate_render_commands()
    
    print("✅ Verificación completada")

if __name__ == '__main__':
    main() 