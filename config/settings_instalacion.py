
from .settings import *
import os

# Configuración independiente para la instalación local
SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "clave-local-demostracion-sistema-algebra-2026"
)

DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

# Base de datos local, sin necesidad de instalar MySQL
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
# Permite instalar y ejecutar el prototipo con SQLite
# sin modificar la configuración principal de desarrollo.