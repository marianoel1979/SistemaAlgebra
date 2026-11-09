from .control_adaptativo import (registrar_acierto_practica,
                                 activar_refuerzo,registrar_acierto_refuerzo,registrar_acierto_evaluacion)
from .models import PasoEjercicioBase,Resolucion,PasoResolucion,Error,Progreso,PasoPatron
from sympy import sympify,Rational,simplify
from .generador_ejercicios import reemplazar_variables,separar_terminos,buscar_patron,EjercicioGeneradoPorError,obtener_resoluciones_patron,traducir_resoluciones_patron
from sympy.core.sympify import SympifyError
def evaluar_suma_parada(ejercicio,respuesta):
    pasos_esperados=PasoEjercicioBase.objects.filter(ejercicio=ejercicio).order_by("numero_paso")

    paso_esperado={}

    for paso in pasos_esperados:
        paso_esperado[paso.numero_paso]=paso.expresion_esperada

    respuesta_alumno={}

    for numero,expresion in respuesta:
        respuesta_alumno[numero]=expresion

    for i in len(paso_esperado-1):
        if respuesta_alumno[i]==paso_esperado[i]:
            correcto=True
        else:
            correcto=False

def evaluar_equivalencia(respuesta,numerador_esperado,denominador_esperado):

    resultados_pasos={}

    resultados_pasos[1]=respuesta[1]==numerador_esperado
    resultados_pasos[2]=respuesta[2]==denominador_esperado
    ejercicio_correcto=all(resultados_pasos.values())
    return {
        "pasos":resultados_pasos,
        "correcto":ejercicio_correcto
    }
def registrar_resolucion_equivalencia(estudiante,  respuestas,
                                      resultado_evaluacion,ejercicio=None,
                                      ejercicio_refuerzo=None,ejercicio_practica=None):

    resolucion = Resolucion.objects.create(
        estudiante=estudiante,
        ejercicio=ejercicio,
        ejercicio_generado_xerror=ejercicio_refuerzo,
        ejercicio_generado_practica=ejercicio_practica,
        correcta=resultado_evaluacion["correcto"]
    )
    for numero_paso, expresion_ingresada in respuestas.items():
        correcto = resultado_evaluacion["pasos"][numero_paso]
        if correcto:
            error=None
        else:
            error=Error.objects.get(codigo="E002")
        paso_resolucion=PasoResolucion.objects.create(
            resolucion=resolucion,
            numero_paso=numero_paso,
            expresion_ingresada=expresion_ingresada,
            correcto=correcto,
            error=error
        )
    return resolucion

def continuar(resultado,progreso):

    if progreso.modo==Progreso.PRACTICA:

        if resultado["correcto"]:
            registrar_acierto_practica(progreso=progreso)
        else:
            error=Error.objects.get(codigo="E002")
            activar_refuerzo(progreso=progreso,error=error)

    elif progreso.modo==Progreso.REFUERZO:
        if resultado["correcto"]:
            registrar_acierto_refuerzo(progreso=progreso)

        else:
            progreso.aciertos_refuerzo = 0
            progreso.save()

    elif progreso.modo == Progreso.EVALUACION:
        if resultado["correcto"]:
            registrar_acierto_evaluacion(progreso)
        else:
            error = Error.objects.get(codigo="E002")
            progreso.aciertos_evaluacion = 0
            activar_refuerzo(progreso, error)

def procesar_respuesta_equivalencia(estudiante,ejercicio,respuesta,
                                    numerador_esperado,denominador_esperado,
                                    progreso,ejercicio_refuerzo=None,ejercicio_practica=None):

    resultado=evaluar_equivalencia(respuesta,numerador_esperado,denominador_esperado)
    if ejercicio_practica is not None:
        resolucion = registrar_resolucion_equivalencia(
            estudiante=estudiante,
            respuestas=respuesta,
            resultado_evaluacion=resultado,
            ejercicio_practica=ejercicio_practica
        )

    elif ejercicio_refuerzo is not None:
        resolucion = registrar_resolucion_equivalencia(
            estudiante=estudiante,
            respuestas=respuesta,
            resultado_evaluacion=resultado,
            ejercicio_refuerzo=ejercicio_refuerzo
        )

    else:
        resolucion = registrar_resolucion_equivalencia(
            estudiante=estudiante,
            respuestas=respuesta,
            resultado_evaluacion=resultado,
            ejercicio=ejercicio
        )
    continuar(resultado,progreso)
    if ejercicio_practica is not None:
        progreso.ejercicio_practica_actual = None
        progreso.save()
    if ejercicio_refuerzo is not None:
        progreso.ejercicio_refuerzo_actual=None
        progreso.save()
    respuesta_procesada_equivalencia={
        "resultado":resultado,
        "resolucion":resolucion,
    }
    return respuesta_procesada_equivalencia

