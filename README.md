# Veterinaria Patitas al Rescate

## Descripción del proyecto

Veterinaria Patitas al Rescate es una API REST desarrollada con Python, Django y Django REST Framework. Su objetivo es facilitar la administración de una veterinaria mediante el registro de propietarios, veterinarios, servicios, citas y pagos.

El sistema permite consultar, registrar, actualizar y eliminar información según los permisos de cada usuario. También incluye reportes, validaciones y controles para mantener la información organizada.

## Tecnologías utilizadas

- Python
- Django 5.2.17
- Django REST Framework 3.16.1
- MySQL
- PyMySQL 1.1.2
- python-dotenv 1.2.1
- Postman para realizar pruebas de la API
- Git y GitHub para el control de versiones

## Funcionalidades principales

El proyecto está organizado en cinco módulos:

**1. Propietarios**

Permite registrar y administrar los datos de los propietarios de las mascotas, incluyendo su identificación, nombre, teléfono, correo electrónico y estado.

**2. Veterinarios**

Permite gestionar la información de los veterinarios, como su identificación profesional, nombre, teléfono, correo electrónico y estado.

**3. Servicios**

Administra los servicios que ofrece la veterinaria. Cada servicio contiene información como código, nombre, descripción, tipo, precio, cupos disponibles y veterinario asignado.

**4. Citas**

Permite registrar las citas de las mascotas, incluyendo el propietario, nombre y especie de la mascota, fechas, estado y observaciones.

Cada cita puede incluir varios servicios mediante el modelo `DetalleCita`. El sistema calcula el total de los servicios, los pagos realizados y el saldo pendiente.

**5. Pagos**

Permite registrar y administrar los pagos correspondientes a las citas, incluyendo el monto, la fecha, el método de pago y la referencia.

Una cita puede tener varios pagos, siempre que se cumplan las validaciones establecidas.

## Requisitos para ejecutar el proyecto

Antes de comenzar, es necesario tener instalado:

- Python
- MySQL y MySQL Workbench
- Git, si se desea clonar el repositorio
- Visual Studio Code u otro editor de código

Las dependencias de Python se encuentran en el archivo `requirements.txt`.

## Instalación y configuración

### 1. Descargar el proyecto

Clonar el repositorio:

```powershell
git clone https://github.com/mpauvenegue-coder/ProyectoVeterinaria.git
```

Entrar a la carpeta del proyecto:

```powershell
cd ProyectoVeterinaria
```

También se puede descargar el proyecto como archivo ZIP desde GitHub y extraerlo.

### 2. Crear y activar el entorno virtual

Desde la carpeta principal del proyecto, ejecutar:

```powershell
py -m venv .venv
```

Activar el entorno:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Instalar las dependencias

Con el entorno virtual activado:

```powershell
pip install -r requirements.txt
```

### 4. Configurar la base de datos

Abrir MySQL Workbench y crear la base de datos:

```sql
CREATE DATABASE veterinaria_db;
```

El proyecto utiliza variables de entorno para configurar la conexión con MySQL.

Crear el archivo `.env` a partir de `.env.example`:

```powershell
Copy-Item .env.example .env
```

Revisar que el archivo `.env` tenga la configuración correspondiente:

```env
SECRET_KEY=clave-local-para-pruebas
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

DB_ENGINE=mysql
DB_NAME=veterinaria_db
DB_USER=root
DB_PASSWORD=root
DB_HOST=127.0.0.1
DB_PORT=3306
```

La contraseña debe cambiarse si la instalación local de MySQL utiliza una diferente.

### 5. Aplicar las migraciones

Ejecutar:

```powershell
python manage.py migrate
```

Este comando crea las tablas necesarias en la base de datos.

### 6. Crear un superusuario

```powershell
python manage.py createsuperuser
```

Ingresar el nombre de usuario, correo electrónico y contraseña solicitados.

### 7. Preparar los datos de prueba

El proyecto cuenta con el comando:

```powershell
python manage.py preparar_demo
```

Este comando permite crear usuarios, grupos, permisos y datos de ejemplo para probar el funcionamiento del sistema.

### 8. Ejecutar el servidor

```powershell
python manage.py runserver
```

El servidor se inicia normalmente en:

http://127.0.0.1:8000/

Para ingresar al panel administrativo de Django:

http://127.0.0.1:8000/admin/

## Endpoints de la API

La API utiliza diferentes rutas para administrar los recursos del sistema.

### Autenticación y sesión

| Método | Endpoint | Función |
|---|---|---|
| POST | `/api/token/` | Obtener token de autenticación |
| GET | `/api/perfil/` | Consultar el perfil del usuario |
| GET | `/api/sesion/` | Consultar información de sesión |

### Gestión de registros

| Recurso | Endpoint |
|---|---|
| Propietarios | `/api/propietarios/` |
| Veterinarios | `/api/veterinarios/` |
| Servicios | `/api/servicios/` |
| Citas | `/api/citas/` |
| Pagos | `/api/pagos/` |

Estas rutas permiten utilizar los métodos `GET` y `POST` para consultar y crear registros.

Para consultar, actualizar o eliminar un registro específico, se utiliza su identificador:

