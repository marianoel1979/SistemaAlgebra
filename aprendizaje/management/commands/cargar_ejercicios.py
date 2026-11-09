from django.core.management.base import BaseCommand
#BaseComand es una clase de Django para crear comandos personalizados
from aprendizaje.models import Tema,Ejercicio,PasoEjercicioBase

class Command(BaseCommand):
    help = "Carga los ejercicios base del sistema educativo"
    #help es una descripcion que nos va a mostrar cuando solicitemos ayuda sobre el comando

    def handle(self,*arg,**options):
        tema=Tema.objects.get(nivel__numero=1,numero=1)
        self.stdout.write(f"Tema encontrado: {tema}")
        ejercicios = [
            {
                "expresion": "4 + 3",
                "resultado": "7",
                "dificultad": 1,
            },
            {
                "expresion": "12 + 5",
                "resultado": "17",
                "dificultad": 1,
            },
            {
                "expresion": "23 + 14",
                "resultado": "37",
                "dificultad": 1,
            },
            {
                "expresion": "48 + 27",
                "resultado": "75",
                "dificultad": 2,
            },
            {
                "expresion": "136 + 58",
                "resultado": "194",
                "dificultad": 2,
            },
            {
                "expresion": "278 + 156",
                "resultado": "434",
                "dificultad": 2,
            },
            {
                "expresion": "487 + 365 + 128",
                "resultado": "980",
                "dificultad": 3,
            },
            {
                "expresion": "1758 + 2486",
                "resultado": "4244",
                "dificultad": 3,
            },
            {
                "expresion": "3679 + 2845 + 1176",
                "resultado": "7700",
                "dificultad": 3,
            },
        ]

        for dato in ejercicios:

            ejercicio, creado=Ejercicio.objects.get_or_create(
                tema=tema,
                expresion_inicial=dato["expresion"],
                defaults={
                    "enunciado": f"Resolvé la siguiente suma: {dato["expresion"]}",
                    "resultado_correcto":dato["resultado"] ,
                    "dificultad": dato["dificultad"],
                    "activo": True,
                }
            )
            if creado:
                self.stdout.write(f"Ejercicio creado: {ejercicio}")
            else:
                self.stdout.write(f"El ejercicio ya existía: {ejercicio}")

        ejercicio_suma= Ejercicio.objects.get(tema=tema,expresion_inicial="1758 + 2486")
        pasos=[
            (1,"Primer sumando","1758"),
            (2,"Segundo sumando","2786"),
            (3,"Llevadas","111-"),
            (4,"Resultado","4244"),
        ]

        for numero,tipo,expresion in pasos:
            paso,creado=PasoEjercicioBase.objects.get_or_create(
                ejercicio=ejercicio_suma,
                numero_paso=numero,
                defaults={
                    "tipo_operacion":tipo,
                    "expresion_esperada":expresion,
                }
            )
            if creado:
                self.stdout.write(f"Paso{numero} creado correctamente.")
            else:
                self.stdout.write((f"El paso {numero} ya existia."))