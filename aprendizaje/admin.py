from django.contrib import admin
from .models import (Nivel,Tema,Ejercicio,PasoEjercicioBase,
                     Error,EjercicioGeneradoPorError,Resolucion,
                     PasoResolucion,Explicacion,Progreso,Grupo,PatronTermino,PasoPatron)


# Register your models here.

admin.site.register(Nivel)
admin.site.register(Tema)
admin.site.register(Ejercicio)
admin.site.register(PasoEjercicioBase)
admin.site.register(Error)
admin.site.register(EjercicioGeneradoPorError)
admin.site.register(Resolucion)
admin.site.register(PasoResolucion)
admin.site.register(Explicacion)
admin.site.register(Progreso)
admin.site.register(Grupo)
admin.site.register(PatronTermino)
admin.site.register(PasoPatron)