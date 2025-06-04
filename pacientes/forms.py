from django import forms
from .models import Paciente, Dispositivo
import re
from datetime import date, timedelta
from itertools import cycle

def validar_rut(rut):
    """
    Función auxiliar para validar RUT chileno utilizando el algoritmo de módulo 11
    Retorna el RUT limpio si es válido o None si es inválido
    
    Esta versión es más permisiva con el formato de entrada
    """
    if not rut:
        return None
    
    # Eliminar puntos, guiones y espacios para normalizar
    rut_limpio = rut.replace(".", "").replace(" ", "").replace("-", "").upper()
    
    # Si el rut es muy corto, no es válido
    if len(rut_limpio) < 2:
        return None
        
    # Extraer el dígito verificador
    dv = rut_limpio[-1]
    # Extraer el número
    rut_num_str = rut_limpio[:-1]
    
    try:
        rut_num = int(rut_num_str)
    except ValueError:
        return None
        
    # Algoritmo para calcular dígito verificador usando módulo 11
    # Invertir dígitos para multiplicación
    reversed_digits = map(int, reversed(str(rut_num)))
    
    # Serie numérica para multiplicar [2,3,4,5,6,7]
    factors = cycle(range(2, 8))
    
    # Sumar productos
    suma = sum(d * f for d, f in zip(reversed_digits, factors))
    
    # Calcular dígito verificador con módulo 11
    remainder = suma % 11
    dv_calculated = 11 - remainder
    
    # Convertir a caracter según reglas del RUT
    if dv_calculated == 11:
        dv_expected = '0'
    elif dv_calculated == 10:
        dv_expected = 'K'
    else:
        dv_expected = str(dv_calculated)
        
    # Validar que el dígito verificador sea correcto
    if dv != dv_expected:
        return None
        
    # Retornar RUT formateado correctamente
    return f"{rut_num}-{dv}"

