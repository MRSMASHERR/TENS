from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from .models import Usuario, Curso, InvitacionCurso
import re
from datetime import date
from itertools import cycle
from django.core.validators import EmailValidator
from django.contrib import messages

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese su correo electrónico o RUT',
                'autocomplete': 'username'
            }
        ),
        label='Correo electrónico o RUT',
        error_messages={
            'required': 'Debe ingresar su correo electrónico o RUT'
        }
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese su contraseña',
                'autocomplete': 'current-password'
            }
        ),
        label='Contraseña',
        min_length=8,
        error_messages={
            'required': 'Debe ingresar su contraseña',
            'min_length': 'La contraseña debe tener al menos 8 caracteres'
        }
    )
    remember_me = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(
            attrs={
                'class': 'form-check-input'
            }
        )
    )

    error_messages = {
        'invalid_login': 'Por favor ingrese un correo electrónico/RUT y contraseña correctos.',
        'inactive': 'Esta cuenta está inactiva. Contacte a un administrador.',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password'].widget.attrs.update({'class': 'form-control'})

    def clean(self):
        identifier = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if not identifier or not password:
            return self.cleaned_data
        
        # Intentar identificar al usuario
        user = None
        username = None
        
        # Primero verificar si es un correo electrónico
        if '@' in identifier:
            try:
                user = Usuario.objects.get(email=identifier)
                username = user.username
            except Usuario.DoesNotExist:
                pass
                
        # Si no es un correo o no se encontró el usuario, verificar si es un RUT
        if not user:
            # Intentar validar y formatear el RUT
            rut_validado = validar_rut(identifier)
            if rut_validado:
                try:
                    user = Usuario.objects.get(rut=rut_validado)
                    username = user.username
                except Usuario.DoesNotExist:
                    pass
        
        # Si aún no encontramos el usuario, tal vez el identifier es el username directamente
        if not user:
            username = identifier
        
        # Autenticar con el username encontrado o el original
        self.user_cache = authenticate(
            self.request, username=username, password=password
        )
        
        # Si la autenticación falló, proporcionar un mensaje de error más específico
        if self.user_cache is None:
            raise forms.ValidationError(
                "Credenciales incorrectas. Verifique su correo electrónico/RUT y contraseña.",
                code='invalid_login',
            )
        
        # Verificar si la cuenta está activa
        if not self.user_cache.is_active:
            raise forms.ValidationError(
                self.error_messages['inactive'],
                code='inactive',
            )
        
        return self.cleaned_data

class RegistroUsuarioForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario'}),
        min_length=4,
        max_length=150,
        error_messages={
            'required': 'El nombre de usuario es obligatorio',
            'min_length': 'El nombre de usuario debe tener al menos 4 caracteres',
            'max_length': 'El nombre de usuario no puede exceder los 150 caracteres'
        }
    )
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
        min_length=2,
        max_length=150,
        error_messages={
            'required': 'El nombre es obligatorio',
            'min_length': 'El nombre debe tener al menos 2 caracteres',
            'max_length': 'El nombre no puede exceder los 150 caracteres'
        }
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'}),
        min_length=2,
        max_length=150,
        error_messages={
            'required': 'El apellido es obligatorio',
            'min_length': 'El apellido debe tener al menos 2 caracteres',
            'max_length': 'El apellido no puede exceder los 150 caracteres'
        }
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
        error_messages={
            'required': 'El correo electrónico es obligatorio',
            'invalid': 'Ingrese un correo electrónico válido'
        }
    )
    rut = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'RUT (sin puntos y con guión)'}),
        error_messages={
            'required': 'El RUT es obligatorio'
        }
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'}),
        min_length=8,
        error_messages={
            'required': 'La contraseña es obligatoria',
            'min_length': 'La contraseña debe tener al menos 8 caracteres'
        }
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmar contraseña'}),
        error_messages={
            'required': 'Debe confirmar la contraseña'
        }
    )
    rol = forms.ChoiceField(
        choices=Usuario.ROLES, 
        widget=forms.Select(attrs={'class': 'form-control'}),
        error_messages={
            'required': 'Debe seleccionar un rol'
        }
    )
    es_paciente = forms.BooleanField(
        required=False, 
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    class Meta:
        model = Usuario
        fields = ['username', 'first_name', 'last_name', 'email', 'rut', 'password1', 'password2', 'rol', 'es_paciente']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar mensajes de error de validación de contraseña
        self.fields['password1'].help_text = """
        <ul class="text-muted">
            <li>La contraseña debe tener al menos 8 caracteres</li>
            <li>No puede ser una contraseña común</li>
            <li>No puede ser completamente numérica</li>
            <li>No puede ser similar a su información personal</li>
        </ul>
        """
        self.fields['password2'].help_text = 'Ingrese la misma contraseña para verificación'

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden")
        return password2

    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")
        email = self.cleaned_data.get("email")
        
        if password1 and email:
            # Obtener el nombre de usuario del email (parte antes del @)
            email_username = email.split('@')[0].lower()
            
            # Verificar si la contraseña contiene el nombre de usuario del email
            if email_username in password1.lower():
                raise forms.ValidationError(
                    "La contraseña no puede contener su nombre de usuario del correo electrónico. "
                    "Por ejemplo, si su correo es 'usuario@inacap.cl', no puede usar 'usuario' en su contraseña."
                )
            
            # Verificar si la contraseña es demasiado similar al email completo
            if email.lower() in password1.lower():
                raise forms.ValidationError(
                    "La contraseña no puede contener su correo electrónico completo."
                )
        
        return password1

    def clean(self):
        cleaned_data = super().clean()
        print("Datos limpios del formulario:", cleaned_data)
        
        # Validar que los campos específicos del rol estén presentes
        rol = cleaned_data.get('rol')
        if rol == 'docente':
            if not cleaned_data.get('especialidad'):
                self.add_error('especialidad', 'La especialidad es requerida para docentes')
            if not cleaned_data.get('titulo_profesional'):
                self.add_error('titulo_profesional', 'El título profesional es requerido para docentes')
        elif rol == 'estudiante':
            if not cleaned_data.get('matricula'):
                self.add_error('matricula', 'La matrícula es requerida para estudiantes')
            if not cleaned_data.get('ano_ingreso'):
                self.add_error('ano_ingreso', 'El año de ingreso es requerido para estudiantes')
            if not cleaned_data.get('semestre_actual'):
                self.add_error('semestre_actual', 'El semestre actual es requerido para estudiantes')
        
        return cleaned_data
    
    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        if not rut:
            raise forms.ValidationError('El RUT es obligatorio')
        
        # Validar formato del RUT
        if not re.match(r'^\d{1,8}-[\dkK]$', rut):
            raise forms.ValidationError('El RUT debe tener el formato correcto (ejemplo: 12345678-9)')
        
        # Verificar si el RUT ya existe
        if Usuario.objects.filter(rut=rut).exists():
            raise forms.ValidationError('Este RUT ya está registrado')
        
        return rut
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError('El correo electrónico es obligatorio')
        
        # Verificar si el email ya existe
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError('Este correo electrónico ya está registrado')
        
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username:
            raise forms.ValidationError('El nombre de usuario es obligatorio')
        
        # Verificar si el username ya existe
        if Usuario.objects.filter(username=username).exists():
            raise forms.ValidationError('Este nombre de usuario ya está en uso')
        
        return username

class EditarUsuarioForm(forms.ModelForm):
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
        min_length=2,
        error_messages={
            'required': 'El nombre es obligatorio',
            'min_length': 'El nombre debe tener al menos 2 caracteres'
        }
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'}),
        min_length=2,
        error_messages={
            'required': 'El apellido es obligatorio',
            'min_length': 'El apellido debe tener al menos 2 caracteres'
        }
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
        error_messages={
            'required': 'El correo electrónico es obligatorio',
            'invalid': 'Ingrese un correo electrónico válido'
        }
    )
    rut = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'RUT (sin puntos y con guión)'}),
        error_messages={
            'required': 'El RUT es obligatorio'
        }
    )
    rol = forms.ChoiceField(
        choices=Usuario.ROLES, 
        widget=forms.Select(attrs={'class': 'form-control'}),
        error_messages={
            'required': 'Debe seleccionar un rol'
        }
    )
    activo = forms.BooleanField(
        required=False, 
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    es_paciente = forms.BooleanField(
        required=False, 
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    class Meta:
        model = Usuario
        fields = ['username', 'first_name', 'last_name', 'email', 'rut', 'rol', 'activo', 'es_paciente']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial_email = self.instance.email if self.instance and self.instance.pk else None
        self.initial_rut = self.instance.rut if self.instance and self.instance.pk else None
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and email != self.initial_email:
            if Usuario.objects.filter(email=email).exists():
                raise forms.ValidationError('Ya existe un usuario con este correo electrónico')
        return email
        
    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        if not rut:
            return rut
            
        rut_validado = validar_rut(rut)
        if not rut_validado:
            raise forms.ValidationError('RUT inválido. Por favor verifica el número y dígito verificador')
            
        # Comprobar si ya existe un usuario con ese RUT (distinto al usuario actual)
        if rut_validado != self.initial_rut and Usuario.objects.filter(rut=rut_validado).exists():
            raise forms.ValidationError('Ya existe un usuario con este RUT')
            
        return rut_validado

class EditarPerfilForm(forms.ModelForm):
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True,
        label='Nombre',
        error_messages={
            'required': 'El nombre es obligatorio',
        }
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True,
        label='Apellido',
        error_messages={
            'required': 'El apellido es obligatorio',
        }
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        required=True,
        label='Correo Electrónico',
        error_messages={
            'required': 'El correo electrónico es obligatorio',
            'invalid': 'Ingrese un correo electrónico válido'
        }
    )
    rut = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True,
        label='RUT',
        error_messages={
            'required': 'El RUT es obligatorio'
        }
    )
    
    # Campos para docentes
    especialidad = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False,
        label='Especialidad'
    )
    titulo_profesional = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False,
        label='Título Profesional'
    )
    anos_experiencia = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        required=False,
        min_value=0,
        initial=0,
        label='Años de Experiencia'
    )
    
    # Campos para estudiantes
    matricula = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False,
        label='Matrícula'
    )
    ano_ingreso = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        required=False,
        label='Año de Ingreso'
    )
    semestre_actual = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        required=False,
        label='Semestre Actual'
    )
    
    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'email', 'rut', 'especialidad', 'titulo_profesional', 
                 'anos_experiencia', 'matricula', 'ano_ingreso', 'semestre_actual']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Establecer valores iniciales si no existen
        if self.instance:
            for field in self.fields:
                if getattr(self.instance, field) is None:
                    self.fields[field].initial = ''
            
            # Ocultar campos según el rol
            if self.instance.rol == 'docente':
                del self.fields['matricula']
                del self.fields['ano_ingreso']
                del self.fields['semestre_actual']
            elif self.instance.rol == 'estudiante':
                del self.fields['especialidad']
                del self.fields['titulo_profesional']
                del self.fields['anos_experiencia']
    
    def clean(self):
        cleaned_data = super().clean()
        # Asegurarse de que los campos tengan al menos un valor vacío en lugar de None
        for field in self.fields:
            if cleaned_data.get(field) is None:
                cleaned_data[field] = ''
        return cleaned_data

