from django.urls import path, include
from . import views
from .views import resolver_ejercicio, resolver_operacion_combinada,explicacion_jerarquia,practica_jerarquia,explicacion_enteros
urlpatterns = [
    path("resolver/", resolver_ejercicio, name="resolver_ejercicio"),
    path(
        "operacion-combinada/",
        resolver_operacion_combinada,
        name="resolver_operacion_combinada"
    ),
    path("explicacion-jerarquia/", explicacion_jerarquia, name="explicacion_jerarquia"),
    path("practica-jerarquia/", practica_jerarquia, name="practica_jerarquia"),
    path("practica-tema/<int:numero_tema>/", practica_jerarquia, name="practica_tema"),
    path("acceso/", include("aprendizaje.urls_acceso")),
    path(
    "explicacion-enteros/",explicacion_enteros,name="explicacion_enteros"
),
]