class PacienteForm(forms.ModelForm):
    nombre = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre completo'}),
        min_length=3,
        max_length=100,
        error_messages={
            'required': 'El nombre es obligatorio',
            'min_length': 'El nombre debe tener al menos 3 caracteres',
            'max_length': 'El nombre no puede exceder los 100 caracteres'
        }
    )
    rut = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'RUT (sin puntos y con guión)'}),
        error_messages={
            'required': 'El RUT es obligatorio'
        }
    )
    fecha_nacimiento = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        error_messages={
            'required': 'La fecha de nacimiento es obligatoria',
            'invalid': 'Formato de fecha inválido, use DD/MM/AAAA'
        }
    )
    # Campo edad para mostrar solo, no se guardará directamente
    edad_mostrar = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Se calcula automáticamente', 
            'readonly': 'readonly'
        }),
        required=False,
        error_messages={
            'invalid': 'La edad se calcula automáticamente'
        }
    )
    sala_cama = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Sala/Cama'}),
        max_length=20,
        error_messages={
            'required': 'La información de sala/cama es obligatoria',
            'max_length': 'La información de sala/cama no puede exceder los 20 caracteres'
        }
    )
    dias_hospitalizacion = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Días de hospitalización'}),
        min_value=0,
        error_messages={
            'required': 'Los días de hospitalización son obligatorios',
            'min_value': 'Los días de hospitalización no pueden ser negativos',
            'invalid': 'Ingrese un número válido para los días de hospitalización'
        }
    )
    
    # Campos de contacto
    genero = forms.ChoiceField(
        choices=Paciente.OPCIONES_GENERO,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_genero'}),
        required=True
    )
    
    genero_otro = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control mt-2',
            'placeholder': 'Especifique su género',
            'id': 'id_genero_otro',
            'style': 'display: none;'
        })
    )
    
    telefono = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono de contacto'}),
        max_length=20,
        required=False
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'}),
        required=False
    )
    
    direccion = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección del paciente'}),
        max_length=200,
        required=False
    )
    
    alergias = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'placeholder': 'Ej: Penicilina, aspirina, látex', 
            'rows': 3
        }),
        required=False,
        label='Alergias',
        help_text='Indique las alergias del paciente, separadas por comas'
    )
    
    # Nuevos campos
    antecedentes_morbidos = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'placeholder': 'Antecedentes mórbidos del paciente',
            'rows': 3
        }),
        required=False,
        label='Antecedentes Mórbidos'
    )
    
    # Campos adicionales
    motivo_consulta = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'placeholder': 'Motivo de consulta',
            'rows': 3
        }),
        required=False,
        label='Motivo Consulta'
    )
    
    diagnostico = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'placeholder': 'Diagnóstico',
            'rows': 3
        }),
        required=False,
        label='Diagnóstico'
    )
    
    # Hábitos como en la imagen
    tabaquismo = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    alcoholismo = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    drogas = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Especifique cuál',
        }),
        label='Drogas'
    )
    
    # Brazalete como opción marcable (si/no)
    brazalete = forms.ChoiceField(
        choices=Paciente.OPCIONES_BRAZALETE,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        required=True,
        initial='NO'
    )
    
    # Previsión como en la imagen
    prevision = forms.ChoiceField(
        choices=Paciente.OPCIONES_PREVISION,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        required=True,
        initial='FONASA'
    )
    
    prevision_otra = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Especifique otra previsión',
        })
    )
    
    class Meta:
        model = Paciente
        fields = [
            'nombre', 'rut', 'fecha_nacimiento', 'sala_cama', 'dias_hospitalizacion', 
            'alergias', 'antecedentes_morbidos', 'motivo_consulta', 'diagnostico', 'tabaquismo', 'alcoholismo', 'drogas',
            'brazalete', 'prevision', 'prevision_otra', 'curso', 'genero', 'genero_otro', 'telefono', 'email', 'direccion'
        ]
        # El campo edad no se incluye aquí ya que es editable=False en el modelo

    def __init__(self, *args, curso=None, **kwargs):
        super().__init__(*args, **kwargs)
        if curso:
            self.fields['curso'].initial = curso
            self.fields['curso'].widget = forms.HiddenInput()
        else:
            self.fields['curso'].widget = forms.HiddenInput()
            self.fields['curso'].required = False

    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        if not rut:
            return rut
            
        rut_validado = validar_rut(rut)
        if not rut_validado:
            raise forms.ValidationError('RUT inválido. Por favor verifica el número y dígito verificador')
        
        # Obtener el curso del formulario
        curso = self.cleaned_data.get('curso') or self.initial.get('curso')
        
        # Comprobar si ya existe un paciente con ese RUT en el mismo curso
        if self.instance and self.instance.pk:
            # Si estamos editando un paciente existente
            if self.instance.rut != rut_validado:
                # Si cambiamos el RUT, verificar que no exista otro con ese RUT en el mismo curso
                if Paciente.objects.filter(rut=rut_validado, curso=curso).exists():
                    raise forms.ValidationError('Ya existe un paciente con este RUT en este curso')
        else:
            # Si estamos creando un nuevo paciente
            if Paciente.objects.filter(rut=rut_validado, curso=curso).exists():
                raise forms.ValidationError('Ya existe un paciente con este RUT en este curso')
                
        return rut_validado
        
    def clean_fecha_nacimiento(self):
        fecha_nac = self.cleaned_data.get('fecha_nacimiento')
        
        if not fecha_nac:
            return fecha_nac
            
        # Verificar que la fecha no sea futura
        if fecha_nac > date.today():
            raise forms.ValidationError('La fecha de nacimiento no puede ser futura')
            
        # Verificar edad mínima y máxima razonable
        edad_calculada = self.calcular_edad(fecha_nac)
        if edad_calculada > 120:
            raise forms.ValidationError('La fecha de nacimiento indica una edad mayor a 120 años, verifique la fecha')
        
        # Si es recién nacido o bebé menor de 1 mes, mostrar advertencia pero permitir
        if edad_calculada == 0:
            dias_edad = (date.today() - fecha_nac).days
            if dias_edad < 0:
                raise forms.ValidationError('La fecha de nacimiento es futura')
                
        return fecha_nac
    
    def calcular_edad(self, fecha_nacimiento):
        """Calcula la edad exacta en años a partir de la fecha de nacimiento"""
        hoy = date.today()
        # Restamos un año si todavía no ha llegado el cumpleaños de este año
        return hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
        

class BusquedaPacienteForm(forms.Form):
    busqueda = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Buscar por nombre, RUT o sala/cama'}))

