# Guía de instalación — SistemaAlgebra

## 1. Requisitos previos

Para ejecutar el sistema localmente se necesita:

- Python 3.13
- MySQL Server 8.0 o compatible
- Git
- Un editor de código, como PyCharm o Visual Studio Code (opcional)
- Conexión a Internet para descargar el proyecto y sus dependencias

Esta guía está orientada a Windows y utiliza PowerShell.

## 2. Descargar el proyecto

Abrir una terminal de PowerShell y ejecutar:

```powershell
git clone https://github.com/marianoel1979/SistemaAlgebra.git
cd SistemaAlgebra
```

Si el proyecto ya fue descargado anteriormente, no es necesario volver a clonarlo.

## 3. Crear el entorno virtual

Dentro de la carpeta del proyecto, ejecutar:

```powershell
python -m venv .venv
```

Activar el entorno virtual:

```powershell
.\.venv\Scripts\Activate.ps1
```

Si PowerShell impide la activación por su política de ejecución, utilizar:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

El entorno virtual permite instalar las dependencias del sistema sin afectar otras instalaciones de Python.

## 4. Instalar las dependencias

Con el entorno virtual activado, ejecutar:

```powershell
python -m pip install -r requirements.txt
```

Este comando instala Django y las demás bibliotecas necesarias para ejecutar el sistema.

## 5. Configurar MySQL

Iniciar MySQL Server y abrir MySQL Workbench u otra herramienta de administración.

Crear una base de datos mediante la siguiente instrucción SQL:

```sql
CREATE DATABASE sistema_algebra
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
```

Es necesario disponer de un usuario de MySQL con permisos para crear y modificar tablas y consultar y registrar datos en esta base.

La configuración de conexión se realizará mediante variables de entorno.

## 6. Configurar las variables de entorno

Crear un archivo llamado `.env` en la carpeta principal del proyecto, al mismo nivel que `manage.py`.

Incorporar las siguientes variables, reemplazando los valores de ejemplo por los correspondientes a la instalación local:

```dotenv
DB_NAME=sistema_algebra
DB_USER=usuario_mysql
DB_PASSWORD=contraseña_mysql
DB_HOST=127.0.0.1
DB_PORT=3306
SECRET_KEY=clave_secreta_generada_para_django
```

Para generar una clave secreta de Django, ejecutar desde el entorno virtual:

```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copiar la clave generada en el valor de `SECRET_KEY`.

**Importante:** el archivo `.env` contiene información privada de configuración y no debe publicarse en GitHub.

## 7. Crear las tablas de la base de datos

En la terminal, desde la carpeta principal del proyecto, ejecutar:

```powershell
python manage.py migrate
```

Este comando aplica las migraciones de Django y crea las tablas necesarias en MySQL.

## 8. Cargar los datos iniciales

Una vez creadas las tablas, ejecutar:

```powershell
python manage.py loaddata datos_iniciales.json
```

Este comando incorpora los datos iniciales incluidos en el repositorio, como niveles, temas, patrones matemáticos, errores, ejercicios y pasos de resolución.

La carga debe realizarse durante la instalación inicial, sobre una base de datos preparada para la demostración.

No es necesario volver a ejecutar este comando para cada actualización del código.

## 9. Iniciar el servidor

Ejecutar:

```powershell
python manage.py runserver
```

Django iniciará el servidor de desarrollo local.

Abrir en el navegador:

[http://127.0.0.1:8000/aprendizaje/](http://127.0.0.1:8000/aprendizaje/)

El servidor debe permanecer ejecutándose mientras se utiliza la aplicación.

Para detenerlo, presionar `Ctrl + C` en la terminal.

## 10. Acceso y prueba del sistema

SistemaAlgebra contempla dos perfiles de usuario:

**Docente:** permite administrar grupos y consultar la información de seguimiento disponible en el prototipo.

**Estudiante:** permite acceder a las actividades de práctica matemática y utilizar las funcionalidades implementadas.

Para realizar pruebas se requiere disponer de las credenciales correspondientes al perfil docente o registrar un estudiante utilizando un código de grupo válido.

Las credenciales y códigos de demostración se proporcionarán por separado, para evitar publicar contraseñas en el repositorio.

## 11. Actualizar el sistema

Cuando se publique una nueva versión del código, ingresar a la carpeta del proyecto y ejecutar:

```powershell
git pull origin main
```

Activar el entorno virtual, si todavía no está activado:

```powershell
.\.venv\Scripts\Activate.ps1
```

Actualizar las dependencias:

```powershell
python -m pip install -r requirements.txt
```

Aplicar las migraciones que pudieran haberse incorporado:

```powershell
python manage.py migrate
```

Finalmente, iniciar nuevamente el sistema:

```powershell
python manage.py runserver
```

**Importante:** las actualizaciones habituales del código no requieren eliminar la base de datos ni volver a cargar el archivo `datos_iniciales.json`.

Si una actualización incorpora nuevos datos obligatorios, se indicará expresamente en las instrucciones de esa versión.

## 12. Estado del prototipo

SistemaAlgebra es un prototipo académico desarrollado como parte del Trabajo Final de Grado de la Licenciatura en Informática.

El sistema tiene como finalidad proporcionar un entorno de práctica progresiva de álgebra, incorporando mecanismos de identificación de errores y actividades de refuerzo adaptativo.

La versión entregada permite evaluar las funcionalidades implementadas hasta la fecha. El desarrollo continuará posteriormente para completar los componentes previstos en el proyecto.

## 13. Código fuente

El código fuente y las actualizaciones del proyecto se encuentran disponibles en el repositorio público:

[https://github.com/marianoel1979/SistemaAlgebra](https://github.com/marianoel