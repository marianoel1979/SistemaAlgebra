from django.db import models
from django.conf import settings
from django.db.models.deletion import SET_NULL


# Create your models here.

class Nivel(models.Model):
    numero=models.PositiveIntegerField(unique=True)
    nombre=models.CharField(max_length=100)
    descripcion=models.TextField()

    def __str__(self):
        return f"Nivel: {self.numero} - {self.nombre}"

class Tema(models.Model):
    nivel=models.ForeignKey(Nivel,on_delete=models.CASCADE)
    numero=models.PositiveIntegerField()
    nombre=models.CharField(max_length=100)
    descripcion=models.TextField()
    class Meta:
        constraints=[models.UniqueConstraint(
            fields=['nivel','numero'],
            name='unique_tema_por_nivel'
        )]

    def __str__(self):
        return f"Nivel {self.nivel.numero} - Tema {self.numero} - {self.nombre}"

class Ejercicio(models.Model):
    tema=models.ForeignKey(Tema,on_delete=models.CASCADE)
    enunciado=models.CharField(max_length=255)
    expresion_inicial=models.CharField(max_length=255)
    resultado_correcto=models.CharField(max_length=100,blank=True,null=True)
    dificultad=models.PositiveIntegerField()
    regla_refuerzo = models.CharField( max_length=50,blank=True,default="")
    activo=models.BooleanField(default=True)

    def __str__(self):
        return self.expresion_inicial

class PasoEjercicioBase(models.Model):
    ejercicio=models.ForeignKey(Ejercicio,on_delete=models.CASCADE)
    numero_paso=models.PositiveIntegerField()
    expresion_esperada=models.CharField(max_length=100)
    tipo_operacion=models.CharField(max_length=255)

    class Meta:
        constraints=[models.UniqueConstraint(
        fields=['ejercicio','numero_paso'],
        name='unique_paso_por_ejercicio'
    )]

    def __str__(self):
        return f"Ejercicio: {self.ejercicio} - Paso: {self.numero_paso} - {self.expresion_esperada}"

class Error(models.Model):
    codigo = models.CharField(max_length=4,unique=True)
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()

    def __str__(self):
        return f"Error {self.id} - {self.descripcion}"

class EjercicioGeneradoPractica(models.Model):
    ejercicio_base=models.ForeignKey(Ejercicio,on_delete=models.PROTECT)
    expresion_generada=models.CharField(max_length=255)
    resultado_correcto=models.CharField(max_length=100)
    fecha_generacion=models.DateTimeField(auto_now_add=True)
    PRACTICA="Practica"
    EVALUACION="Evaluacion"
    MODOS = [(PRACTICA, 'Practica'),
             (EVALUACION,'Evaluacion'),]
    modo = models.CharField(max_length=10, choices=MODOS, default=PRACTICA)
    def __str__(self):
        return f"Ejercicio: {self.expresion_generada}"

class EjercicioGeneradoPorError(models.Model):
    ejercicio=models.ForeignKey(Ejercicio,on_delete=models.PROTECT)
    error=models.ForeignKey(Error,on_delete=models.PROTECT)
    dificultad = models.PositiveIntegerField(default=1)
    expresion_generada=models.CharField(max_length=255)
    resultado_correcto=models.CharField(max_length=100)
    fecha_generacion=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ejercicio {self.ejercicio}"

class Resolucion(models.Model):
    estudiante=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    ejercicio=models.ForeignKey(Ejercicio,on_delete=models.SET_NULL,null=True,blank=True)
    ejercicio_generado_practica=models.ForeignKey(EjercicioGeneradoPractica,
                                                  on_delete=models.PROTECT,
                                                  null=True, blank=True
                                                  )
    ejercicio_generado_xerror=models.ForeignKey(EjercicioGeneradoPorError,
                                                on_delete=models.SET_NULL,null=True,blank=True)
    fecha_inicio=models.DateTimeField(auto_now_add=True)
    fecha_fin=models.DateTimeField(null=True,blank=True)
    correcta=models.BooleanField(null=True,blank=True)

    def __str__(self):
        return f"Resolucion {self.id} - {self.estudiante}"