def evaluar_resolucion_completa(ejercicio, valores, pasos_alumno, resultado_alumno):

    resultado_evaluacion = {
        "correcto": False,
        "error_detectado": None,
        "accion":"repetir",
        "regla_refuerzo": None
    }
    expresion = ejercicio.expresion_inicial

    # Convertimos los números generados a valores exactos.
    # Así evitamos errores de redondeo en las fracciones.
    valores_exactos = {
        letra: Rational(numero)
        for letra, numero in valores.items()
    }

    # Calculamos el resultado correcto del ejercicio.
    resultado_correcto = sympify(expresion,locals=valores_exactos)

    # Convertimos la respuesta del alumno a un valor matemático.
    resultado_ingresado = sympify(resultado_alumno)

    # Comparamos los resultados.
    if resultado_ingresado == resultado_correcto:

        # Si coincide, aprobamos sin revisar los pasos.
        resultado_evaluacion["correcto"] = True
        resultado_evaluacion["accion"]="continuar"
        return resultado_evaluacion

    # Si no coincide, por ahora devolvemos incorrecto.
    # Después incorporaremos la detección del primer error.
    expresion_numerica = reemplazar_variables(expresion, valores)
    primera_diferencia = localizar_primera_diferencia(
        expresion_numerica,
        pasos_alumno + [resultado_alumno]
    )
    if primera_diferencia is not None:
        posicion = identificar_termino_modificado(
            primera_diferencia["anterior"],
            primera_diferencia["actual"]
        )
        if posicion is not None:
            terminos = separar_terminos({"expresion": expresion})
            termino = terminos[posicion - 1]
            patron = buscar_patron(termino)
            if patron["patron"] is not None:
                reglas = obtener_reglas_patron(patron["patron"])
                primer_paso = reglas.filter(paso_anterior__isnull=True).order_by("id").first()

                errores = [
                    paso.error_asociado
                    for paso in reglas
                    if paso.error_asociado is not None
                ]

                if errores and all(error.pk == errores[0].pk for error in errores):
                    if primer_paso is not None and primer_paso.regla:
                        resultado_evaluacion["error_detectado"] = errores[0]
                        resultado_evaluacion["regla_refuerzo"] = primer_paso.regla
                        resultado_evaluacion["accion"] = "reforzar"
        resultado_evaluacion["termino_con_error"] = posicion

    # Guardamos la información para analizarla después.
    resultado_evaluacion["primera_diferencia"] = primera_diferencia

    return resultado_evaluacion

def evaluar_jerarquia(expresion, valores, pasos_alumno, resultado_alumno):
    """Evalúa procedimientos válidos respetando las rutas de PasoPatron."""

    respuesta = {
        "correcto": False,
        "error_detectado": None,
        "accion": "repetir"
    }

    def normalizar(texto):
        texto = "".join(str(texto).split())
        texto = texto.replace("×", "*").replace("÷", "/")
        texto = texto.replace("+-", "-")
        texto = texto.replace("--", "+")
        texto = texto.replace("-+", "-")
        texto = texto.replace("(-", "(") if False else texto
        return texto

    pasos = [normalizar(p) for p in pasos_alumno if p.strip()]

    if not pasos:
        respuesta["error_detectado"] = "Falta desarrollar el procedimiento"
        return respuesta

    datos = buscar_patron(expresion)
    patron = datos["patron"]

    if patron is None:
        respuesta["error_detectado"] = "Patrón no encontrado"
        return respuesta

    rutas = traducir_resoluciones_patron(
        obtener_resoluciones_patron(patron),
        datos["equivalencias"],
        valores
    )

    if not rutas:
        respuesta["error_detectado"] = "El patrón no tiene pasos configurados"
        return respuesta

    try:
        exactos = {
            letra: Rational(numero)
            for letra, numero in valores.items()
        }

        resultado_correcto = sympify(expresion, locals=exactos)
        resultado_ingresado = sympify(normalizar(resultado_alumno))

        resultado_ok = simplify(
            resultado_ingresado - resultado_correcto
        ) == 0

    except (ValueError, TypeError, SyntaxError, SympifyError):
        respuesta["error_detectado"] = "Resultado con formato inválido"
        return respuesta

    def comparar_ruta(ruta):
        esperados = [normalizar(n["expresion"]) for n in ruta]

        # El resultado final puede estar también entre los pasos.
        ingresados = pasos[:]
        if ingresados and ingresados[-1] == esperados[-1]:
            ingresados.pop()

        # Exigimos al menos un paso intermedio.
        if not ingresados:
            return False

        posicion = 0

        # Los pasos escritos deben aparecer en orden
        # dentro de una misma ruta válida.
        for paso in ingresados:
            encontrado = False

            while posicion < len(esperados) - 1:
                if paso == esperados[posicion]:
                    encontrado = True
                    posicion += 1
                    break

                posicion += 1

            if not encontrado:
                return False

        return True

    if resultado_ok and any(comparar_ruta(ruta) for ruta in rutas):
        respuesta["correcto"] = True
        respuesta["accion"] = "continuar"
        return respuesta

    # Identificamos el primer paso que no coincide
    # con ninguna continuación de una ruta válida.D
    def coincidencias(ruta):
        esperados = [normalizar(n["expresion"]) for n in ruta[:-1]]
        posicion = 0
        cantidad = 0

        for paso in pasos:
            while posicion < len(esperados) and esperados[posicion] != paso:
                posicion += 1

            if posicion == len(esperados):
                break

            cantidad += 1
            posicion += 1

        return cantidad

    mejor_ruta = max(rutas, key=coincidencias)
    cantidad = coincidencias(mejor_ruta)
    if cantidad < len(pasos):
        expresion_anterior = (
            pasos[cantidad - 1]
            if cantidad > 0
            else reemplazar_variables(expresion, {
                letra: Rational(numero)
                for letra, numero in valores.items()
            })
        )

        error_calculo = clasificar_error_paso(
            expresion_anterior,
            pasos[cantidad]
        )

        if error_calculo == "ERROR_CALCULO":
            respuesta["error_detectado"] = "ERROR_CALCULO"
            respuesta["accion"] = "repetir"
            return respuesta

    if not resultado_ok and cantidad == len(pasos):
        respuesta["error_detectado"] = "Resultado final incorrecto"
        return respuesta
    # Verificamos si el alumno omitió una multiplicación pendiente.
    # La clasificación del error se implementará aquí.
    indice = min(cantidad, len(mejor_ruta) - 2)
    codigo_id = mejor_ruta[indice].get("error_asociado")

    if codigo_id is not None:
        error = Error.objects.filter(pk=codigo_id).first()

        if error is not None:
            respuesta["error_detectado"] = error.codigo
            respuesta["accion"] = "reforzar"
            return respuesta

    respuesta["error_detectado"] = "Procedimiento incorrecto o incompleto"
    return respuesta


