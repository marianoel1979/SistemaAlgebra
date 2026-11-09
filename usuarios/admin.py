from django.contrib import admin
from .models import Usuario
from django.contrib.auth.admin import UserAdmin

# Register your models here.


class UsuarioAdmin(UserAdmin):

    new_add_fielset=("Datos del sistema",{"fields":("tipo_usuario","grupo")})
    add_fieldsets = UserAdmin.add_fieldsets + (new_add_fielset,)
    new_fieldset=("Datos del sistema",{"fields":("tipo_usuario","grupo")})
    fieldsets = UserAdmin.fieldsets + (new_fieldset,)
admin.site.register(Usuario,UsuarioAdmin)