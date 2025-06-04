from django.core.management.base import BaseCommand
from django.utils import timezone
from pacientes.models import Dispositivo
from django.db.models import Q
from datetime import date

class Command(BaseCommand):
    help = 'Retira automáticamente los dispositivos que han cumplido su tiempo de instalación'

    def handle(self, *args, **kwargs):
        # Obtener la fecha actual
        hoy = date.today()
        
        # Obtener dispositivos que deben retirarse (su fecha_retiro es hoy o anterior)
        dispositivos_a_retirar = Dispositivo.objects.filter(
            Q(fecha_retiro__lte=hoy) & Q(fecha_retiro__isnull=False)
        )
        
        total_dispositivos = dispositivos_a_retirar.count()
        self.stdout.write(f"Se encontraron {total_dispositivos} dispositivos por retirar")
        
        # Preparar mensaje detallado para los registros
        mensaje_detalle = ""
        
        # Procesar cada dispositivo
        for dispositivo in dispositivos_a_retirar:
            # Obtener información del dispositivo
            tipo = dispositivo.get_tipo_display_completo()
            paciente = dispositivo.paciente.nombre
            fecha_instalacion = dispositivo.fecha_instalacion
            dias = dispositivo.dias_instalacion
            
            # Mostrar información de dispositivo y paciente
            mensaje = f"Dispositivo: {tipo} - Paciente: {paciente} - "
            mensaje += f"Instalado: {fecha_instalacion} - Días programados: {dias}"
            self.stdout.write(mensaje)
            mensaje_detalle += mensaje + "\n"
            
            # Eliminar el dispositivo
            dispositivo.delete()
        
        # Mensaje final
        if total_dispositivos > 0:
            self.stdout.write(self.style.SUCCESS(f"Se han retirado {total_dispositivos} dispositivos exitosamente"))
        else:
            self.stdout.write(self.style.WARNING("No hay dispositivos que deban retirarse hoy"))
        
        return f"Retirados {total_dispositivos} dispositivos" 