import  random
import re
from .models import (EjercicioGeneradoPorError, EjercicioGeneradoPractica,
                     Progreso, PasoEjercicioBase,PatronTermino,PasoPatron,Ejercicio)

from sympy import Rational, gcd, sympify
from itertools import product



def generar_equivalencia(dificultad):
    if dificultad==1:
        numerador=random.randint(1,5)
        denominador=random.randint(numerador+1,10)
        factor=random.randint(2,4)
    elif dificultad==2:
        numerador=random.randint(3,12)
        denominador=random.randint(numerador+1,20)
        factor=random.randint(3,6)
    elif dificultad==3:
        numerador=random.randint(5,20)
        denominador=random.randint(numerador+1,30)
        factor=random.randint(4,9)
    else:
        raise ValueError("La dificultad debe ser 1,2 o 3")

    numerador_esperado=numerador*factor
    denominador_esperado=denominador*factor

    return{
        "numerador":numerador,
        "denominador":denominador,
        "factor":factor,
        "numerador_esperado":numerador_esperado,
        "denominador_esperado":denominador_esperado,
    }

def guardar_equivalencia_generada(ejercicio_base,error,dificultad):
    datos=generar_equivalencia(dificultad)

    expresion=(
        f"{datos["numerador"]}/{datos["denominador"]}"
        f" = ?/? (multiplicar por {datos["factor"]})"
        )
    resultado=(
        f"{datos["numerador_esperado"]}/"
        f"{datos["denominador_esperado"]}"
    )

    ejercicio_generado=EjercicioGeneradoPorError.objects.create(
        ejercicio=ejercicio_base,
        error=error,
        dificultad=dificultad,
        expresion_generada=expresion,
        resultado_correcto=resultado
    )
    return ejercicio_generado

def guardar_equivalencia_practica(ejercicio_base,progreso):
    if progreso.modo==Progreso.EVALUACION:
        dificultad=3
    else:
        dificultad=ejercicio_base.dificultad
    datos=generar_equivalencia(dificultad)
    expresion=(
        f"{datos["numerador"]}/{datos["denominador"]}"
        f" = ?/? (multiplicar por {datos["factor"]})"
    )
    resultado=(
        f"{datos["numerador_esperado"]}/"
        f"{datos["denominador_esperado"]}"
    )
    ejercicio_generado=EjercicioGeneradoPractica.objects.create(
        ejercicio_base=ejercicio_base,
        expresion_generada=expresion,
        resultado_correcto=resultado,
        modo=progreso.modo
    )
    return ejercicio_generado

def tokenizar_plantilla(ejercicio):
    plantilla=[]
    i=0
    while i<len(ejercicio):
        if ejercicio[i:i+2]=="**":
            plantilla.append("**")
            i+=2
        else:
            plantilla.append(ejercicio[i])
            i+=1

    return plantilla

def generar_ejercicio_combinado(plantilla, nivel):
    datos_ejercicio = {}
    ejercicio = []

    for i, char in enumerate(plantilla):
        if char.isalpha() and char != "x":
            if char not in datos_ejercicio:
                numero = random.randint(1, 10)

                if nivel == 2:
                    numero = random.choice([-1, 1]) * numero

                datos_ejercicio[char] = numero

            numero = datos_ejercicio[char]

            if numero < 0:
                ejercicio.append(f"({numero})")
            else:
                ejercicio.append(str(numero))
        else:
            ejercicio.append(char)

    datos_ejercicio["expresion"] = "".join(ejercicio)

    return datos_ejercicio

def obtener_ejercicio_combinado(ejercicio_base,datos_ejercicio):
    pasos_correctos=PasoEjercicioBase.objects.filter(ejercicio=ejercicio_base).order_by("numero_paso")
    pasos_traducidos={}
    for paso in pasos_correctos:
        numero=paso.numero_paso
        expresion=paso.expresion_esperada
        texto = expresion

        for clave,valor in datos_ejercicio.items():
            if clave != "expresion":
                texto=texto.replace(clave,str(valor))

        pasos_traducidos[numero]=texto

    return pasos_traducidos

