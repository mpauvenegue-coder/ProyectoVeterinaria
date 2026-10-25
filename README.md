# Proyecto Veterinaria API

API REST desarrollada con **Django** y **Django REST Framework** para gestionar propietarios, veterinarios, servicios, citas y pagos de una veterinaria.

El proyecto **no requiere frontend**: sus funcionalidades se pueden probar mediante **Postman** y pruebas automatizadas.

## Requisitos

- Python instalado.
- MySQL instalado y en ejecución, con permisos para crear una base de datos.
- Dependencias especificadas en `requirements.txt` (Django 5.2.17, Django REST Framework 3.16.1, python-dotenv 1.2.1 y PyMySQL 1.1.2, según la configuración del proyecto).

## Instalación desde cero (Windows y PowerShell)

Abrir PowerShell en la carpeta del proyecto, donde se encuentra `manage.py`, y ejecutar:

```powershell
py -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Editar `.env` con la configuración local. **Nunca publicar `.env` en GitHub.** Las siguientes variables muestran valores de ejemplo, no credenciales reales:

```dotenv
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

Crear la base de datos en MySQL, por ejemplo desde MySQL Workbench:

```sql
CREATE DATABASE veterinaria_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Aplicar las migraciones incluidas en el repositorio y crear un superusuario:

```powershell
python manage.py migrate
python manage.py createsuperuser
```

Opcionalmente, cargar datos ficticios, grupos y usuarios de demostración:

```powershell
python manage.py preparar_demo
```

> **Seguridad:** `preparar_demo` crea usuarios de ejemplo con contraseñas conocidas y tokens de prueba. Utilizarlo **únicamente en una base local de demostración**, nunca en un servidor público. No publicar contraseñas ni tokens reales.

Iniciar el servidor:

```powershell
python manage.py runserver
```

- Servidor local: http://127.0.0.1:8000/
- Panel de administración: http://127.0.0.1:8000/admin/

## Pruebas automatizadas

Ejecutar:

```powershell
python manage.py test
```

El proyecto contempla **19 pruebas automatizadas en `citas/tests.py`**. La ejecución y sus resultados deben verificarse en el entorno configurado y conservarse como evidencia mediante una captura o registro de consola.

## Pruebas con Postman

Importar en Postman los archivos:

- `postman/VeterinariaAPI.postman_collection.json`
- `postman/VeterinariaAPI.postman_environment.json`

Seleccionar el entorno importado. La colección contempla **20 solicitudes**, con respuestas esperadas y comprobaciones de códigos HTTP.

Para reproducir las pruebas:

1. Preparar una base de datos local de desarrollo y ejecutar `python manage.py preparar_demo`.
2. Verificar los identificadores reales de propietario y veterinario, y configurar las variables `propietario_demo_id` y `veterinario_demo_id` según corresponda.
3. Configurar localmente `clave_admin`, `clave_recepcionista` y `clave_consulta` con las contraseñas de demostración.
4. Ejecutar las solicitudes en orden, de la **01 a la 20**. Las solicitudes 01 a 03 obtienen los tokens de los tres perfiles; las solicitudes de creación pueden guardar identificadores para operaciones posteriores.
5. Revisar el código HTTP y el contenido de cada respuesta.

Para las rutas protegidas se utiliza el encabezado:

```http
Authorization: Token <token>
```

> **Importante:** No exportar ni compartir el entorno después de introducir contraseñas o tokens reales. Si se repite la colección, pueden producirse conflictos por identificaciones, códigos o registros ya existentes. Algunas solicitudes dependen de datos creados previamente y de los identificadores usados en las pruebas; ajustar los valores o reiniciar los datos de prueba cuando sea necesario.

## Módulos y funcionamiento

1. **Propietarios:** registra la información del responsable de la mascota.
2. **Veterinarios:** administra los profesionales que prestan servicios.
3. **Servicios:** gestiona los servicios ofrecidos, sus precios, cupos y la asignación de veterinarios.
4. **Citas:** registra al propietario, los datos básicos de la mascota, la fecha, el estado y los servicios solicitados mediante `DetalleCita`.
5. **Pagos:** registra los abonos asociados a las citas.

Una cita puede incluir varios servicios y un mismo servicio puede formar parte de distintas citas, mediante `DetalleCita`. La información de la cita permite calcular el total, el monto pagado y el saldo pendiente.

**Alcance:** no se incluye un modelo independiente de mascota ni un expediente médico.

## Endpoints

| Método | Ruta | Función |
|---|---|---|
| POST | `/api/token/` | Obtener token de autenticación |
| GET | `/api/perfil/` | Consultar el perfil autenticado |
| GET | `/api/sesion/` | Consultar información de sesión |
| GET, POST | `/api/propietarios/` | Listar y crear propietarios |
| GET, PUT, PATCH, DELETE | `/api/propietarios/<id>/` | Consultar, editar y eliminar un propietario |
| GET, POST | `/api/veterinarios/` | Listar y crear veterinarios |
| GET, PUT, PATCH, DELETE | `/api/veterinarios/<id>/` | Consultar, editar y eliminar un veterinario |
| GET, POST | `/api/servicios/` | Listar y crear servicios |
| GET, PUT, PATCH, DELETE | `/api/servicios/<id>/` | Consultar, editar y eliminar un servicio |
| GET, POST | `/api/citas/` | Listar y crear citas |
| GET, PUT, PATCH, DELETE | `/api/citas/<id>/` | Consultar, editar y eliminar una cita |
| GET, POST | `/api/citas/<id>/detalles/` | Listar y agregar servicios a una cita |
| GET, PUT, PATCH, DELETE | `/api/citas/detalles/<id>/` | Consultar, editar y eliminar un detalle |
| GET, POST | `/api/pagos/` | Listar y registrar pagos |
| GET, PUT, PATCH, DELETE | `/api/pagos/<id>/` | Consultar, editar y eliminar un pago |
| GET | `/api/reportes/resumen/` | Consultar el resumen general |
| GET | `/api/reportes/propietarios-atenciones/` | Consultar el reporte de atenciones por propietario |
| GET | `/api/reportes/servicios-bajo-cupos/` | Consultar servicios con pocos cupos |
| GET | `/api/reportes/citas-propietario/<id>/` | Consultar citas por propietario |
| GET | `/api/reportes/servicios-veterinario/<id>/` | Consultar servicios por veterinario |

Los listados admiten filtros, búsqueda, ordenamiento y/o paginación, según el recurso. Por ejemplo:

```http
GET /api/citas/?estado=PENDIENTE&propietario=1&page=1
GET /api/servicios/?tipo=Consulta&veterinario=1&ordering=precio&page=1
```

## Roles y permisos

- **Administrador:** puede consultar, crear, modificar y eliminar, de acuerdo con los permisos configurados.
- **Recepcionista:** puede consultar, crear y modificar; no eliminar.
- **Consulta:** acceso de solo lectura.
- **Sin autenticación:** acceso denegado a los recursos protegidos.

Los permisos se gestionan mediante usuarios, grupos y permisos de Django. Para los detalles, consultar la matriz de permisos del documento técnico.

## Limitaciones conocidas

- No incluye frontend, expediente médico ni agenda con verificación automática de horarios.
- `cupos` representa unidades disponibles de atención por servicio, no productos físicos.
- Cada equipo debe configurar sus propias credenciales y conexión local con MySQL.
- Las pruebas de Postman y las automatizadas deben ejecutarse en el entorno correspondiente; este README no sustituye la evidencia de ejecución.
- Los aportes individuales, commits, revisiones y Pull Requests deben reflejar el trabajo real de los integrantes.

## Documentación técnica

El documento técnico del proyecto, que contempla el diagrama entidad-relación, la matriz de permisos, las reglas de negocio y el catálogo de endpoints, se encuentra en:

`docs/Documento_tecnico.pdf`

> **Nota para la entrega:** verificar que las rutas de los archivos de Postman, el documento técnico, las migraciones y los endpoints coincidan con los archivos y el código de la versión final del repositorio.
