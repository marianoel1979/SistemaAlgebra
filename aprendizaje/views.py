from django.shortcuts import render
from .models import Ejercicio,Progreso,Tema
from .evaluador import procesar_respuesta_equivalencia,evaluar_resolucion_completa,evaluar_jerarquia
from django.contrib.auth import get_user_model
from .control_adaptativo import obtener_explicacion_refuerzo,generar_refuerzo
from.generador_ejercicios import guardar_equivalencia_practica,generar_ejercicio_combinado
from django.shortcuts import redirect
from .generador_ejercicios import generar_refuerzo as generar_refuerzo_dinamico
from sympy import sympify, simplify

# Create your views here.
def resolver_ejercicio(request):

    estudiante=get_user_model().objects.get(username="alumno1")
    tema = Tema.objects.get(nivel__numero=3, numero=1)
    progreso, creado = Progreso.objects.get_or_create(
        estudiante=estudiante,
        tema=tema
    )
    ejercicio_practica=None
    ejercicio = Ejercicio.objects.filter(tema=progreso.tema,dificultad=progreso.dificultad_actual,activo=True).first()
    if not progreso.nivel_aprobado and progreso.modo in (Progreso.PRACTICA, Progreso.EVALUACION):
        if progreso.ejercicio_practica_actual:
            ejercicio_practica = progreso.ejercicio_practica_actual
        elif ejercicio is not None:
            ejercicio_practica = guardar_equivalencia_practica(ejercicio,progreso)
            progreso.ejercicio_practica_actual = ejercicio_practica
            progreso.save()
    resultado = None
    mostrar_explicacion=None
    ejercicio_refuerzo=None
    if request.method == "POST":
        numerador = int(request.POST.get("numerador"))
        denominador = int(request.POST.get("denominador"))
        respuestas={
            1:numerador,
            2:denominador
        }
        if progreso.modo==Progreso.REFUERZO:
            ejercicio_refuerzo=progreso.ejercicio_refuerzo_actual
            resultado_correcto_refuerzo = ejercicio_refuerzo.resultado_correcto
            resultado_correcto_refuerzo = resultado_correcto_refuerzo.split("/")
            numerador_esperado_refuerzo = int(resultado_correcto_refuerzo[0])
            denominador_esperado_refuerzo = int(resultado_correcto_refuerzo[1])
            datos = procesar_respuesta_equivalencia(
                estudiante, ejercicio, respuestas,
                numerador_esperado_refuerzo,
                denominador_esperado_refuerzo,
                progreso,
                ejercicio_refuerzo=ejercicio_refuerzo
            )
        else:
            partes = ejercicio_practica.resultado_correcto.split("/")
            numerador_esperado = int(partes[0])
            denominador_esperado = int(partes[1])
            datos=procesar_respuesta_equivalencia(estudiante,ejercicio,
                                                  respuestas,numerador_esperado,denominador_esperado,
                                                  progreso,ejercicio_practica=ejercicio_practica)
        resultado=datos["resultado"]
        if not progreso.nivel_aprobado and progreso.modo in (Progreso.PRACTICA, Progreso.EVALUACION):
            ejercicio = Ejercicio.objects.filter(
                tema=progreso.tema,
                dificultad=progreso.dificultad_actual,
                activo=True
            ).first()
            ejercicio_practica = guardar_equivalencia_practica(ejercicio,progreso)
            progreso.ejercicio_practica_actual = ejercicio_practica
            progreso.save()
    if progreso.modo==Progreso.REFUERZO:
        mostrar_explicacion = obtener_explicacion_refuerzo(progreso)
        if progreso.ejercicio_refuerzo_actual:
            ejercicio_refuerzo=progreso.ejercicio_refuerzo_actual
        else:
            ejercicio_refuerzo=generar_refuerzo(progreso,ejercicio_base=ejercicio)
            progreso.ejercicio_refuerzo_actual=ejercicio_refuerzo
            progreso.save()
        return render(request, "aprendizaje/resolver_refuerzo.html", {
            "ejercicio": ejercicio,
            "resultado": resultado,
            "explicacion": mostrar_explicacion,
            "refuerzo": ejercicio_refuerzo,
        })
    return render(request, "aprendizaje/resolver_ejercicio.html", {
        "ejercicio": ejercicio,
        "resultado": resultado,
        "explicacion":mostrar_explicacion,
        "refuerzo":ejercicio_refuerzo,
        "ejercicio_practica": ejercicio_practica,
        "progreso":progreso,
    })

