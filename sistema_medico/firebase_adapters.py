from datetime import datetime, date
from django.utils import timezone
from django.db import models
from .firebase_config import get_database_client, get_pyrebase_client, DATABASE_NODES
import json
import uuid

class FirebaseAdapter:
    """Adaptador para convertir entre modelos Django y nodos de Realtime Database"""
    
    def __init__(self):
        self.db = get_database_client()
        self.pyrebase = get_pyrebase_client()
    
    def model_to_dict(self, model_instance):
        """Convierte un modelo Django a un diccionario compatible con Realtime Database"""
        data = {}
        
        for field in model_instance._meta.fields:
            value = getattr(model_instance, field.name)
            
            # Manejar tipos de datos especiales
            if isinstance(value, (datetime, date)):
                data[field.name] = value.isoformat()
            elif hasattr(value, 'pk'):  # Relaciones ForeignKey
                data[field.name] = str(value.pk)
            elif isinstance(value, (list, dict)):
                data[field.name] = json.dumps(value)
            elif value is not None:
                data[field.name] = value
        
        # Agregar ID del modelo
        data['id'] = str(model_instance.pk)
        data['created_at'] = timezone.now().isoformat()
        
        return data
    
    def dict_to_model_data(self, data_dict, model_class):
        """Convierte un diccionario de Realtime Database a datos compatibles con modelos Django"""
        model_data = {}
        
        for field in model_class._meta.fields:
            field_name = field.name
            if field_name in data_dict:
                value = data_dict[field_name]
                
                # Convertir tipos de datos especiales
                if isinstance(field, (models.DateTimeField, models.DateField)) and value:
                    try:
                        if isinstance(field, models.DateField):
                            model_data[field_name] = datetime.fromisoformat(value).date()
                        else:
                            model_data[field_name] = datetime.fromisoformat(value)
                    except:
                        model_data[field_name] = None
                elif isinstance(field, models.ForeignKey) and value:
                    # Para relaciones, guardamos el ID como string
                    model_data[field_name] = value
                elif isinstance(field, (models.JSONField, models.TextField)) and isinstance(value, str):
                    try:
                        model_data[field_name] = json.loads(value)
                    except:
                        model_data[field_name] = value
                else:
                    model_data[field_name] = value
        
        return model_data

class RealtimeDatabaseManager:
    """Manager para operaciones CRUD con Realtime Database"""
    
    def __init__(self, node_name):
        self.db = get_database_client()
        self.pyrebase = get_pyrebase_client()
        self.node_name = node_name
        self.node_ref = self.db.child(node_name)
    
    def create(self, data):
        """Crear un nuevo registro"""
        # Generar ID único
        record_id = str(uuid.uuid4())
        data['id'] = record_id
        data['created_at'] = timezone.now().isoformat()
        
        # Guardar en la base de datos
        self.node_ref.child(record_id).set(data)
        return record_id
    
    def get(self, record_id):
        """Obtener un registro por ID"""
        snapshot = self.node_ref.child(record_id).get()
        if snapshot:
            return snapshot
        return None
    
    def update(self, record_id, data):
        """Actualizar un registro"""
        data['updated_at'] = timezone.now().isoformat()
        self.node_ref.child(record_id).update(data)
        return record_id
    
    def delete(self, record_id):
        """Eliminar un registro"""
        self.node_ref.child(record_id).delete()
        return True
    
    def list(self, filters=None, order_by=None, limit=None):
        """Listar registros con filtros opcionales"""
        snapshot = self.node_ref.get()
        
        if not snapshot:
            return []
        
        records = []
        for record_id, record_data in snapshot.items():
            if isinstance(record_data, dict):
                record_data['id'] = record_id
                
                # Aplicar filtros
                if filters:
                    matches = True
                    for field, value in filters.items():
                        if field in record_data and record_data[field] != value:
                            matches = False
                            break
                    if not matches:
                        continue
                
                records.append(record_data)
        
        # Aplicar ordenamiento
        if order_by:
            if isinstance(order_by, str):
                records.sort(key=lambda x: x.get(order_by, ''))
            elif isinstance(order_by, (list, tuple)):
                for field in order_by:
                    records.sort(key=lambda x: x.get(field, ''))
        
        # Aplicar límite
        if limit:
            records = records[:limit]
        
        return records
    
    def search(self, field, value):
        """Búsqueda por campo específico"""
        snapshot = self.node_ref.order_by_child(field).equal_to(value).get()
        
        if not snapshot:
            return []
        
        records = []
        for record_id, record_data in snapshot.items():
            if isinstance(record_data, dict):
                record_data['id'] = record_id
                records.append(record_data)
        
        return records
    
    def get_by_key(self, key, value):
        """Obtener registros por clave específica"""
        return self.search(key, value)

# Managers específicos para cada modelo
class UsuarioRealtimeManager(RealtimeDatabaseManager):
    def __init__(self):
        super().__init__(DATABASE_NODES['usuarios'])
    
    def get_by_rut(self, rut):
        """Obtener usuario por RUT"""
        return self.search('rut', rut)

class PacienteRealtimeManager(RealtimeDatabaseManager):
    def __init__(self):
        super().__init__(DATABASE_NODES['pacientes'])
    
    def get_by_rut(self, rut):
        """Obtener paciente por RUT"""
        return self.search('rut', rut)
    
    def get_activos(self):
        """Obtener pacientes activos"""
        return self.search('activo', True)

class SignosVitalesRealtimeManager(RealtimeDatabaseManager):
    def __init__(self):
        super().__init__(DATABASE_NODES['signos_vitales'])
    
    def get_by_paciente(self, paciente_id):
        """Obtener signos vitales por paciente"""
        return self.search('paciente_id', paciente_id)

class BalanceHidricoRealtimeManager(RealtimeDatabaseManager):
    def __init__(self):
        super().__init__(DATABASE_NODES['balance_hidrico'])
    
    def get_by_paciente(self, paciente_id):
        """Obtener balance hídrico por paciente"""
        return self.search('paciente_id', paciente_id)

class EvolucionRealtimeManager(RealtimeDatabaseManager):
    def __init__(self):
        super().__init__(DATABASE_NODES['evoluciones'])
    
    def get_by_paciente(self, paciente_id):
        """Obtener evoluciones por paciente"""
        return self.search('paciente_id', paciente_id) 