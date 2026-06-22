# Altezza - Sistema Web para Restaurante

Altezza es una aplicación web desarrollada para la gestión de un restaurante. El sistema permite visualizar el menú, gestionar platos, administrar reservas, reseñas y funcionalidades relacionadas al panel de administración.

El proyecto está separado en dos aplicaciones Flask:

* **Backend**: expone la API y se conecta con la base de datos MySQL.
* **Frontend**: renderiza las vistas web y consume los endpoints del backend.

---
## Las credenciales que hay que cambiar:



---

## Tecnologías utilizadas

* Python 3
* Flask
* MySQL
* HTML
* CSS
* JavaScript
* Jinja2
* Requests
* Entorno virtual con `venv`

---

## Bibliotecas/complementos:
* Flask-mail
* Bcrypt
* qrcode
* python-dotenv
* re
* mysql-connector-python

## .env del FRONTEND

SECRET_KEY=

#Email
MAIL_SERVER= smtp.gmail.com
MAIL_PORT= 587
MAIL_USE_TLS= True
MAIL_USE_SSL= False
MAIL_USERNAME= 
MAIL_PASSWORD= 
MAIL_DEFAULT_SENDER= altezzaadmin@gmail.com

## .env del BACKEND

SECRET_KEY=
JWT_SECRET_KEY=

#Database
DB_HOST=db
DB_USER= 
DB_PASSWORD= 
DB_NAME= altezza

MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_DEFAULT_SENDER=altezzaadmin@gmail.com

## Puertos utilizados

La aplicación funciona localmente con los siguientes puertos:

```
Frontend: http://127.0.0.1:5001
Backend:  http://127.0.0.1:5000
```

---

## Base de datos

El proyecto utiliza MySQL.

Los datos de conexión por defecto son:

```
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=
DB_PASSWORD= 
DB_NAME=altezza
```

---

## Levantar el proyecto con Docker

Desde la raíz del proyecto, ejecutar:

```
docker compose up --build
```

Esto construye las imágenes y levanta los contenedores.

---
## Script de ejecución sin Docker

El proyecto se puede levantar sin Docker usando el archivo:
(LINUX)

```
iniciar.sh
```

Y bajarlo con:

```
apagar.sh
```

Configuración actual:

```
Backend:  puerto 5000
Frontend: puerto 5001
```

---

## Verificar que MySQL esté corriendo y que los datos de conexión sean correctos.

Datos por defecto:

```
Usuario:
Contraseña:
Base: altezza
Puerto: 3306
```
CORROBORAR QUE EL USUARIO Y LA CONTRASENA SEAN LOS INDICADOS

---

## Autores

Proyecto desarrollado como trabajo final para la materia Introducción al Desarrollo de Software.

Integrantes:

Juan Cruz, Presas, 115479
Julian, Hidalgo, 114444
Tomas, Vitale, 113963
Marcos, Quilici, 115385
Enzo, Miotti, 115827
Sarai, slavkis, 114351
Matias, Juchani 114756
