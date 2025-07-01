#!/usr/bin/env python
"""
Script para instalar dependencias de Firebase
"""
import subprocess
import sys
import os

def install_package(package):
    """Instalar un paquete usando pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✓ {package} instalado correctamente")
        return True
    except subprocess.CalledProcessError:
        print(f"✗ Error instalando {package}")
        return False

def main():
    """Función principal"""
    print("Instalando dependencias de Firebase...")
    print("=" * 50)
    
    # Lista de paquetes de Firebase
    firebase_packages = [
        "firebase-admin==6.4.0",
        "pyrebase4==4.7.1",
    ]
    
    # Instalar cada paquete
    success_count = 0
    for package in firebase_packages:
        if install_package(package):
            success_count += 1
    
    print("=" * 50)
    print(f"Instalación completada: {success_count}/{len(firebase_packages)} paquetes instalados")
    
    if success_count == len(firebase_packages):
        print("✓ Todas las dependencias de Firebase han sido instaladas correctamente")
        print("\nPróximos pasos:")
        print("1. Configura las variables de entorno en el archivo .env")
        print("2. Descarga el archivo de clave de servicio de Firebase")
        print("3. Ejecuta el script de migración: python migrate_to_firebase.py")
    else:
        print("✗ Algunas dependencias no se pudieron instalar")
        print("Revisa los errores e intenta instalar manualmente")

if __name__ == "__main__":
    main() 