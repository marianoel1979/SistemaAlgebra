from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from .forms_acceso import AccesoForm, RegistroEstudianteForm, CambioClaveForm, RecuperacionClaveForm
from .models import Progreso

def acceso(request):
    if request.user.is_authenticated and getattr(request.user, 'tipo_usuario', None) == 'ESTUDIANTE':
        return redirect('inicio_estudiante')
    form = AccesoForm(request, data=request.POST or None)
    intentos = request.session.get('intentos_acceso', 0)
    if request.method == 'POST':
        if form.is_valid():
            usuario = form.get_user()
            if getattr(usuario, 'tipo_usuario', None) != 'ESTUDIANTE':
                form.add_error(None, 'Este acceso es exclusivo para estudiantes.')
            else:
                login(request, usuario)
                request.session['intentos_acceso'] = 0
                request.session.set_expiry(600)
                return redirect('inicio_estudiante')
        intentos += 1
        request.session['intentos_acceso'] = intentos
    return render(request, 'aprendizaje/acceso/ingreso.html', {'form': form, 'mostrar_recuperacion': intentos >= 3})


def registro(request):
    if request.user.is_authenticated and getattr(request.user, 'tipo_usuario', None) == 'ESTUDIANTE':
        return redirect('inicio_estudiante')
    form = RegistroEstudianteForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        usuario = form.save()
        login(request, usuario)
        request.session.set_expiry(600)
        return redirect('inicio_estudiante')
    return render(request, 'aprendizaje/acceso/registro.html', {'form': form})


@login_required(login_url='acceso_estudiante')
def inicio_estudiante(request):
    if getattr(request.user, 'tipo_usuario', None) != 'ESTUDIANTE':
        return render(request, 'aprendizaje/acceso/sin_permiso.html', status=403)

    request.session.set_expiry(600)

    progreso = Progreso.objects.filter(
        estudiante=request.user
    ).select_related('tema', 'tema__nivel').first()

    return render(request, 'aprendizaje/acceso/inicio.html', {
        'progreso': progreso
    })


@login_required(login_url='acceso_estudiante')
def cambiar_clave(request):
    form = CambioClaveForm(request.user, request.POST or None)
    if request.method == 'POST' and form.is_valid():
        usuario = form.save()
        update_session_auth_hash(request, usuario)
        request.session.set_expiry(600)
        messages.success(request, 'Contraseña actualizada.')
        return redirect('inicio_estudiante')
    return render(request, 'aprendizaje/acceso/cambiar_clave.html', {'form': form})


@require_POST
def salir(request):
    logout(request)
    return redirect('acceso_estudiante')


class RecuperarClave(PasswordResetView):
    template_name = 'aprendizaje/acceso/recuperar.html'
    email_template_name = 'aprendizaje/acceso/correo_recuperacion.txt'
    subject_template_name = 'aprendizaje/acceso/asunto_recuperacion.txt'
    success_url = reverse_lazy('recuperacion_enviada')


class RecuperacionEnviada(PasswordResetDoneView):
    template_name = 'aprendizaje/acceso/recuperacion_enviada.html'


class ConfirmarClave(PasswordResetConfirmView):
    form_class = RecuperacionClaveForm
    template_name = 'aprendizaje/acceso/confirmar_clave.html'
    success_url = reverse_lazy('recuperacion_completa')


class RecuperacionCompleta(PasswordResetCompleteView):
    template_name = 'aprendizaje/acceso/recuperacion_completa.html'
