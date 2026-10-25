# Proyecto Veterinaria API

API REST desarrollada con Django y Django REST Framework para gestionar propietarios, veterinarios, servicios, citas y pagos de una veterinaria.

El proyecto no requiere frontend. Las funcionalidades se prueban mediante Postman y pruebas automatizadas de Django.

## Requisitos

- Python instalado.
- MySQL instalado y en funcionamiento.
- Dependencias especificadas en `requirements.txt`:
  - Django 5.2.17
  - Django REST Framework 3.16.1
  - python-dotenv 1.2.1
  - PyMySQL 1.1.2
- Credenciales locales para acceder a MySQL y crear la base de datos.

## Instalación desde cero

Las siguientes instrucciones están dirigidas a Windows utilizando PowerShell.

### 1. Crear y activar el entorno virtual

Abrir PowerShell en la carpeta principal del proyecto, donde se encuentra `manage.py`, y ejecutar:

```powershell
py -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Configurar las variables de entorno

Crear el archivo `.env` a partir de `.env.example`:

```powershell
Copy-Item .env.example .env
```

Editar `.env` con las credenciales correspondientes a la instalación local de MySQL.

Ejemplo de configuración:

```env
SECRET_KEY=cambiar-por-una-clave-local
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
DB_ENGINE=mysql
DB_NAME=veterinaria_db
DB_USER=root
DB_PASSWORD=
DB_HOST=127.0.0.1
DB_PORT=3306
```

**Importante:** el archivo `.env` contiene información privada y no debe subirse a GitHub. El archivo `.env.example` debe incluir únicamente valores de ejemplo.

### 3. Crear la base de datos

Desde MySQL Workbench o una consola de MySQL, ejecutar:

```sql
CREATE DATABASE veterinaria_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
```

### 4. Aplicar las migraciones

Con el entorno virtual activado, ejecutar:

```powershell
python manage.py migrate
```

Este comando crea las tablas correspondientes a las migraciones incluidas en el proyecto.

### 5. Crear un superusuario

```powershell
python manage.py createsuperuser
```

Seguir las instrucciones de la consola para establecer el usuario y la contraseña.

### 6. Cargar datos de demostración (opcional)

```powershell
python manage.py preparar_demo
```

Este comando permite preparar datos ficticios, usuarios, grupos y tokens para realizar pruebas.

**Advertencia:** los usuarios de demostración utilizan credenciales conocidas. Deben emplearse únicamente en un entorno local de desarrollo y nunca en un servidor público.

### 7. Iniciar el servidor

```powershell
python manage.py runserver
```

Direcciones principales:

- API: http://127.0.0.1:8000/
- Panel de administración: http://127.0.0.1:8000/admin/

## Módulos del proyecto

La API está organizada en cinco módulos principales.

### 1. Propietarios

Permite administrar la información de los propietarios responsables de las mascotas.

Incluye datos de identificación, nombre, teléfono, correo electrónico y estado.

### 2. Veterinarios

Gestiona la información de los profesionales veterinarios que prestan servicios.

### 3. Servicios

Administra los servicios ofrecidos por la veterinaria, incluyendo su tipo, precio, cupos disponibles y veterinario asignado.

### 4. Citas

Permite registrar y gestionar las citas veterinarias.

Cada cita contiene información del propietario, nombre y especie de la mascota, fecha, estado y servicios solicitados.

Los servicios se relacionan con las citas mediante el modelo `DetalleCita`, que permite asociar varios servicios a una misma cita.

El sistema contempla el cálculo del total de la cita, los pagos realizados y el saldo pendiente.

### 5. Pagos

Permite registrar y consultar los pagos asociados a las citas veterinarias.

Una cita puede tener varios pagos.

### Relaciones principales

- Un propietario puede tener varias citas.
- Un veterinario puede estar asociado a varios servicios.
- Una cita puede incluir varios servicios.
- Un servicio puede aparecer en diferentes citas.
- Una cita puede registrar varios pagos.

La relación entre citas y servicios se administra mediante `DetalleCita`.

El proyecto no incluye un modelo independiente de mascota ni un expediente médico.

## Endpoints de la API

### Autenticación y sesión

| Método | Endpoint | Descripción |
|---|---|---|
| POST | `/api/token/` | Obtener token de autenticación |
| GET | `/api/perfil/` | Consultar el perfil autenticado |
| GET | `/api/sesion/` | Consultar información de sesión |

### Propietarios

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/api/propietarios/` | Listar propietarios |
| POST | `/api/propietarios/` | Crear propietario |
| GET | `/api/propietarios/<id>/` | Consultar propietario |
| PUT | `/api/propietarios/<id>/` | Actualizar propietario |
| PATCH | `/api/propietarios/<id>/` | Actualizar parcialmente |
| DELETE | `/api/propietarios/<id>/` | Eliminar propietario |

