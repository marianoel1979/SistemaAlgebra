from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.deletion import SET_NULL

import aprendizaje.models


# Create your models here.
class Usuario(AbstractUser):
    ESTUDIANTE="ESTUDIANTE"
    DOCENTE="DOCENTE"

    TIPOS_USUARIO=[
        (ESTUDIANTE,"Estudiante"),
        (DOCENTE,"Docente"),
    ]
    tipo_usuario=models.CharField(
        max_length=10,choices=TIPOS_USUARIO
    )
    grupo=models.ForeignKey('aprendizaje.Grupo',null=True,blank=True,on_delete=models.SET_NULL)