def separar_terminos(pasos_traducidos):
    ejercicio = pasos_traducidos["expresion"]
    terminos = []
    termino_actual = ""
    profundidad = 0

    for i, caracter in enumerate(ejercicio):

        if caracter == "(":
            profundidad += 1


        elif caracter == ")":
            profundidad -= 1

        if (profundidad == 0
                and caracter in ("+", "-")
                and i > 0
                and ejercicio[i-1] not in ("+", "-", "*", "/", "(")):

            terminos.append(termino_actual)
            termino_actual = caracter

        else:
            termino_actual += caracter

    if termino_actual:
        terminos.append(termino_actual)

    return terminos

def normalizar_termino(termino):
    equivalencias={}
    letras="abcdefghijklmnopq"
    termino_normalizado=""
    indice=0
    for caracter in termino:
        if caracter.isalpha():
            if caracter not in equivalencias:
                equivalencias[caracter]=letras[indice]
                indice+=1
            termino_normalizado+=equivalencias[caracter]
        else:
            termino_normalizado+=caracter

    return {
        "patron": termino_normalizado,
        "equivalencias":equivalencias
    }

def buscar_patron(termino):
    signo = "-" if termino.startswith("-") else "+"
    termino_limpio = termino.lstrip("+-")


    datos=normalizar_termino(termino_limpio)
    patron=PatronTermino.objects.filter(patron=datos["patron"],activo=True).first()
    return{"patron":patron,"equivalencias":datos["equivalencias"],"signo": signo}

def obtener_resoluciones_patron(patron):
    pasos=PasoPatron.objects.filter(patron=patron).order_by("id")
    nodos={}
    raices=[]
    for paso in pasos:
        nodos[paso.id]={
            "id": paso.id,
            "expresion": paso.expresion,
            "calculo_r": paso.calculo_r,
            "calculo_s": paso.calculo_s,
            "calculo_t": paso.calculo_t,
            "calculo_u": paso.calculo_u,
            "descripcion": paso.descripcion,
            "error_asociado": paso.error_asociado_id,
            "es_final": paso.es_final,
            "paso_anterior_id": paso.paso_anterior_id,
            "siguientes": []
        }
    for nodo in nodos.values():
        anterior_id=nodo["paso_anterior_id"]
        if anterior_id is None:
            raices.append(nodo)
        else:
            nodos[anterior_id]["siguientes"].append(nodo)

    return raices

def reemplazar_variables(expresion, variables):

    def sustituir(coincidencia):
        letra = coincidencia.group()

        if letra in variables:
            numero = variables[letra]

            if numero < 0:
                return f"({numero})"

            return str(numero)

        return letra

    return re.sub(r"\b[a-z]\b", sustituir, expresion)

def traducir_resoluciones_patron(arbol, equivalencias, valores):

    # Relacionamos las letras originales con las del patrón.
    # Ejemplo: h -> a, y el valor de h es 2.
    variables_iniciales = {}

    for letra_original, letra_patron in equivalencias.items():
        variables_iniciales[letra_patron] = Rational(
            valores[letra_original]
        )

    # Guardaremos aquí todas las rutas traducidas.
    resoluciones = []

    # Función interna para recorrer cada rama del árbol.
    def recorrer(nodo, variables, camino):

        # Copiamos las variables para que una rama
        # no modifique los valores de otra.
        variables_actuales = variables.copy()

        # Guardamos temporalmente los nuevos cálculos.
        nuevos_valores = {}

        # Revisamos los cálculos r, s, t y u del paso.
        for letra in ("r", "s", "t", "u"):

            calculo = nodo[f"calculo_{letra}"]

            if calculo:
                nuevos_valores[letra] = calcular_expresion(
                    calculo,
                    variables_actuales
                )

        # Actualizamos las variables después de calcularlas todas.
        variables_actuales.update(nuevos_valores)

        # Reemplazamos las letras por sus valores numéricos.
        expresion_traducida = reemplazar_variables(
            nodo["expresion"],
            variables_actuales
        )

        # Guardamos el paso traducido.
        nuevo_camino = camino + [{
            "id": nodo["id"],
            "expresion": expresion_traducida,
            "error_asociado": nodo["error_asociado"],
            "es_final": nodo["es_final"]
        }]

        # Si no tiene continuaciones, guardamos la ruta completa.
        if not nodo["siguientes"]:
            resoluciones.append(nuevo_camino)
            return

        # Recorremos todas las continuaciones posibles.
        for siguiente in nodo["siguientes"]:
            recorrer(
                siguiente,
                variables_actuales,
                nuevo_camino
            )

    # Iniciamos el recorrido desde cada primer paso.
    for raiz in arbol:
        recorrer(raiz, variables_iniciales, [])

    return resoluciones

