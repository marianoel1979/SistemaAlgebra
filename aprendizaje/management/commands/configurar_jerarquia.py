"""Carga los patrones de jerarquía de las dificultades 1, 2 y 3."""
from django.core.management.base import BaseCommand
from django.db import transaction
from aprendizaje.models import Error, PatronTermino, PasoPatron


class Command(BaseCommand):
    help = "Configura las rutas de los tres patrones de jerarquía"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        error, _ = Error.objects.get_or_create(
            codigo="E008",
            defaults={"nombre": "Jerarquía de operaciones", "descripcion": "No respeta el orden de prioridad de las operaciones matemáticas."},
        )
        # Cada lista representa una ruta válida; las ramas comparten el patrón.
        definiciones = {
            "a+b*c": [
                [("a+r", "b*c", None, None, None, "Multiplicar primero", "resolver_multiplicacion", error),
                 ("s", None, "a+r", None, None, "Resolver la suma", "resolver_suma", None)]
            ],
            "a+b*c-d": [
                [("a+r-d", "b*c", None, None, None, "Multiplicar primero", "resolver_multiplicacion", error),
                 ("s-d", None, "a+r", None, None, "Resolver la suma", "resolver_suma", None),
                 ("t", None, None, "s-d", None, "Resolver la resta", "resolver_resta", None)]
            ],
            "a+b*c-d*e": [
                [("a+r-d*e", "b*c", None, None, None, "Multiplicar el primer producto", "resolver_multiplicacion", error),
                 ("a+r-s", None, "d*e", None, None, "Multiplicar el segundo producto", "resolver_multiplicacion", error),
                 ("t-s", None, None, "a+r", None, "Resolver la suma", "resolver_suma", None),
                 ("u", None, None, None, "t-s", "Resolver la resta", "resolver_resta", None)],
                [("a+b*c-r", "d*e", None, None, None, "Multiplicar el segundo producto", "resolver_multiplicacion", error),
                 ("a+s-r", None, "b*c", None, None, "Multiplicar el primer producto", "resolver_multiplicacion", error),
                 ("t-r", None, None, "a+s", None, "Resolver la suma", "resolver_suma", None),
                 ("u", None, None, None, "t-r", "Resolver la resta", "resolver_resta", None)]
            ],
        }
        for plantilla, rutas in definiciones.items():
            patron, _ = PatronTermino.objects.get_or_create(
                patron=plantilla,
                defaults={"descripcion": f"Jerarquía: {plantilla}", "activo": True},
            )
            # Solo se reemplazan los pasos de estos tres patrones; no otros temas.
            PasoPatron.objects.filter(patron=patron).delete()
            for ruta in rutas:
                anterior = None
                for indice, (expresion, r, s, t, u, descripcion, regla, asociado) in enumerate(ruta):
                    anterior = PasoPatron.objects.create(
                        patron=patron, paso_anterior=anterior,
                        expresion=expresion, calculo_r=r, calculo_s=s,
                        calculo_t=t, calculo_u=u, descripcion=descripcion,
                        regla=regla, error_asociado=asociado,
                        es_final=(indice == len(ruta) - 1),
                    )
            self.stdout.write(self.style.SUCCESS(f"Configurado: {plantilla}"))
