from django import forms
from .models import BalanceHidrico

class BalanceHidricoForm(forms.ModelForm):
    hora = forms.ChoiceField(
        choices=BalanceHidrico.HORARIOS, 
        widget=forms.Select(attrs={'class': 'form-control'}),
        error_messages={'required': 'La hora es obligatoria'}
    )
    
    # Ingresos
    agua = forms.IntegerField(
        min_value=0,
        max_value=5000,
        widget=forms.NumberInput(attrs={
            'class': 'form-control ingreso',
            'placeholder': '0'
        }),
        error_messages={
            'required': 'Este campo es obligatorio',
            'min_value': 'El valor no puede ser negativo',
            'max_value': 'El valor no puede exceder los 5000 ml',
            'invalid': 'Ingrese un valor numérico válido'
        }
    )
    soluciones = forms.IntegerField(
        min_value=0,
        max_value=5000,
        widget=forms.NumberInput(attrs={
            'class': 'form-control ingreso',
            'placeholder': '0'
        }),
        error_messages={
            'required': 'Este campo es obligatorio',
            'min_value': 'El valor no puede ser negativo',
            'max_value': 'El valor no puede exceder los 5000 ml',
            'invalid': 'Ingrese un valor numérico válido'
        }
    )
    alimentos = forms.IntegerField(
        min_value=0,
        max_value=3000,
        widget=forms.NumberInput(attrs={
            'class': 'form-control ingreso',
            'placeholder': '0'
        }),
        error_messages={
            'required': 'Este campo es obligatorio',
            'min_value': 'El valor no puede ser negativo',
            'max_value': 'El valor no puede exceder los 3000 ml',
            'invalid': 'Ingrese un valor numérico válido'
        }
    )
    medicamentos_sueros = forms.IntegerField(
        min_value=0,
        max_value=5000,
        widget=forms.NumberInput(attrs={
            'class': 'form-control ingreso',
            'placeholder': '0'
        }),
        error_messages={
            'required': 'Este campo es obligatorio',
            'min_value': 'El valor no puede ser negativo',
            'max_value': 'El valor no puede exceder los 5000 ml',
            'invalid': 'Ingrese un valor numérico válido'
        }
    )
    
    # Egresos
    orina = forms.IntegerField(
        min_value=0,
        max_value=5000,
        widget=forms.NumberInput(attrs={
            'class': 'form-control egreso',
            'placeholder': '0'
        }),
        error_messages={
            'required': 'Este campo es obligatorio',
            'min_value': 'El valor no puede ser negativo',
            'max_value': 'El valor no puede exceder los 5000 ml',
            'invalid': 'Ingrese un valor numérico válido'
        }
    )
    deposiciones = forms.ChoiceField(
        choices=BalanceHidrico.PRESENCIA_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        }),
        error_messages={
            'required': 'Este campo es obligatorio'
        }
    )
    vomito = forms.ChoiceField(
        choices=BalanceHidrico.PRESENCIA_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        }),
        error_messages={
            'required': 'Este campo es obligatorio'
        }
    )
    hemoderivado = forms.IntegerField(
        min_value=0,
        max_value=5000,
        widget=forms.NumberInput(attrs={
            'class': 'form-control egreso',
            'placeholder': '0'
        }),
        error_messages={
            'required': 'Este campo es obligatorio',
            'min_value': 'El valor no puede ser negativo',
            'max_value': 'El valor no puede exceder los 5000 ml',
            'invalid': 'Ingrese un valor numérico válido'
        }
    )
    drenaje = forms.IntegerField(
        min_value=0,
        max_value=5000,
        widget=forms.NumberInput(attrs={
            'class': 'form-control egreso',
            'placeholder': '0'
        }),
        error_messages={
            'required': 'Este campo es obligatorio',
            'min_value': 'El valor no puede ser negativo',
            'max_value': 'El valor no puede exceder los 5000 ml',
            'invalid': 'Ingrese un valor numérico válido'
        }
    )
    
    observaciones = forms.CharField(
        required=False,
        max_length=500,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Observaciones adicionales'
        }),
        error_messages={
            'max_length': 'Las observaciones no pueden exceder los 500 caracteres'
        }
    )
    
    class Meta:
        model = BalanceHidrico
        fields = ['hora', 'agua', 'soluciones', 'alimentos', 'medicamentos_sueros', 'orina', 'hemoderivado', 'drenaje', 'deposiciones', 'vomito', 'observaciones']
        
    def clean(self):
        cleaned_data = super().clean()
        
        # Comprobar que haya al menos un ingreso o egreso con valor
        ingresos = [
            cleaned_data.get('agua', 0) or 0,
            cleaned_data.get('soluciones', 0) or 0,
            cleaned_data.get('alimentos', 0) or 0,
            cleaned_data.get('medicamentos_sueros', 0) or 0
        ]
        
        # Egresos medibles en ml
        egresos = [
            cleaned_data.get('orina', 0) or 0,
            cleaned_data.get('hemoderivado', 0) or 0,
            cleaned_data.get('drenaje', 0) or 0
        ]
        
        if sum(ingresos) == 0 and sum(egresos) == 0 and cleaned_data.get('deposiciones') == '-' and cleaned_data.get('vomito') == '-':
            raise forms.ValidationError('Debe ingresar al menos un valor para ingresos o egresos')
            
        # Validar balance extremo (positivo o negativo)
        balance = sum(ingresos) - sum(egresos)
        if balance > 5000:
            self.add_error(None, forms.ValidationError('El balance positivo es demasiado alto (>5000ml). Verifique los valores.'))
        elif balance < -5000:
            self.add_error(None, forms.ValidationError('El balance negativo es demasiado alto (<-5000ml). Verifique los valores.'))
            
        return cleaned_data 