```text
/api/propietarios/{id}/
/api/veterinarios/{id}/
/api/servicios/{id}/
/api/citas/{id}/
/api/pagos/{id}/
```

Las rutas de detalle permiten utilizar `GET`, `PUT`, `PATCH` y `DELETE`, según los permisos del usuario y las reglas del sistema.

### Detalles de las citas

| Método | Endpoint | Función |
|---|---|---|
| GET, POST | `/api/citas/{id}/detalles/` | Consultar o agregar servicios a una cita |
| GET, PUT, PATCH, DELETE | `/api/citas/detalles/{id}/` | Consultar, modificar o eliminar un detalle |

### Reportes

El sistema incluye las siguientes consultas:

| Endpoint | Función |
|---|---|
| `/api/reportes/resumen/` | Resumen general de los registros y pagos |
| `/api/reportes/propietarios-atenciones/` | Atenciones y pagos por propietario |
| `/api/reportes/servicios-bajo-cupos/` | Servicios con pocos cupos disponibles |
| `/api/reportes/citas-propietario/{id}/` | Citas de un propietario |
| `/api/reportes/servicios-veterinario/{id}/` | Servicios asociados a un veterinario |

Todos los reportes utilizan el método `GET`.

## Filtros, búsquedas y paginación

La API permite filtrar y buscar información según el módulo.

Entre los parámetros disponibles se encuentran:

- Propietarios: `activo`, `buscar`, `ordering` y `page`.
- Veterinarios: `activo`, `buscar` y `page`.
- Servicios: `tipo`, `veterinario`, `activo`, `buscar`, `ordering` y `page`.
- Citas: `estado`, `propietario`, `activo`, `ordering` y `page`.
- Pagos: `cita`, `metodo`, `activo` y `page`.

Los listados utilizan paginación de cinco registros por página.

Ejemplo para consultar citas pendientes:

```http
GET /api/citas/?estado=PENDIENTE&page=1
```

## Usuarios y permisos

El sistema utiliza autenticación mediante tokens y sesiones de Django.

Se manejan tres perfiles principales:

| Perfil | Consultar | Crear | Modificar | Eliminar |
|---|---|---|---|---|
| Administrador | Sí | Sí | Sí | Sí |
| Recepcionista | Sí | Sí | Sí | No |
| Consulta | Sí | No | No | No |

Los permisos se administran mediante los usuarios y grupos de Django.

El administrador tiene acceso completo. Los recepcionistas pueden gestionar registros sin eliminarlos y los usuarios de consulta solamente pueden visualizar información.

## Reglas de negocio

El sistema incluye validaciones para mantener la integridad de los datos.

Entre las principales reglas se encuentran:

- Validación de campos obligatorios y valores permitidos.
- Verificación de propietarios y veterinarios activos.
- Control de los cupos disponibles en los servicios.
- Restricción de servicios repetidos dentro de una misma cita.
- Validación de fechas y estados de las citas.
- Control de pagos para evitar montos superiores al saldo pendiente.
- Actualización del estado de las citas según los pagos registrados.
- Restricciones para modificar o eliminar registros relacionados.
- Control de acceso según los permisos del usuario.

Estas validaciones se aplican en las operaciones correspondientes y permiten evitar registros incorrectos o inconsistencias.

## Pruebas del proyecto

### Pruebas automatizadas

El proyecto incluye pruebas automatizadas de Django para comprobar el funcionamiento de la API.

Para ejecutarlas:

```powershell
python manage.py test
```

También se pueden ejecutar las pruebas del módulo de citas:

```powershell
python manage.py test citas
```

En `citas/tests.py` se incluyen 19 pruebas que verifican diferentes operaciones, validaciones y permisos.

### Pruebas manuales

La API también se puede probar mediante Postman, enviando solicitudes HTTP a los diferentes endpoints.

Las pruebas permiten comprobar la creación, consulta, modificación y eliminación de registros, además de la autenticación, los permisos, los filtros y las respuestas ante datos inválidos.

## Estructura del proyecto

```text
ProyectoVeterinaria/
│
├── propietarios/
├── veterinarios/
├── servicios/
├── citas/
├── pagos/
├── veterinaria_backend/
│
├── .env.example
├── .gitignore
├── manage.py
├── requirements.txt
└── README.md
```

Las carpetas de los módulos contienen los archivos correspondientes a modelos, vistas, serializadores, rutas y otras configuraciones de Django.

La carpeta `veterinaria_backend` contiene la configuración principal del proyecto, incluyendo las rutas generales y los permisos.

## Integrantes

**Universidad de Costa Rica — Sede del Pacífico**

**Curso:** IF-0009 Desarrollo de Software IV

**Profesor:** Mag. Irwin Leal Elizondo

**Estudiantes:**

- Suly Daniela Bustos Medina — C5D410
- María Paula Venegas Sosa — C5K896

## Información adicional

Este proyecto fue desarrollado con fines académicos para aplicar los conocimientos adquiridos durante el curso, especialmente en el desarrollo de API REST, manejo de bases de datos, autenticación, permisos, validaciones y pruebas de software.

El sistema funciona como una API y no incluye una interfaz gráfica propia. Sus operaciones pueden consultarse mediante herramientas como Postman o la interfaz navegable de Django REST Framework, cuando corresponda.
