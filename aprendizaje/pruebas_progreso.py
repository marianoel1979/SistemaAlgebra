from usuarios.models import Usuario

from aprendizaje.models import Tema, Progreso


def probar_progreso():
    alumno=Usuario.objects.get(username="alumno1")
    primer_tema = Tema.objects.get(nivel__numero=1, numero=1)

    print("Estudiante: ",alumno)
    print("Primer tema: ",primer_tema)
    print("Nivel",primer_tema.nivel)

