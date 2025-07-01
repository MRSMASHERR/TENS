#!/usr/bin/env python
"""
Script para migrar datos de Django/MySQL a Firebase Firestore
"""
import os
import sys
import django
from datetime import datetime
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_medico.settings')
django.setup()

from django.contrib.auth import get_user_model
from pacientes.models import Paciente, Dispositivo
from signos_vitales.models import SignosVitales
from balance_hidrico.models import BalanceHidrico
from evoluciones.models import Evolucion
from usuarios.models import Notificacion, ConfiguracionUsuario, Curso, InvitacionCurso
from sistema_medico.firebase_adapters import (
    FirebaseAdapter, UsuarioRealtimeManager, PacienteRealtimeManager,
    SignosVitalesRealtimeManager, BalanceHidricoRealtimeManager,
    EvolucionRealtimeManager
)

Usuario = get_user_model()

class FirebaseMigrator:
    """Clase para migrar datos a Firebase"""
    
    def __init__(self):
        self.adapter = FirebaseAdapter()
        self.usuario_manager = UsuarioRealtimeManager()
        self.paciente_manager = PacienteRealtimeManager()
        self.signos_manager = SignosVitalesRealtimeManager()
        self.balance_manager = BalanceHidricoRealtimeManager()
        self.evolucion_manager = EvolucionRealtimeManager()
        
        # Mapeo de IDs para mantener referencias
        self.id_mapping = {
            'usuarios': {},
            'pacientes': {},
            'cursos': {},
        }
    
    def migrate_usuarios(self):
        """Migrar usuarios"""
        print("Migrando usuarios...")
        usuarios = Usuario.objects.all()
        
        for usuario in usuarios:
            try:
                # Convertir modelo a diccionario
                usuario_data = self.adapter.model_to_dict(usuario)
                
                # Crear en Realtime Database
                realtime_id = self.usuario_manager.create(usuario_data)
                
                # Guardar mapeo de IDs
                self.id_mapping['usuarios'][usuario.pk] = realtime_id
                
                print(f"  Usuario migrado: {usuario.username} -> {realtime_id}")
                
            except Exception as e:
                print(f"  Error migrando usuario {usuario.username}: {e}")
    
    def migrate_cursos(self):
        """Migrar cursos"""
        print("Migrando cursos...")
        cursos = Curso.objects.all()
        
        for curso in cursos:
            try:
                curso_data = self.adapter.model_to_dict(curso)
                
                # Actualizar referencias de docente y estudiantes
                if curso.docente_id in self.id_mapping['usuarios']:
                    curso_data['docente_id'] = self.id_mapping['usuarios'][curso.docente_id]
                
                # Crear en Realtime Database
                realtime_id = self.usuario_manager.create(curso_data)
                self.id_mapping['cursos'][curso.pk] = realtime_id
                
                print(f"  Curso migrado: {curso.nombre} -> {realtime_id}")
                
            except Exception as e:
                print(f"  Error migrando curso {curso.nombre}: {e}")
    
    def migrate_pacientes(self):
        """Migrar pacientes"""
        print("Migrando pacientes...")
        pacientes = Paciente.objects.all()
        
        for paciente in pacientes:
            try:
                paciente_data = self.adapter.model_to_dict(paciente)
                
                # Actualizar referencias
                if paciente.registrado_por_id in self.id_mapping['usuarios']:
                    paciente_data['registrado_por_id'] = self.id_mapping['usuarios'][paciente.registrado_por_id]
                
                if paciente.usuario_asociado_id in self.id_mapping['usuarios']:
                    paciente_data['usuario_asociado_id'] = self.id_mapping['usuarios'][paciente.usuario_asociado_id]
                
                if paciente.curso_id in self.id_mapping['cursos']:
                    paciente_data['curso_id'] = self.id_mapping['cursos'][paciente.curso_id]
                
                # Crear en Realtime Database
                realtime_id = self.paciente_manager.create(paciente_data)
                self.id_mapping['pacientes'][paciente.pk] = realtime_id
                
                print(f"  Paciente migrado: {paciente.nombre} -> {realtime_id}")
                
            except Exception as e:
                print(f"  Error migrando paciente {paciente.nombre}: {e}")
    
    def migrate_dispositivos(self):
        """Migrar dispositivos"""
        print("Migrando dispositivos...")
        dispositivos = Dispositivo.objects.all()
        
        for dispositivo in dispositivos:
            try:
                dispositivo_data = self.adapter.model_to_dict(dispositivo)
                
                # Actualizar referencias
                if dispositivo.paciente_id in self.id_mapping['pacientes']:
                    dispositivo_data['paciente_id'] = self.id_mapping['pacientes'][dispositivo.paciente_id]
                
                if dispositivo.registrado_por_id in self.id_mapping['usuarios']:
                    dispositivo_data['registrado_por_id'] = self.id_mapping['usuarios'][dispositivo.registrado_por_id]
                
                # Crear en Realtime Database
                realtime_id = self.paciente_manager.create(dispositivo_data)
                
                print(f"  Dispositivo migrado: {dispositivo.get_tipo_display_completo()} -> {realtime_id}")
                
            except Exception as e:
                print(f"  Error migrando dispositivo: {e}")
    
    def migrate_signos_vitales(self):
        """Migrar signos vitales"""
        print("Migrando signos vitales...")
        signos = SignosVitales.objects.all()
        
        for signo in signos:
            try:
                signo_data = self.adapter.model_to_dict(signo)
                
                # Actualizar referencias
                if signo.paciente_id in self.id_mapping['pacientes']:
                    signo_data['paciente_id'] = self.id_mapping['pacientes'][signo.paciente_id]
                
                if signo.registrado_por_id in self.id_mapping['usuarios']:
                    signo_data['registrado_por_id'] = self.id_mapping['usuarios'][signo.registrado_por_id]
                
                # Crear en Realtime Database
                realtime_id = self.signos_manager.create(signo_data)
                
                print(f"  Signos vitales migrados: {signo.fecha_registro} -> {realtime_id}")
                
            except Exception as e:
                print(f"  Error migrando signos vitales: {e}")
    
    def migrate_balance_hidrico(self):
        """Migrar balance hídrico"""
        print("Migrando balance hídrico...")
        balances = BalanceHidrico.objects.all()
        
        for balance in balances:
            try:
                balance_data = self.adapter.model_to_dict(balance)
                
                # Actualizar referencias
                if balance.paciente_id in self.id_mapping['pacientes']:
                    balance_data['paciente_id'] = self.id_mapping['pacientes'][balance.paciente_id]
                
                if balance.registrado_por_id in self.id_mapping['usuarios']:
                    balance_data['registrado_por_id'] = self.id_mapping['usuarios'][balance.registrado_por_id]
                
                # Crear en Realtime Database
                realtime_id = self.balance_manager.create(balance_data)
                
                print(f"  Balance hídrico migrado: {balance.fecha} -> {realtime_id}")
                
            except Exception as e:
                print(f"  Error migrando balance hídrico: {e}")
    
    def migrate_evoluciones(self):
        """Migrar evoluciones"""
        print("Migrando evoluciones...")
        evoluciones = Evolucion.objects.all()
        
        for evolucion in evoluciones:
            try:
                evolucion_data = self.adapter.model_to_dict(evolucion)
                
                # Actualizar referencias
                if evolucion.paciente_id in self.id_mapping['pacientes']:
                    evolucion_data['paciente_id'] = self.id_mapping['pacientes'][evolucion.paciente_id]
                
                if evolucion.registrado_por_id in self.id_mapping['usuarios']:
                    evolucion_data['registrado_por_id'] = self.id_mapping['usuarios'][evolucion.registrado_por_id]
                
                # Crear en Realtime Database
                realtime_id = self.evolucion_manager.create(evolucion_data)
                
                print(f"  Evolución migrada: {evolucion.fecha} -> {realtime_id}")
                
            except Exception as e:
                print(f"  Error migrando evolución: {e}")
    
    def migrate_notificaciones(self):
        """Migrar notificaciones"""
        print("Migrando notificaciones...")
        notificaciones = Notificacion.objects.all()
        
        for notificacion in notificaciones:
            try:
                notificacion_data = self.adapter.model_to_dict(notificacion)
                
                # Actualizar referencias
                if notificacion.usuario_id in self.id_mapping['usuarios']:
                    notificacion_data['usuario_id'] = self.id_mapping['usuarios'][notificacion.usuario_id]
                
                # Crear en Realtime Database
                realtime_id = self.usuario_manager.create(notificacion_data)
                
                print(f"  Notificación migrada: {notificacion.titulo} -> {realtime_id}")
                
            except Exception as e:
                print(f"  Error migrando notificación: {e}")
    
    def migrate_configuraciones(self):
        """Migrar configuraciones de usuario"""
        print("Migrando configuraciones...")
        configuraciones = ConfiguracionUsuario.objects.all()
        
        for config in configuraciones:
            try:
                config_data = self.adapter.model_to_dict(config)
                
                # Actualizar referencias
                if config.usuario_id in self.id_mapping['usuarios']:
                    config_data['usuario_id'] = self.id_mapping['usuarios'][config.usuario_id]
                
                # Crear en Realtime Database
                realtime_id = self.usuario_manager.create(config_data)
                
                print(f"  Configuración migrada: {config.usuario.username} -> {realtime_id}")
                
            except Exception as e:
                print(f"  Error migrando configuración: {e}")
    
    def migrate_invitaciones(self):
        """Migrar invitaciones a cursos"""
        print("Migrando invitaciones...")
        invitaciones = InvitacionCurso.objects.all()
        
        for invitacion in invitaciones:
            try:
                invitacion_data = self.adapter.model_to_dict(invitacion)
                
                # Actualizar referencias
                if invitacion.curso_id in self.id_mapping['cursos']:
                    invitacion_data['curso_id'] = self.id_mapping['cursos'][invitacion.curso_id]
                
                if invitacion.enviada_por_id in self.id_mapping['usuarios']:
                    invitacion_data['enviada_por_id'] = self.id_mapping['usuarios'][invitacion.enviada_por_id]
                
                # Crear en Realtime Database
                realtime_id = self.usuario_manager.create(invitacion_data)
                
                print(f"  Invitación migrada: {invitacion.email} -> {realtime_id}")
                
            except Exception as e:
                print(f"  Error migrando invitación: {e}")
    
    def save_mapping(self):
        """Guardar el mapeo de IDs en un archivo"""
        with open('firebase_migration_mapping.json', 'w') as f:
            json.dump(self.id_mapping, f, indent=2)
        print("Mapeo de IDs guardado en firebase_migration_mapping.json")
    
    def run_migration(self):
        """Ejecutar toda la migración"""
        print("Iniciando migración a Firebase...")
        print("=" * 50)
        
        try:
            self.migrate_usuarios()
            self.migrate_cursos()
            self.migrate_pacientes()
            self.migrate_dispositivos()
            self.migrate_signos_vitales()
            self.migrate_balance_hidrico()
            self.migrate_evoluciones()
            self.migrate_notificaciones()
            self.migrate_configuraciones()
            self.migrate_invitaciones()
            
            self.save_mapping()
            
            print("=" * 50)
            print("¡Migración completada exitosamente!")
            
        except Exception as e:
            print(f"Error durante la migración: {e}")
            raise

if __name__ == '__main__':
    migrator = FirebaseMigrator()
    migrator.run_migration() 