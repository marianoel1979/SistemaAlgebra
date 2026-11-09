from .models import Progreso,Explicacion
from .generador_ejercicios import guardar_equivalencia_generada

def registrar_acierto_practica(progreso):
    if progreso.modo != Progreso.PRACTICA:
        return

    progreso.aciertos_dificultad+=1

    if progreso.aciertos_dificultad>=3:
        if progreso.dificultad_actual<3:
            progreso.dificultad_actual+=1
            progreso.aciertos_dificultad=0
        else:
            progreso.modo=Progreso.EVALUACION
            progreso.aciertos_dificultad=0

    progreso.save()

def activar_refuerzo(progreso,error):
    progreso.modo_anterior = progreso.modo
    progreso.modo=Progreso.REFUERZO
    progreso.error=error
    progreso.dificultad_refuerzo=1
    progreso.aciertos_refuerzo=0
    progreso.save()

def registrar_acierto_refuerzo(progreso):
    if progreso.modo != Progreso.REFUERZO:
        return

    progreso.aciertos_refuerzo+=1

    if progreso.aciertos_refuerzo>=2:
        if progreso.dificultad_refuerzo<3:
            progreso.dificultad_refuerzo+=1
            progreso.aciertos_refuerzo=0
        else:
            if progreso.modo_anterior==Progreso.PRACTICA:
                progreso.modo=Progreso.PRACTICA
                if progreso.dificultad_actual<3:
                    progreso.dificultad_actual+=1
                    progreso.aciertos_dificultad=0
                else:
                    progreso.modo=Progreso.EVALUACION
                    progreso.aciertos_dificultad=0
            elif progreso.modo_anterior==Progreso.EVALUACION:
                progreso.modo = Progreso.EVALUACION
                progreso.aciertos_evaluacion = 0

            progreso.error = None
            progreso.modo_anterior=None
            progreso.aciertos_refuerzo = 0
            progreso.dificultad_refuerzo = 1

    progreso.save()


def generar_refuerzo(progreso,ejercicio_base):
    if progreso.modo != Progreso.REFUERZO:
        return None
    if progreso.error is None:
        return None
    ejercicio_generado = guardar_equivalencia_generada(
        ejercicio_base=ejercicio_base,
        error=progreso.error,
        dificultad=progreso.dificultad_refuerzo
    )
    return ejercicio_generado

def obtener_explicacion_refuerzo(progreso):
    if progreso.modo != Progreso.REFUERZO:
        return None

    explicacion=Explicacion.objects.filter(
        tema=progreso.tema,
        error=progreso.error,
        activo=True
    ).first()
    return explicacion

def registrar_acierto_evaluacion(progreso):
    if progreso.modo != Progreso.EVALUACION:
        return

    progreso.aciertos_evaluacion += 1

    if progreso.aciertos_evaluacion >= 6:
        progreso.nivel_aprobado=True

        progreso.save()
        return True

    progreso.save()
    return False