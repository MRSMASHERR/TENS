from django import forms
from .models import Evolucion

class EvolucionForm(forms.ModelForm):
    registro = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Registro de evolución'}),
        min_length=10,
        max_length=2000,
        error_messages={
            'required': 'El registro de evolución es obligatorio',
            'min_length': 'El registro debe tener al menos 10 caracteres',
            'max_length': 'El registro no puede exceder los 2000 caracteres'
        }
    )
    indicaciones = forms.CharField(
        required=False, 
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Indicaciones médicas'}),
        max_length=1000,
        error_messages={
            'max_length': 'Las indicaciones no pueden exceder los 1000 caracteres'
        }
    )
    
    class Meta:
        model = Evolucion
        fields = ['registro', 'indicaciones']
        
    def clean_registro(self):
        registro = self.cleaned_data.get('registro')
        if not registro:
            return registro
            
        # Verificar que no contenga solo espacios en blanco
        if registro.strip() == '':
            raise forms.ValidationError('El registro no puede estar vacío')
            
        # Verificar longitud mínima sin contar espacios
        if len(registro.strip()) < 10:
            raise forms.ValidationError('El registro debe contener al menos 10 caracteres significativos')
            
        return registro
        
    def clean(self):
        cleaned_data = super().clean()
        registro = cleaned_data.get('registro', '')
        indicaciones = cleaned_data.get('indicaciones', '')
        
        # Comprobar si las indicaciones son iguales al registro
        if indicaciones and registro and registro.strip() == indicaciones.strip():
            self.add_error('indicaciones', 'Las indicaciones no pueden ser idénticas al registro')
            
        return cleaned_data 