def resolver_operacion_combinada(request):
    estudiante = get_user_model().objects.get(username="alumno1")

    tema = Tema.objects.get(
        nivel__numero=5,
        numero=6
    )

    progreso, creado = Progreso.objects.get_or_create(
        estudiante=estudiante,
        tema=tema
    )
    mostrar_resultado_refuerzo = False
    evaluacion = None
    refuerzo_correcto = None
    refuerzo = None
    if progreso.modo == Progreso.EVALUACION:
        dificultad = 3
    else:
        dificultad = progreso.dificultad_actual
    if progreso.tema_aprobado:
        return render(request, "aprendizaje/resultado_examen.html", {
            "resultado": request.session.get("resultado_examen")
        })
    ejercicio = Ejercicio.objects.filter(
        tema__nivel__numero=5,
        tema__numero=6,
        dificultad=dificultad,
        activo=True,
        regla_refuerzo=""
    ).order_by("?").first()

    if ejercicio is None:
        return render(request, "aprendizaje/sin_ejercicios.html")

    if request.method == "GET":

        datos = generar_ejercicio_combinado(
            ejercicio.expresion_inicial,
            dificultad
        )

        expresion_numerica = datos["expresion"]

        request.session["ejercicio_combinado"] = {
            "ejercicio_id": ejercicio.id,
            "valores": {
                letra: numero
                for letra, numero in datos.items()
                if letra != "expresion"
            },
            "expresion": expresion_numerica
        }

    else:
        tipo_respuesta = request.POST.get("tipo_respuesta", "principal")
        datos_guardados = request.session.get("ejercicio_combinado")

        if datos_guardados is None:
            return redirect(request.path)
        ejercicio = Ejercicio.objects.get(
            id=datos_guardados["ejercicio_id"]
        )


        expresion_numerica = datos_guardados["expresion"]
        if tipo_respuesta == "refuerzo":
            refuerzo_guardado = request.session.get("refuerzo_actual")

            if refuerzo_guardado is None:

                return redirect(request.path)
            refuerzo = {
                "plantilla": Ejercicio.objects.get(
                    id=refuerzo_guardado["ejercicio_id"]
                ),
                "expresion": refuerzo_guardado["expresion"]
            }
            respuesta_refuerzo = request.POST.get(
                "resultado_refuerzo", ""
            ).strip()
            try:
                respuesta = sympify(respuesta_refuerzo)
                esperado = sympify(refuerzo_guardado["resultado_correcto"])

                refuerzo_correcto = simplify(respuesta - esperado) == 0
                print("Respuesta alumno:", respuesta)
                print("Resultado esperado:", esperado)
                print("Comparación:", refuerzo_correcto)

            except (ValueError, TypeError, SyntaxError):
                refuerzo_correcto = False
            mostrar_resultado_refuerzo = True
            if refuerzo_correcto:
                request.session["refuerzos_correctos"] = (
                        request.session.get("refuerzos_correctos", 0) + 1
                )
                request.session.pop("refuerzo_actual", None)
                if request.session["refuerzos_correctos"] < 6:
                    regla = refuerzo["plantilla"].regla_refuerzo

                    aciertos = request.session["refuerzos_correctos"]
                    dificultad = (aciertos // 2) + 1

                    refuerzo = generar_refuerzo_dinamico(regla, dificultad)

                    if refuerzo is not None:
                        request.session["refuerzo_actual"] = {
                            "ejercicio_id": refuerzo["plantilla"].id,
                            "expresion": refuerzo["expresion"],
                            "resultado_correcto": str(refuerzo["resultado_correcto"])
                        }
        else:
            texto_pasos = request.POST.get("pasos", "")
            resultado_alumno = request.POST.get("resultado", "").strip()

            pasos_alumno = [
                paso.strip()
                for paso in texto_pasos.splitlines()
                if paso.strip()
            ]
            evaluacion = evaluar_resolucion_completa(
                ejercicio,
                datos_guardados["valores"],
                pasos_alumno,
                resultado_alumno
            )
            print("DIAGNÓSTICO EVALUADOR:", evaluacion)
            refuerzo = None
            if progreso.modo == Progreso.EVALUACION:
                progreso.ejercicios_evaluacion_realizados += 1

                if evaluacion["accion"] == "continuar":
                    progreso.aciertos_evaluacion += 1

                progreso.save()
                if progreso.ejercicios_evaluacion_realizados == 4:
                    porcentaje = progreso.aciertos_evaluacion * 25
                    aprobado = progreso.aciertos_evaluacion >= 3
                    request.session["resultado_examen"] = {
                        "porcentaje": porcentaje,
                        "aciertos": progreso.aciertos_evaluacion,
                        "aprobado": aprobado
                    }
                    if aprobado:
                        progreso.tema_aprobado = True
                    else:
                        progreso.modo = Progreso.PRACTICA
                        progreso.dificultad_actual = 1
                        progreso.aciertos_dificultad = 0
                    progreso.aciertos_evaluacion = 0
                    progreso.ejercicios_evaluacion_realizados = 0
                    progreso.save()
                    request.session.pop("ejercicio_combinado", None)
                    return render(request, "aprendizaje/resultado_examen.html", {
                        "resultado": request.session["resultado_examen"]
                    })

                request.session.pop("ejercicio_combinado", None)
                return redirect(request.path)
            if evaluacion["accion"] == "continuar":
                request.session["intentos_sin_refuerzo"] = 0
                progreso.aciertos_dificultad += 1
                if progreso.aciertos_dificultad >= 3:
                    if progreso.dificultad_actual < 3:
                        progreso.dificultad_actual += 1
                        progreso.aciertos_dificultad = 0
                    else:
                        progreso.modo = Progreso.EVALUACION
                        progreso.aciertos_dificultad = 0
                progreso.save()
                request.session.pop("ejercicio_combinado", None)
                return redirect(request.path)

            elif evaluacion["accion"] == "repetir":
                request.session["intentos_sin_refuerzo"] = (
                        request.session.get("intentos_sin_refuerzo", 0) + 1
                )

                if request.session["intentos_sin_refuerzo"] >= 2:
                    request.session.pop("ejercicio_combinado", None)
                    request.session["intentos_sin_refuerzo"] = 0
                    return redirect(request.path)

            elif evaluacion["accion"] == "reforzar":
                request.session["intentos_sin_refuerzo"] = 0
                request.session["refuerzos_correctos"] = 0
                request.session.pop("refuerzo_actual", None)

                refuerzo = generar_refuerzo_dinamico(
                    evaluacion["regla_refuerzo"],
                    1
                )

                if refuerzo is not None:
                    request.session["refuerzo_actual"] = {
                        "ejercicio_id": refuerzo["plantilla"].id,
                        "expresion": refuerzo["expresion"],
                        "resultado_correcto": str(refuerzo["resultado_correcto"])
                    }


    return render(
        request,
        "aprendizaje/resolver_operacion_combinada.html",
        {
            "ejercicio": ejercicio,
            "modo": progreso.modo,
            "es_evaluacion": progreso.modo == Progreso.EVALUACION,
            "expresion_numerica": expresion_numerica,
            "evaluacion": evaluacion,
            "refuerzo": refuerzo,
            "refuerzo_correcto": refuerzo_correcto,
            "mostrar_resultado_refuerzo": mostrar_resultado_refuerzo,
            "hay_refuerzo_pendiente": "refuerzo_actual" in request.session,


        }
    )

def explicacion_jerarquia(request):
    return render (request,"aprendizaje/explicacion_jerarquia.html")

def practica_jerarquia(request, numero_tema=1):
    """Demo Tema 1: 3 aciertos por dificultad y refuerzo de 9 aciertos."""
    from secrets import token_urlsafe

    patrones = obtener_patrones_tema(numero_tema)
    clave = f"tema_{numero_tema}_demo"
    estado = request.session.get(clave)

    def ejercicio_nuevo(dificultad, anterior=None):
        plantilla = patrones[dificultad]
        datos = generar_ejercicio_combinado(plantilla, dificultad)
        for _ in range(12):
            if anterior is None or datos["expresion"] != anterior:
                break
            datos = generar_ejercicio_combinado(plantilla, dificultad)
        return datos

    if not estado or estado.get("version") != 2:
        medallas = estado.get("medallas", 0) if isinstance(estado, dict) else 0
        estado = {
            "version": 2, "modo": "practica", "dificultad": 1,
            "aciertos_practica": 0, "aciertos_refuerzo": 0,
            "medallas": medallas, "error": None,
            "ejercicio": ejercicio_nuevo(1), "token": token_urlsafe(16),
            "completado": False,
        }
        request.session[clave] = estado

    evaluacion = None
    if request.method == "POST" and not estado["completado"]:
        if request.POST.get("token_ejercicio") != estado["token"]:
            evaluacion = {"correcto": False, "error_detectado": "Este ejercicio ya fue enviado. Continuá con el siguiente.", "accion": "repetir"}
        else:
            datos = estado["ejercicio"]
            plantilla = patrones[estado["dificultad"]]
            valores = {letra: datos[letra] for letra in plantilla if letra.isalpha()}
            evaluacion = evaluar_jerarquia(
                plantilla, valores,
                request.POST.get("pasos", "").splitlines(),
                request.POST.get("resultado", ""),
            )
            if evaluacion["correcto"]:
                anterior = datos["expresion"]
                if estado["modo"] == "refuerzo":
                    estado["aciertos_refuerzo"] += 1
                    if estado["aciertos_refuerzo"] == 9:
                        estado["modo"] = "practica"
                        estado["dificultad"] = min(3, estado.pop("dificultad_previa", 1) + 1)
                        estado["aciertos_practica"] = 0
                        estado["error"] = None
                    else:
                        estado["dificultad"] = estado["aciertos_refuerzo"] // 3 + 1
                else:
                    estado["medallas"] += 1
                    estado["aciertos_practica"] += 1
                    if estado["aciertos_practica"] == 3:
                        if estado["dificultad"] == 3:
                            estado["completado"] = True
                        else:
                            estado["dificultad"] += 1
                            estado["aciertos_practica"] = 0
                if not estado["completado"]:
                    estado["ejercicio"] = ejercicio_nuevo(estado["dificultad"], anterior)
                estado["token"] = token_urlsafe(16)
            elif evaluacion["accion"] == "reforzar" and estado["modo"] == "practica":
                estado["dificultad_previa"] = estado["dificultad"]
                estado["modo"] = "refuerzo"
                estado["dificultad"] = 1
                estado["aciertos_refuerzo"] = 0
                estado["error"] = evaluacion["error_detectado"]
                estado["ejercicio"] = ejercicio_nuevo(1, datos["expresion"])
                estado["token"] = token_urlsafe(16)
            request.session[clave] = estado
            request.session.modified = True

    contexto = {
        "expresion_numerica": estado["ejercicio"]["expresion"].replace("*", " × "),
        "medallas": estado["medallas"], "evaluacion": evaluacion,
        "modo_refuerzo": estado["modo"] == "refuerzo",
        "dificultad_refuerzo": estado["dificultad"],
        "aciertos_refuerzo": estado["aciertos_refuerzo"],
        "aciertos_dificultad": estado["aciertos_practica"],
        "error_refuerzo": estado.get("error") or "",
        "token_ejercicio": estado["token"],
        "completado": estado["completado"],
        "numero_tema": numero_tema,
        "mensaje_error": {
            "E008": "Recordá respetar la jerarquía: primero multiplicaciones y divisiones; después sumas y restas."
        }.get(evaluacion.get("error_detectado") if evaluacion else None,
              evaluacion.get("error_detectado") if evaluacion else ""),
    }
    return render(request, "aprendizaje/practica_jerarquia.html", contexto)

def obtener_patrones_tema(numero_tema):
    patrones = {
        1: {
            1: "a+b*c",
            2: "a+b*c-d",
            3: "a+b*c-d*e",
        },
        2: {
            1: "a+b*c",
            2: "a+b*c-d",
            3: "a+b*c-d*e",
        },
    }

    return patrones.get(numero_tema, {})
def explicacion_enteros(request):
    return render(request, "aprendizaje/explicacion_enteros.html")