class PasoResolucion(models.Model):
    resolucion=models.ForeignKey(Resolucion,on_delete=models.CASCADE)
    numero_paso=models.PositiveIntegerField()
    expresion_ingresada=models.CharField(max_length=255)
    correcto=models.BooleanField()
    error=models.ForeignKey(Error,on_delete=models.PROTECT,null=True,blank=True)


    class Meta:
        constraints=[models.UniqueConstraint(
            fields=['resolucion','numero_paso'],
            name='unique_numero_paso_por_resolucion'
        )]
    def __str__(self):
        return f"paso {self.numero_paso} : {self.expresion_ingresada}"

class Explicacion(models.Model):
    tema=models.ForeignKey(Tema,on_delete=models.PROTECT,null=True,blank=True)
    error=models.ForeignKey(Error,on_delete=models.PROTECT,null=True,blank=True)
    cuerpo=models.TextField()
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"Explicacion {self.id} - tema: {self.tema} - error: {self.error}"

class Progreso(models.Model):
    estudiante = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    tema=models.ForeignKey(Tema,on_delete=models.PROTECT)
    PRACTICA='Practica'
    REFUERZO='Refuerzo'
    EVALUACION='Evaluacion'
    MODOS=[(PRACTICA,'Practica'),
       (REFUERZO,'Refuerzo'),
       (EVALUACION,'Evaluacion')]
    modo=models.CharField(max_length=10,choices=MODOS,default=PRACTICA)
    error=models.ForeignKey(Error,on_delete=models.PROTECT,null=True,blank=True)
    dificultad_actual=models.PositiveIntegerField(default=1)
    aciertos_dificultad=models.PositiveIntegerField(default=0)
    ejercicio_refuerzo_actual=models.ForeignKey(EjercicioGeneradoPorError,
                                                on_delete=models.PROTECT,
                                                null=True,blank=True)
    dificultad_refuerzo=models.PositiveIntegerField(default=1)
    aciertos_refuerzo=models.PositiveIntegerField(default=0)
    ejercicio_practica_actual=models.ForeignKey(EjercicioGeneradoPractica,
                                                on_delete=models.PROTECT,
                                                null=True, blank=True)
    aciertos_evaluacion = models.PositiveIntegerField(default=0)
    ejercicios_evaluacion_realizados = models.PositiveIntegerField(default=0)
    modo_anterior=models.CharField(max_length=10,choices=MODOS,null=True,blank=True)
    tema_aprobado=models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["estudiante", "tema"],
                name="unique_progreso_estudiante_tema"
            )
        ]

    def __str__(self):
        return f"Estudiante: {self.estudiante} - Tema: {self.tema}, {self.modo}, error {self.error}"

class Grupo(models.Model):
    nombre=models.CharField(max_length=100)
    codigo = models.CharField(max_length=40, unique=True)

    docente=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name = 'grupos_docente')
    activo=models.BooleanField(default=True)
    fecha_creacion=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Grupo {self.nombre}"

class PatronTermino(models.Model):
    patron=models.CharField(max_length=100,unique=True)
    descripcion=models.CharField(max_length=200)
    activo=models.BooleanField(default=True)

    def __str__(self):
        return f"{self.patron}"

class PasoPatron(models.Model):
    patron=models.ForeignKey(PatronTermino,on_delete=models.PROTECT)
    paso_anterior=models.ForeignKey("self",on_delete=models.CASCADE,null=True,blank=True,related_name="siguientes")
    expresion=models.CharField(max_length=200)
    calculo_r=models.CharField(max_length=200,null=True,blank=True)
    calculo_s = models.CharField(
        max_length=200,
        null=True,
        blank=True
    )
    calculo_t = models.CharField(
        max_length=200,
        null=True,
        blank=True
    )
    calculo_u = models.CharField(
        max_length=200,
        null=True,
        blank=True
    )
    descripcion=models.CharField(max_length=200)
    es_final=models.BooleanField(default=False)
    regla = models.CharField(max_length=50, blank=True)

    error_asociado = models.ForeignKey(
        Error,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.expresion}"