def calcular_expresion(expresion, variables):

    # Sustituimos MCD por la función gcd de SymPy.
    expresion = expresion.replace("MCD(", "gcd(")

    # Calculamos la expresión utilizando las variables disponibles.
    return sympify(
        expresion,
        locals={**variables, "gcd": gcd, "Rational": Rational}
    )

def generar_refuerzo(regla, dificultad):

    # Buscar una plantilla aleatoria.
    plantilla = Ejercicio.objects.filter(
        regla_refuerzo=regla,
        dificultad=dificultad,
        activo=True
    ).order_by("?").first()

    if plantilla is None:
        return None

    # Generar los valores numéricos.
    datos = generar_ejercicio_combinado(
        plantilla.expresion_inicial,
        dificultad
    )

    if datos is None:
        return None

    # Calcular el resultado correcto.
    valores = {
        letra: Rational(numero)
        for letra, numero in datos.items()
        if letra != "expresion"
    }

    resultado = sympify(
        plantilla.resultado_correcto,
        locals=valores
    )

    return {
        "plantilla": plantilla,
        "expresion": datos["expresion"],
        "valores": datos,
        "resultado_correcto": resultado
    }

def preparar_ejercicio_completo(ejercicio_base,valores):
    datos={"expresion":ejercicio_base.expresion_inicial}
    terminos=separar_terminos(datos)
    resultado=[]
    for termino in terminos:
        datos_patron=buscar_patron(termino)
        patron=datos_patron["patron"]
        if patron is None:
            raise ValueError(f"Patrón no encontrado: {termino}")

        arbol=obtener_resoluciones_patron(patron)
        rutas=traducir_resoluciones_patron(arbol,datos_patron["equivalencias"],valores)
        resultado.append({
            "termino": termino,
            "signo": datos_patron["signo"],
            "rutas": rutas
        })
    return resultado

def combinar_resoluciones(terminos_preparados):

    # Obtenemos las rutas disponibles de cada término.
    opciones = [termino["rutas"] for termino in terminos_preparados]

    # Guardaremos todas las resoluciones completas.
    resoluciones = []

    # product genera todas las combinaciones de rutas.
    for combinacion in product(*opciones):

        # Buscamos la cantidad de pasos de la ruta más larga.
        cantidad_pasos = max(len(ruta) for ruta in combinacion)

        # Guardaremos los pasos de esta combinación.
        camino = []

        for numero_paso in range(cantidad_pasos):

            partes = []

            # Recorremos los cuatro términos.
            for indice, ruta in enumerate(combinacion):

                # Si la ruta terminó, usamos su último paso.
                posicion = min(numero_paso, len(ruta) - 1)

                # Obtenemos la expresión numérica.
                expresion = ruta[posicion]["expresion"]

                # Recuperamos el signo original del término.
                signo = terminos_preparados[indice]["signo"]

                # Agregamos el signo y la expresión.
                partes.append(signo + expresion)

            # Unimos los términos en una sola expresión.
            expresion_completa = "".join(partes).lstrip("+")

            # Guardamos el paso completo.
            camino.append(expresion_completa)

        resoluciones.append(camino)

    return resoluciones

def normalizar_expresion_numerica(expresion, valores):
    equivalencias = {}
    expresion_normalizada = expresion

    for letra, numero in valores.items():
        representacion = f"({numero})" if numero < 0 else str(numero)
        equivalencias[letra] = numero

    return equivalencias


def resolver_parentesis(expresion):
    inicio = expresion.find("(")
    fin = expresion.find(")")

    if inicio == -1 or fin == -1:
        return expresion

    operacion = expresion[inicio + 1:fin]

    if "*" in operacion:
        a, b = operacion.split("*")
        resultado = int(a) * int(b)
    elif "+" in operacion:
        a, b = operacion.split("+")
        resultado = int(a) + int(b)
    else:
        return expresion

    return expresion[:inicio] + str(resultado) + expresion[fin + 1:]


















