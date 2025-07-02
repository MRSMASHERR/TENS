#!/usr/bin/env python
"""
Script de inicialización para Render
Ejecuta migraciones y crea superusuario automáticamente
"""

import os
import sys
import django
import subprocess

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_medico.settings')
django.setup()

def run_command(command):
    """Ejecutar un comando de Django"""
    try:
        result = subprocess.run(
            ['python', 'manage.py'] + command.split(),
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ {command}: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en {command}: {e.stderr}")
        return False

def main():
    print("🚀 Iniciando configuración de Render...")
    
    # 1. Ejecutar migraciones
    print("\n📦 Ejecutando migraciones...")
    if not run_command("migrate"):
        print("❌ Falló la migración")
        return False
    
    # 2. Recolectar archivos estáticos
    print("\n📁 Recolectando archivos estáticos...")
    if not run_command("collectstatic --noinput"):
        print("❌ Falló la recolección de estáticos")
        return False
    
    # 3. Crear superusuario si las variables están configuradas
    print("\n👤 Verificando creación de superusuario...")
    username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
    email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
    password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
    
    if all([username, email, password]):
        print(f"🔑 Creando superusuario: {username}")
        if run_command(f"create_superuser_firebase --username {username} --email {email} --password {password}"):
            print("✅ Superusuario creado exitosamente")
        else:
            print("⚠️ No se pudo crear el superusuario (puede que ya exista)")
    else:
        print("⚠️ Variables de superusuario no configuradas")
        print("Para crear un superusuario, configura estas variables de entorno:")
        print("- DJANGO_SUPERUSER_USERNAME")
        print("- DJANGO_SUPERUSER_EMAIL")
        print("- DJANGO_SUPERUSER_PASSWORD")
    
    print("\n🎉 Configuración completada!")
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 