from django import forms
from .models import SignosVitales
import re
from django.utils.safestring import mark_safe
from usuarios.models import Notificacion

class SignosVitalesForm(forms.ModelForm):
    hora = forms.ChoiceField(
        choices=SignosVitales.HORARIOS, 
        widget=forms.Select(attrs={'class': 'form-control'}),
        error_messages={'required': 'La hora es obligatoria'}
    )
    presion_arterial = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '120/80'}),
        error_messages={'required': 'La presión arterial es obligatoria'}
    )
    frecuencia_cardiaca = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'FC'}),
        min_value=20,
        max_value=250,
        error_messages={
            'required': 'La frecuencia cardíaca es obligatoria',
            'min_value': 'La frecuencia cardíaca debe ser mayor a 20',
            'max_value': 'La frecuencia cardíaca debe ser menor a 250',
            'invalid': 'Ingrese un valor numérico válido'
        }
    )
    saturacion = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Saturación O2'}),
        min_value=0,
        max_value=100,
        error_messages={
            'required': 'La saturación de oxígeno es obligatoria',
            'min_value': 'La saturación debe ser mayor o igual a 0%',
            'max_value': 'La saturación no puede ser mayor a 100%',
            'invalid': 'Ingrese un valor numérico válido'
        }
    )
    frecuencia_respiratoria = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'FR'}),
        min_value=0,
        max_value=60,
        error_messages={
            'required': 'La frecuencia respiratoria es obligatoria',
            'min_value': 'La frecuencia respiratoria debe ser mayor o igual a 0',
            'max_value': 'La frecuencia respiratoria debe ser menor a 60',
            'invalid': 'Ingrese un valor numérico válido'
        }
    )
    temperatura = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Temperatura', 'step': '0.1'}),
        min_value=34.0,
        max_value=42.0,
        decimal_places=1,
        error_messages={
            'required': 'La temperatura es obligatoria',
            'min_value': 'La temperatura debe ser mayor a 34.0°C',
            'max_value': 'La temperatura debe ser menor a 42.0°C',
            'invalid': 'Ingrese un valor decimal válido con un decimal'
        }
    )
    hgt = forms.IntegerField(
        required=False, 
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'HGT'}),
        min_value=20,
        max_value=500,
        error_messages={
            'min_value': 'El HGT debe ser mayor a 20 mg/dL',
            'max_value': 'El HGT debe ser menor a 500 mg/dL',
            'invalid': 'Ingrese un valor numérico válido'
        }
    )
    ESTADO_HGT_CHOICES = [
        ('', 'Seleccione'),
        ('ayuno', 'En ayunas'),
        ('postprandial', 'Post prandial')
    ]
    estado_hgt = forms.ChoiceField(
        required=False,
        choices=ESTADO_HGT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Estado para HGT'
    )
    eva = forms.IntegerField(
        required=False, 
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'EVA (1-10)'}),
        min_value=0,
        max_value=10,
        error_messages={
            'min_value': 'EVA debe estar entre 0 y 10',
            'max_value': 'EVA debe estar entre 0 y 10',
            'invalid': 'Ingrese un valor numérico válido'
        }
    )
    
    class Meta:
        model = SignosVitales
        fields = ['hora', 'presion_arterial', 'frecuencia_cardiaca', 'saturacion', 
                 'frecuencia_respiratoria', 'temperatura', 'hgt', 'estado_hgt', 'eva']
        
    def clean_presion_arterial(self):
        presion = self.cleaned_data.get('presion_arterial')
        if not presion:
            return presion
            
        # Verifica el formato correcto (sistólica/diastólica)
        if not re.match(r'^\d{2,3}\/\d{2,3}$', presion):
            raise forms.ValidationError('El formato debe ser sistólica/diastólica (ej: 120/80)')
            
        # Verifica valores dentro de rangos aceptables
        try:
            sistolica, diastolica = map(int, presion.split('/'))
            
            # Validación más específica según los requisitos
            alerta_sistolica = False
            alerta_diastolica = False
            mensaje_alerta = ""
            
            # Rangos para presión sistólica
            if sistolica < 90:
                alerta_sistolica = True
                mensaje_alerta += "Presión sistólica baja. "
            elif sistolica > 139:
                alerta_sistolica = True
                mensaje_alerta += "Presión sistólica alta. "
                
            # Rangos para presión diastólica
            if diastolica < 60:
                alerta_diastolica = True
                mensaje_alerta += "Presión diastólica baja. "
            elif diastolica > 89:
                alerta_diastolica = True
                mensaje_alerta += "Presión diastólica alta. "
            
            # Guardar información de alerta para uso posterior
            self.sistolica_fuera_rango = alerta_sistolica
            self.diastolica_fuera_rango = alerta_diastolica
            self.mensaje_alerta_pa = mensaje_alerta
            
            # Validaciones base
            if sistolica < 40 or sistolica > 250:
                raise forms.ValidationError('La presión sistólica debe estar entre 40 y 250 mmHg')
                
            if diastolica < 20 or diastolica > 150:
                raise forms.ValidationError('La presión diastólica debe estar entre 20 y 150 mmHg')
                
            if sistolica <= diastolica:
                raise forms.ValidationError('La presión sistólica debe ser mayor que la diastólica')
        except ValueError:
            raise forms.ValidationError('Los valores de presión deben ser numéricos')
            
        return presion
        
    def clean_frecuencia_cardiaca(self):
        fc = self.cleaned_data.get('frecuencia_cardiaca')
        if fc is not None:
            self.fc_fuera_rango = fc < 60 or fc > 90
            if self.fc_fuera_rango:
                self.mensaje_alerta_fc = "Frecuencia cardíaca fuera del rango normal (60-90 lpm)."
        return fc
        
    def clean_saturacion(self):
        sat = self.cleaned_data.get('saturacion')
        if sat is not None:
            self.sat_fuera_rango = sat < 95
            if self.sat_fuera_rango:
                self.mensaje_alerta_sat = "Saturación de oxígeno por debajo de 95%."
        return sat
        
    def clean_frecuencia_respiratoria(self):
        fr = self.cleaned_data.get('frecuencia_respiratoria')
        if fr is not None:
            self.fr_fuera_rango = fr < 12 or fr > 20
            if self.fr_fuera_rango:
                self.mensaje_alerta_fr = "Frecuencia respiratoria fuera del rango normal (12-20 rpm)."
        return fr
        
    def clean_temperatura(self):
        temp = self.cleaned_data.get('temperatura')
        if temp is not None:
            temp_valor = float(temp)
            self.temp_clasificacion = ""
            
            if temp_valor < 36.0:
                self.temp_clasificacion = "Hipotermia"
                self.temp_fuera_rango = True
            elif 36.0 <= temp_valor <= 36.9:
                self.temp_clasificacion = "Normal"
                self.temp_fuera_rango = False
            elif 37.0 <= temp_valor <= 37.3:
                self.temp_clasificacion = "Subfebril"
                self.temp_fuera_rango = True
            elif 37.4 <= temp_valor <= 38.5:
                self.temp_clasificacion = "Febril"
                self.temp_fuera_rango = True
            else:  # > 38.5
                self.temp_clasificacion = "Hipertermia"
                self.temp_fuera_rango = True
                
            if self.temp_fuera_rango:
                self.mensaje_alerta_temp = f"Temperatura clasificada como: {self.temp_clasificacion}"
                
        return temp
        
    def clean_hgt(self):
        hgt = self.cleaned_data.get('hgt')
        estado_hgt = self.cleaned_data.get('estado_hgt')
        
        if hgt is not None and estado_hgt:
            self.hgt_fuera_rango = False
            
            if estado_hgt == 'ayuno':
                if hgt < 60:
                    self.hgt_fuera_rango = True
                    self.mensaje_alerta_hgt = "Glicemia en ayunas por debajo del rango normal (< 60 mg/dL)."
                elif hgt > 125:
                    self.hgt_fuera_rango = True
                    if hgt > 125 and hgt <= 180:
                        self.mensaje_alerta_hgt = "Glicemia en ayunas elevada. Posible resistencia a la insulina o intolerancia a la glucosa."
                    else:
                        self.mensaje_alerta_hgt = "Glicemia en ayunas muy elevada."
            
            elif estado_hgt == 'postprandial':
                if hgt > 180:
                    self.hgt_fuera_rango = True
                    self.mensaje_alerta_hgt = "Glicemia postprandial por encima del valor esperado (> 180 mg/dL)."
        
        return hgt
    
    def clean_eva(self):
        eva = self.cleaned_data.get('eva')
        if eva is not None and (eva < 0 or eva > 10):
            raise forms.ValidationError('EVA debe estar entre 0 y 10')
        return eva
        
    def get_alertas(self):
        """Retorna todas las alertas generadas durante la validación"""
        alertas = []
        
        # Revisar cada signo vital y agregar alerta si corresponde
        if hasattr(self, 'sistolica_fuera_rango') and (self.sistolica_fuera_rango or self.diastolica_fuera_rango):
            alertas.append(self.mensaje_alerta_pa)
            
        if hasattr(self, 'fc_fuera_rango') and self.fc_fuera_rango:
            alertas.append(self.mensaje_alerta_fc)
            
        if hasattr(self, 'sat_fuera_rango') and self.sat_fuera_rango:
            alertas.append(self.mensaje_alerta_sat)
            
        if hasattr(self, 'fr_fuera_rango') and self.fr_fuera_rango:
            alertas.append(self.mensaje_alerta_fr)
            
        if hasattr(self, 'temp_fuera_rango') and self.temp_fuera_rango:
            alertas.append(self.mensaje_alerta_temp)
            
        if hasattr(self, 'hgt_fuera_rango') and self.hgt_fuera_rango:
            alertas.append(self.mensaje_alerta_hgt)
            
        return alertas 