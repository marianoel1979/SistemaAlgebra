from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, SetPasswordForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from .models import Grupo

Usuario = get_user_model()


def validar_clave(clave):
    if len(clave) < 8 or not any(c.isupper() for c in clave) or not any(c.islower() for c in clave) or not any(c.isdigit() for c in clave):
        raise ValidationError('Usá al menos 8 caracteres, una mayúscula, una minúscula y un número.')
    validate_password(clave)


class AccesoForm(AuthenticationForm):
    username = forms.CharField(label='Nombre de usuario', widget=forms.TextInput(attrs={'autocomplete': 'username'}))
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'}))


class RegistroEstudianteForm(forms.Form):
    nombre = forms.CharField(max_length=150)
    apellido = forms.CharField(max_length=150)
    codigo_grupo = forms.CharField(max_length=40, label='Código del grupo')
    username = forms.CharField(max_length=150, label='Nombre de usuario')
    email = forms.EmailField(required=False, label='Correo electrónico (opcional)')
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}))
    password2 = forms.CharField(label='Repetir contraseña', widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}))

    def clean_username(self):
        nombre = self.cleaned_data['username'].strip()
        if Usuario.objects.filter(username__iexact=nombre).exists():
            raise ValidationError('Ese nombre de usuario ya está en uso.')
        return nombre

    def clean_codigo_grupo(self):
        codigo = self.cleaned_data['codigo_grupo'].strip()
        grupo = Grupo.objects.filter(codigo=codigo, activo=True).first()
        if grupo is None:
            raise ValidationError('El código no corresponde a un grupo activo.')
        self.grupo = grupo
        return codigo

    def clean(self):
        datos = super().clean()
        clave = datos.get('password1')
        if clave:
            try:
                validar_clave(clave)
            except ValidationError as exc:
                self.add_error('password1', exc)
        if clave and datos.get('password2') and clave != datos['password2']:
            self.add_error('password2', 'Las contraseñas no coinciden.')
        return datos

    @transaction.atomic
    def save(self):
        if not self.is_valid():
            raise ValueError('El formulario debe validarse antes de guardar.')
        d = self.cleaned_data
        usuario = Usuario.objects.create_user(
            username=d['username'], password=d['password1'],
            first_name=d['nombre'], last_name=d['apellido'], email=d['email'],
            tipo_usuario='ESTUDIANTE', grupo=self.grupo,
        )
        return usuario


class CambioClaveForm(PasswordChangeForm):
    def clean_new_password1(self):
        clave = self.cleaned_data.get('new_password1')
        validar_clave(clave)
        return clave


class RecuperacionClaveForm(SetPasswordForm):
    def clean_new_password1(self):
        clave = self.cleaned_data.get("new_password1")
        validar_clave(clave)
        return clave