### Veterinarios

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/api/veterinarios/` | Listar veterinarios |
| POST | `/api/veterinarios/` | Crear veterinario |
| GET | `/api/veterinarios/<id>/` | Consultar veterinario |
| PUT | `/api/veterinarios/<id>/` | Actualizar veterinario |
| PATCH | `/api/veterinarios/<id>/` | Actualizar parcialmente |
| DELETE | `/api/veterinarios/<id>/` | Eliminar veterinario |

### Servicios

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/api/servicios/` | Listar servicios |
| POST | `/api/servicios/` | Crear servicio |
| GET | `/api/servicios/<id>/` | Consultar servicio |
| PUT | `/api/servicios/<id>/` | Actualizar servicio |
| PATCH | `/api/servicios/<id>/` | Actualizar parcialmente |
| DELETE | `/api/servicios/<id>/` | Eliminar servicio |

### Citas

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/api/citas/` | Listar citas |
| POST | `/api/citas/` | Crear cita |
| GET | `/api/citas/<id>/` | Consultar cita |
| PUT | `/api/citas/<id>/` | Actualizar cita |
| PATCH | `/api/citas/<id>/` | Actualizar parcialmente |
| DELETE | `/api/citas/<id>/` | Eliminar cita |
| GET | `/api/citas/<id>/detalles/` | Listar servicios de una cita |
| POST | `/api/citas/<id>/detalles/` | Agregar servicios a una cita |
| GET | `/api/citas/detalles/<id>/` | Consultar detalle |
| PUT | `/api/citas/detalles/<id>/` | Actualizar detalle |
| PATCH | `/api/citas/detalles/<id>/` | Actualizar parcialmente |
| DELETE | `/api/citas/detalles/<id>/` | Eliminar detalle |

### Pagos

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/api/pagos/` | Listar pagos |
| POST | `/api/pagos/` | Registrar pago |
| GET | `/api/pagos/<id>/` | Consultar pago |
| PUT | `/api/pagos/<id>/` | Actualizar pago |
| PATCH | `/api/pagos/<id>/` | Actualizar parcialmente |
| DELETE | `/api/pagos/<id>/` | Eliminar pago |