def obtener_reglas_patron(patron):
    return PasoPatron.objects.filter(
        patron=patron
    ).select_related("error_asociado")

def analizar_pasos_alumno(pasos_alumno):

    pasos_analizados = []

    for numero, expresion in enumerate(pasos_alumno, start=1):

        pasos_analizados.append({
            "numero": numero,
            "expresion": expresion.strip()
        })

    return pasos_analizados

def comparar_pasos(expresion_anterior, expresion_actual):

    # Calculamos la diferencia entre ambas expresiones.
    diferencia = simplify(
        sympify(expresion_anterior) - sympify(expresion_actual)
    )

    # Si la diferencia es cero, son equivalentes.
    return diferencia == 0

def localizar_primera_diferencia(expresion_inicial, pasos_alumno):

    # Comenzamos con la expresión original del ejercicio.
    anterior = expresion_inicial

    # Recorremos los pasos del alumno en orden.
    for paso in analizar_pasos_alumno(pasos_alumno):

        actual = paso["expresion"]
        print("PASO ANTERIOR:", anterior)
        print("PASO ACTUAL:", actual)

        # Comparamos el paso actual con el anterior.
        if not comparar_pasos(anterior, actual):
            return {
                "numero": paso["numero"],
                "anterior": anterior,
                "actual": actual
            }

        # Si es equivalente, avanzamos al siguiente paso.
        anterior = actual

    # No encontramos diferencias matemáticas.
    return None

def identificar_termino_modificado(anterior, actual):
    terminos_anteriores = separar_terminos({"expresion": anterior})
    terminos_actuales = separar_terminos({"expresion": actual})

    if len(terminos_anteriores) != len(terminos_actuales):
        return None

    for posicion, (antes, despues) in enumerate(
        zip(terminos_anteriores, terminos_actuales), start=1
    ):
        if antes != despues:
            if not comparar_pasos(antes, despues):
                return posicion

    return None

def clasificar_error_paso(expresion_anterior, expresion_alumno):
    """
    Distingue errores de cálculo dentro de un término
    de transformaciones que alteran la jerarquía.
    """
    anterior = expresion_anterior.replace(" ", "").replace("×", "*").replace("÷", "/")
    alumno = expresion_alumno.replace(" ", "").replace("×", "*").replace("÷", "/")

    if anterior == alumno:
        return None

    terminos_originales = separar_terminos({"expresion": anterior})
    terminos_alumno = separar_terminos({"expresion": alumno})

    if len(terminos_originales) != len(terminos_alumno):
        return "NO_CLASIFICADO"

    modificados = [
        (original, actual)
        for original, actual in zip(terminos_originales, terminos_alumno)
        if original != actual
    ]

    if len(modificados) != 1:
        return "NO_CLASIFICADO"

    original, actual = modificados[0]

    try:
        valor_original = sympify(original)
        valor_alumno = sympify(actual)

        if simplify(valor_original - valor_alumno) != 0:
            return "ERROR_CALCULO"

    except (ValueError, TypeError, SyntaxError, SympifyError):
        return "NO_CLASIFICADO"

    return "NO_CLASIFICADO"


