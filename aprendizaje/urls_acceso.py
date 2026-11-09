from django.urls import path
from . import views_acceso as v

urlpatterns = [
    path('ingresar/', v.acceso, name='acceso_estudiante'),
    path('registrarse/', v.registro, name='registro_estudiante'),
    path('inicio/', v.inicio_estudiante, name='inicio_estudiante'),
    path('cambiar-clave/', v.cambiar_clave, name='cambiar_clave_estudiante'),
    path('salir/', v.salir, name='salir_estudiante'),
    path('recuperar/', v.RecuperarClave.as_view(), name='recuperar_clave_estudiante'),
    path('recuperar/enviado/', v.RecuperacionEnviada.as_view(), name='recuperacion_enviada'),
    path('recuperar/<uidb64>/<token>/', v.ConfirmarClave.as_view(), name='password_reset_confirm'),
    path('recuperar/completo/', v.RecuperacionCompleta.as_view(), name='recuperacion_completa'),
]