### Reportes

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/api/reportes/resumen/` | Resumen general de la veterinaria |
| GET | `/api/reportes/propietarios-atenciones/` | Reporte de atenciones por propietario |
| GET | `/api/reportes/servicios-bajo-cupos/` | Servicios con pocos cupos |
| GET | `/api/reportes/citas-propietario/<id>/` | Citas de un propietario |
| GET | `/api/reportes/servicios-veterinario/<id>/` | Servicios por veterinario |

## Filtros, búsqueda, ordenamiento y paginación

La API incorpora mecanismos para consultar información mediante filtros, búsquedas, ordenamiento y paginación, según el recurso.

Ejemplos:

**Consultar citas pendientes de un propietario:**

```http
GET /api/citas/?estado=PENDIENTE&propietario=1&page=1
```

**Consultar servicios por tipo y veterinario, ordenados por precio:**

```http
GET /api/servicios/?tipo=Consulta&veterinario=1&ordering=precio&page=1
```

**Buscar propietarios:**

```http
GET /api/propietarios/?buscar=Maria&page=1
```

## Roles y permisos

El sistema contempla tres perfiles de usuario.

| Perfil | Consultar | Crear | Modificar | Eliminar |
|---|---|---|---|---|
| Administrador | Sí | Sí | Sí | Sí |
| Recepcionista | Sí | Sí | Sí | No |
| Consulta | Sí | No | No | No |

Los usuarios sin autenticación no pueden acceder a los recursos protegidos.

La autorización depende de los permisos de Django asignados a cada usuario o grupo.

La matriz detallada de permisos se encuentra en la documentación técnica del proyecto.

## Pruebas automatizadas

Para ejecutar las pruebas de Django:

```powershell
python manage.py test
```

El proyecto contempla 19 pruebas automatizadas en `citas/tests.py`, destinadas a verificar el comportamiento de la API, sus validaciones y permisos.

La ejecución debe realizarse en un entorno correctamente configurado. Los resultados reales de la consola deben conservarse como evidencia de las pruebas realizadas.

## Pruebas con Postman

El proyecto contempla una colección de 20 solicitudes para comprobar el funcionamiento de los endpoints.

Archivos de referencia:

- `postman/VeterinariaAPI.postman_collection.json`
- `postman/VeterinariaAPI.postman_environment.json`

### Procedimiento

1. Iniciar el servidor Django.
2. Importar la colección y el entorno en Postman.
3. Seleccionar el entorno correspondiente.
4. Configurar las variables locales necesarias.
5. Preparar los datos de demostración si se requiere.
6. Ejecutar las solicitudes en el orden establecido.
7. Revisar los códigos HTTP y las respuestas obtenidas.

Las solicitudes incluyen operaciones CRUD, autenticación, permisos, filtros, reportes y validaciones de reglas de negocio.

Los códigos HTTP contemplados incluyen:

- `200 OK`: operación o consulta exitosa.
- `201 Created`: recurso creado correctamente.
- `204 No Content`: eliminación exitosa cuando está permitida.
- `400 Bad Request`: datos inválidos.
- `401 Unauthorized`: falta de autenticación.
- `403 Forbidden`: usuario sin permisos suficientes.
- `404 Not Found`: recurso inexistente.
- `409 Conflict`: operación rechazada por un conflicto con las reglas del sistema.

### Consideraciones de seguridad

No deben publicarse contraseñas ni tokens reales en los archivos exportados de Postman.

Las solicitudes de autenticación pueden almacenar tokens en variables del entorno para utilizarse en las peticiones posteriores.

Si se repiten las pruebas, pueden producirse conflictos por identificaciones, códigos o registros creados anteriormente. En ese caso, deben utilizarse nuevos datos de prueba o restablecerse los registros correspondientes.

## Reglas de negocio y validaciones

El sistema incorpora validaciones destinadas a mantener la integridad de la información.

Estas reglas se aplican a las operaciones correspondientes y pueden generar respuestas de error cuando los datos no cumplen las condiciones establecidas.

Entre los escenarios contemplados se encuentran:

- Validación de datos obligatorios.
- Control de valores inválidos.
- Verificación de relaciones entre registros.
- Restricciones de eliminación cuando existen registros asociados.
- Control de acceso según el perfil del usuario.

El detalle de las reglas de negocio y sus códigos HTTP se documenta en el documento técnico.

## Limitaciones conocidas

- No incluye una interfaz gráfica o frontend.
- No contempla un expediente médico independiente.
- No dispone de un modelo separado para mascotas.
- No implementa una agenda con comprobación automática de disponibilidad horaria.
- Los cupos representan unidades disponibles de atención por servicio.
- La configuración de MySQL y las credenciales deben establecerse en cada equipo.
- Las pruebas deben ejecutarse en un entorno configurado para obtener evidencia válida.

## Trabajo colaborativo con GitHub

El desarrollo del proyecto se realiza mediante Git y GitHub.

Se utilizan ramas individuales para organizar los aportes de las integrantes y Pull Requests para integrar los cambios en la rama principal `main`.

El historial del repositorio permite consultar los commits, las contribuciones individuales y las integraciones realizadas durante el desarrollo.

## Documentación técnica

La documentación complementaria del proyecto incluye el diagrama entidad-relación, la matriz de permisos, las reglas de negocio y el catálogo de endpoints.

Archivo de referencia:

`docs/Documento_tecnico.pdf`

## Tecnologías utilizadas

- Python
- Django
- Django REST Framework
- MySQL
- PyMySQL
- python-dotenv
- Postman
- Git y GitHub

## Integrantes

- María Paula
- Daniela

## Observaciones finales

Este proyecto tiene fines académicos y está orientado a demostrar el desarrollo de una API REST mediante Django, la integración con una base de datos relacional, la aplicación de reglas de negocio, el control de permisos y la realización de pruebas automatizadas y manuales.