class DispositivoForm(forms.ModelForm):
    class Meta:
        model = Dispositivo
        fields = [
            'categoria', 'tipo_sonda', 'tipo_via_aerea', 'tipo_vvp', 'tipo_drenaje',
            'fecha_instalacion', 'dias_instalacion', 'ubicacion'
        ]
        widgets = {
            'fecha_instalacion': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("Inicializando DispositivoForm")
        
        # Garantizar valores iniciales para todos los campos de tipo
        initial_data = kwargs.get('initial', {})
        data = {}
        
        if args and args[0]:
            print(f"Datos POST recibidos: {args[0]}")
            data = args[0]
        elif 'data' in kwargs:
            data = kwargs['data']
            
        categoria = data.get('categoria') if data else initial_data.get('categoria')
        print(f"Categoría detectada: {categoria}")
        
        # Asegurar que los campos de tipo tengan valores predeterminados
        if categoria == 'SONDA' and not data.get('tipo_sonda'):
            self.initial['tipo_sonda'] = initial_data.get('tipo_sonda', 'FOLEY_FR_16')
            print(f"Valor inicial para tipo_sonda: {self.initial.get('tipo_sonda')}")
            
        elif categoria == 'VIA_AEREA' and not data.get('tipo_via_aerea'):
            self.initial['tipo_via_aerea'] = initial_data.get('tipo_via_aerea', 'CANULA_MAYO')
            print(f"Valor inicial para tipo_via_aerea: {self.initial.get('tipo_via_aerea')}")
            
        elif categoria == 'VVP' and not data.get('tipo_vvp'):
            self.initial['tipo_vvp'] = initial_data.get('tipo_vvp', 'BRANULA_18G')
            print(f"Valor inicial para tipo_vvp: {self.initial.get('tipo_vvp')}")
            
        elif categoria == 'DRENAJE' and not data.get('tipo_drenaje'):
            self.initial['tipo_drenaje'] = initial_data.get('tipo_drenaje', 'TORACICO')
            print(f"Valor inicial para tipo_drenaje: {self.initial.get('tipo_drenaje')}")
            
        # Asegurar que fecha_instalacion tenga un valor predeterminado
        if not data.get('fecha_instalacion'):
            self.initial['fecha_instalacion'] = initial_data.get('fecha_instalacion', date.today())
            print(f"Valor inicial para fecha_instalacion: {self.initial.get('fecha_instalacion')}")
        
        # Establecer los campos requeridos basado en la categoría
        for field_name in self.fields:
            # Por defecto, solo categoría y fecha_instalacion son requeridos siempre
            if field_name in ['categoria', 'fecha_instalacion', 'dias_instalacion']:
                self.fields[field_name].required = True
            else:
                self.fields[field_name].required = False
                
        # Personalizar requisitos según la categoría
        if categoria:
            if categoria == 'SONDA':
                self.fields['tipo_sonda'].required = True
            elif categoria == 'VIA_AEREA':
                self.fields['tipo_via_aerea'].required = True
            elif categoria == 'VVP':
                self.fields['tipo_vvp'].required = True
            elif categoria == 'DRENAJE':
                self.fields['tipo_drenaje'].required = True
        
        # Establecer mensajes de error personalizados
        self.fields['tipo_sonda'].error_messages = {'required': 'Debe seleccionar un tipo de sonda.'}
        self.fields['tipo_via_aerea'].error_messages = {'required': 'Debe seleccionar un tipo de vía aérea.'}
        self.fields['tipo_vvp'].error_messages = {'required': 'Debe seleccionar un tipo de VVP.'}
        self.fields['tipo_drenaje'].error_messages = {'required': 'Debe seleccionar un tipo de drenaje.'}
        
        print(f"Valores iniciales establecidos: {self.initial}")
        
    def clean_dias_instalacion(self):
        dias = self.cleaned_data.get('dias_instalacion')
        if dias is not None and dias < 1:
            raise forms.ValidationError('Los días de instalación deben ser al menos 1.')
        elif dias is not None and dias > 30:
            raise forms.ValidationError('Los días de instalación no pueden exceder los 30 días.')
        return dias
        
    def clean_fecha_instalacion(self):
        from datetime import date, timedelta
        fecha = self.cleaned_data.get('fecha_instalacion')
        hoy = date.today()
        
        # Verificar que la fecha no sea en el futuro
        if fecha and fecha > hoy:
            raise forms.ValidationError('La fecha de instalación no puede ser en el futuro.')
        
        # Verificar que la fecha no sea muy antigua (más de 15 días atrás)
        limite_pasado = hoy - timedelta(days=15)
        if fecha and fecha < limite_pasado:
            raise forms.ValidationError('La fecha de instalación no puede ser anterior a 15 días desde hoy.')
        
        # Si la validación es exitosa, devolver la fecha
        return fecha
        
    def clean(self):
        cleaned_data = super().clean()
        categoria = cleaned_data.get('categoria')
        
        # Log para depuración
        print(f"Validando formulario - Categoría: {categoria}")
        
        # Validación específica según la categoría seleccionada
        if categoria == 'SONDA':
            tipo_sonda = cleaned_data.get('tipo_sonda')
            print(f"Tipo de sonda en clean(): {tipo_sonda}")
            if not tipo_sonda:
                self.add_error('tipo_sonda', 'Debe seleccionar un tipo de sonda.')
                
        elif categoria == 'VIA_AEREA':
            tipo_via_aerea = cleaned_data.get('tipo_via_aerea')
            print(f"Tipo de vía aérea en clean(): {tipo_via_aerea}")
            if not tipo_via_aerea:
                self.add_error('tipo_via_aerea', 'Debe seleccionar un tipo de vía aérea.')
                
        elif categoria == 'VVP':
            tipo_vvp = cleaned_data.get('tipo_vvp')
            print(f"Tipo de VVP en clean(): {tipo_vvp}")
            if not tipo_vvp:
                self.add_error('tipo_vvp', 'Debe seleccionar un tipo de VVP.')
                
        elif categoria == 'DRENAJE':
            tipo_drenaje = cleaned_data.get('tipo_drenaje')
            print(f"Tipo de drenaje en clean(): {tipo_drenaje}")
            if not tipo_drenaje:
                self.add_error('tipo_drenaje', 'Debe seleccionar un tipo de drenaje.')
                
        return cleaned_data 

class DarDeAltaForm(forms.Form):
    motivo_alta = forms.CharField(
        max_length=100, 
        required=False, 
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Motivo del alta (opcional)'
        })
    )
    
    def dar_de_alta(self, paciente):
        """Aplica el alta al paciente"""
        motivo = self.cleaned_data.get('motivo_alta')
        paciente.dar_de_alta(motivo)
        return paciente 