class CursoForm(forms.ModelForm):
    nombre = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: Enfermería Básica - Segundo Semestre 2025'
        }),
        label='Nombre del Curso',
        help_text='El nombre del curso debe ser descriptivo y único',
        error_messages={
            'required': 'El nombre del curso es obligatorio',
            'max_length': 'El nombre no puede exceder los 100 caracteres'
        }
    )
    
    descripcion = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Ej: Curso práctico de enfermería donde los estudiantes aprenderán técnicas básicas de atención al paciente'
        }),
        label='Descripción',
        help_text='Describe los objetivos y contenido del curso brevemente',
        required=False
    )
    
    codigo = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: ENF-2025-S2',
            'readonly': True
        }),
        label='Código del Curso',
        help_text='El código se generará automáticamente basado en el nombre del curso',
        required=False
    )
    
    generar_codigo_manual = forms.BooleanField(
        label='Generar código manualmente',
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'data-toggle': 'toggle-codigo-manual'
        })
    )
    
    class Meta:
        model = Curso
        fields = ['nombre', 'descripcion', 'codigo', 'generar_codigo_manual']
    
    def clean(self):
        cleaned_data = super().clean()
        nombre = cleaned_data.get('nombre')
        codigo = cleaned_data.get('codigo')
        generar_manual = cleaned_data.get('generar_codigo_manual')
        
        if nombre and not codigo and not generar_manual:
            # Generar código automáticamente a partir del nombre
            import re
            from datetime import datetime
            
            # Extraer iniciales de palabras significativas (evitando preposiciones)
            palabras = re.findall(r'\b[a-zA-Z0-9]\w+', nombre)
            iniciales = [p[0].upper() for p in palabras if len(p) > 2][:3]
            
            # Si no hay suficientes iniciales, usar las primeras 3 letras del nombre
            if len(iniciales) < 2:
                iniciales = [nombre[:3].upper()]
                
            # Añadir año actual y un número aleatorio para evitar duplicados
            año_actual = datetime.now().year
            import random
            num_aleatorio = random.randint(100, 999)
            
            # Formatear el código
            prefijo = ''.join(iniciales)
            codigo_generado = f"{prefijo}-{año_actual}-{num_aleatorio}"
            
            # Asignar al formulario
            cleaned_data['codigo'] = codigo_generado
        
        # Verificar si ya existe un curso con este código
        if codigo:
            from usuarios.models import Curso
            if Curso.objects.filter(codigo=codigo).exclude(id=self.instance.id if self.instance.id else None).exists():
                self.add_error('codigo', 'Ya existe un curso con este código. Utilice uno diferente o deje en blanco para generar automáticamente.')
            
            # Verificar formato (letras, números, guiones)
            import re
            if not re.match(r'^[A-Za-z0-9\-]+$', codigo):
                self.add_error('codigo', 'El código debe contener solo letras, números y guiones.')
        
        return cleaned_data

