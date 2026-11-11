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

## 5. Configurar la base de datos SQLite

Para facilitar la instalación y evaluación del prototipo, se utiliza SQLite, que está incluido en Python y no requiere instalar un servidor de base de datos.

El proyecto incorpora el archivo config/settings_instalacion.py, que configura automáticamente SQLite.

La base de datos se creará en el archivo db.sqlite3, dentro de la carpeta principal del proyecto, al ejecutar las migraciones.

Esta configuración es independiente de la utilizada durante el desarrollo con MySQL.

## 6. Configurar las variables de entorno

Para ejecutar el prototipo con SQLite se utilizará el archivo config/settings_instalacion.py.

Esta configuración incluye una clave de demostración para el entorno local, por lo que no es obligatorio crear un archivo .env para realizar las pruebas.

Esta configuración está destinada exclusivamente a la evaluación local del prototipo y no debe utilizarse en un servidor público de producción.
## 7. Crear las tablas de la base de datos

En la terminal, desde la carpeta principal del proyecto, ejecutar:

```powershell
python manage.py migrate --settings=config.settings_instalacion
```

Este comando aplica las migraciones de Django y crea las tablas necesarias en MySQL.

## 8. Cargar los datos iniciales

Una vez creadas las tablas, ejecutar:

```powershell
python manage.py loaddata datos_iniciales.json --settings=config.settings_instalacion
```

Este comando incorpora los datos iniciales incluidos en el repositorio, como niveles, temas, patrones matemáticos, errores, ejercicios y pasos de resolución.

La carga debe realizarse durante la instalación inicial, sobre una base de datos preparada para la demostración.

No es necesario volver a ejecutar este comando para cada actualización del código.

## 9. Iniciar el servidor

Ejecutar:

```powershell
python manage.py runserver --settings=config.settings_instalacion
```

Django iniciará el servidor de desarrollo local.

Abrir en el navegador:

http://127.0.0.1:8000/aprendizaje/acceso/ingresar/

El servidor debe permanecer ejecutándose mientras se utiliza la aplicación.

Para detenerlo, presionar `Ctrl + C` en la terminal.

## 10. Acceso y prueba del sistema

SistemaAlgebra contempla dos perfiles de usuario:

**Docente:** permite administrar grupos y consultar la información de seguimiento disponible en el prototipo.

**Estudiante:** permite acceder a las actividades de práctica matemática y utilizar las funcionalidades implementadas.

Para realizar pruebas se requiere disponer de las credenciales correspondientes al perfil docente o registrar un estudiante utilizando un código de grupo válido.

Las credenciales y códigos de demostración se proporcionarán por separado, para evitar publicar contraseñas en el repositorio.
### Opción 1. Ingresar con un usuario existente

Usuario: Mateomarcu

Contraseña: la correspondiente al usuario de demostración, proporcionada por separado.

Contenido asignado: Nivel 5, Tema 1 – Jerarquía de operaciones.

### Opción 2. Registrar un estudiante nuev

Para registrar un estudiante, utilizar el siguiente grupo previamente creado:

Grupo: 1° A

Código de grupo: 66D7994E
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
python manage.py migrate --settings=config.settings_instalacion
```

Finalmente, iniciar nuevamente el sistema:

```powershell
python manage.py runserver --settings=config.settings_instalacion
```

**Importante:** las actualizaciones habituales del código no requieren eliminar la base de datos ni volver a cargar el archivo `datos_iniciales.json`.

Si una actualización incorpora nuevos datos obligatorios, se indicará expresamente en las instrucciones de esa versión.

## 12. Estado del prototipo

SistemaAlgebra es un prototipo académico desarrollado como parte del Trabajo Final de Grado de la Licenciatura en Informática.

El sistema tiene como finalidad proporcionar un entorno de práctica progresiva de álgebra, incorporando mecanismos de identificación de errores y actividades de refuerzo adaptativo.

La versión entregada permite evaluar las funcionalidades implementadas hasta la fecha. El desarrollo continuará posteriormente para completar los componentes previstos en el proyecto.

## 13. Código fuente

El código fuente y las actualizaciones del proyecto se encuentran disponibles en el repositorio público:

https://github.com/marianoel1979/SistemaAlgebra