class InvitarEstudiantesForm(forms.Form):
    emails = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'placeholder': 'Ingrese las direcciones de correo electrónico separadas por comas o líneas nuevas', 
            'rows': 5
        }),
        label='Direcciones de correo electrónico',
        help_text='Puede ingresar múltiples correos separados por comas o en líneas diferentes'
    )
    
    def clean_emails(self):
        data = self.cleaned_data['emails']
        
        # Separar direcciones de correo (por comas o líneas nuevas)
        emails_raw = data.replace(',', '\n').split('\n')
        emails = []
        invalid_emails = []
        docentes_emails = []
        
        # Validar cada correo
        validator = EmailValidator(message='Dirección de correo inválida: %(value)s')
        for email in emails_raw:
            email = email.strip()
            if not email:  # Ignorar líneas vacías
                continue
                
            try:
                validator(email)
                # Verificar si el email pertenece a un docente
                usuario = Usuario.objects.filter(email=email).first()
                if usuario and usuario.rol == 'docente':
                    docentes_emails.append(email)
                    continue
                emails.append(email)
            except forms.ValidationError:
                invalid_emails.append(email)
        
        if docentes_emails:
            raise forms.ValidationError(
                'No se pueden invitar docentes al curso: %(value)s',
                params={'value': ', '.join(docentes_emails)}
            )
        
        if invalid_emails:
            raise forms.ValidationError(
                'Las siguientes direcciones de correo no son válidas: %(value)s',
                params={'value': ', '.join(invalid_emails)}
            )
        
        if not emails:
            raise forms.ValidationError('Debe ingresar al menos una dirección de correo válida')
        
        return emails

class InvitarEstudianteForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Ingrese el correo electrónico del estudiante'
        }),
        label='Correo electrónico',
        error_messages={
            'required': 'Debe ingresar un correo electrónico',
            'invalid': 'Ingrese un correo electrónico válido'
        }
    )
    
    def clean_email(self):
        email = self.cleaned_data['email']
        
        # Verificar si el email pertenece a un docente
        usuario = Usuario.objects.filter(email=email).first()
        if usuario and usuario.rol == 'docente':
            raise forms.ValidationError('No se pueden invitar docentes al curso')
            
        return email

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