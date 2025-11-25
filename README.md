# Sistema de Administración de Veteranos de Malvinas

Este proyecto tiene como objetivo desarrollar una aplicación web para la **Asociación de Veteranos de la Guerra de Malvinas “Virgen del Rosario”**, con el fin de gestionar eficientemente los datos de los veteranos mediante un servicio web, accesible tanto para veteranos designados como administradores por la asociación, como para veteranos en general.

---

## 👥 Integrantes

- Agustín Laner 
- Agustín Nahuel Alieni 
- Camila Astrada 
- Daniel Aguero 
- Francisco Barosco 
- Julian Varea 
- Luciano Gonzalez 

---

## 🧠 Descripción del Proyecto

La Asociación necesita administrar un listado de veteranos de guerra, cada uno con una serie de datos personales. Para esto, se requiere un software que permita:

- Cargar información personal de los veteranos.
- Consultar, modificar o eliminar registros.
- Visualizar información específica mediante filtros.

La cantidad **máxima de personas** que se podrá almacenar será **X veteranos**. Toda la información será almacenada y recuperada automáticamente desde la base de datos en cada ejecución.

---

## ✅ Funcionalidades del Sistema

- Insertar los datos de un veterano de guerra.
- Eliminar a un veterano por su DNI.
- Mostrar todos los veteranos registrados.
- Buscar veteranos por apellido.
- Modificar los datos personales de un veterano ingresando su DNI (el DNI no puede modificarse).
- Mostrar datos actualizados luego de la modificación.
- Listar los veteranos fallecidos, mostrando: nombre, apellido, DNI, fecha de fallecimiento y ciudad de residencia.
- Filtrar personas por “fuerza a la que perteneció”.
- Filtrar personas por mes de nacimiento, mostrando:
  - Nombre, apellido, fecha de nacimiento, edad, ciudad de residencia, dirección postal, correo electrónico y si vive o falleció.
- Acceso diferenciado:
  - **Administrador:** carga y gestión completa de datos.
  - **Veterano normal:** acceso restringido a consultas personales.

---

## 💻 Tecnologías utilizadas

- **Frontend**:
  - HTML5
  - CSS3
  - Bootstrap
  - JavaScript

- **Backend**:
  - Python
  - Flask

- **Base de datos**:
  - MySQL

- **Otros**:
  - Figma (bocetos gráficos de interfaz)

---

# Cómo correr el proyecto con Docker

## 1. Instalar Docker y Docker Compose

Asegúrate de tener **Docker** y **Docker Compose** instalados en tu
máquina.

------------------------------------------------------------------------

## 2. Levantar el proyecto

Este comando construye las imágenes y levanta los contenedores en
segundo plano.\
Úsalo cada vez que quieras iniciar la aplicación:

``` bash
sudo docker-compose up -d --build
```

------------------------------------------------------------------------

## 3. Poblar datos geográficos *(solo la primera vez)*

Este comando descarga y carga las **provincias y localidades
argentinas** desde la API del gobierno.\
Solo es necesario ejecutarlo una vez al instalar el proyecto:

``` bash
sudo docker-compose exec web flask db-populate-geo
```

------------------------------------------------------------------------

## 4. Cargar datos iniciales *(solo la primera vez)*

Este comando carga las fuerzas, roles, la agrupación y el usuario
administrador.\
Se usa `--force` para asegurar que se cargue todo incluso si hay datos
parciales:

``` bash
sudo docker-compose exec -T db mysql -u root -pMalvinas2025! --force malvinas_db < db/seed.sql
```

------------------------------------------------------------------------

## 5. Visualizar la página

Abrí tu navegador y andá a:

**http://localhost:5000**

------------------------------------------------------------------------

## 6. Credenciales de Administrador

-   **Email:** `veteranos@virgendelrosario.admin`\
-   **Contraseña:** `veteranos@admin`

------------------------------------------------------------------------

## 7. Parar el proyecto

Cuando termines de trabajar:

``` bash
sudo docker-compose down
```

## 📁 Estructura del Proyecto

```
proyecto-malvinas-unrc-2025/
├── app
│   ├── db.py
│   ├── __init__.py
│   ├── routes.py
│   ├── static
│   │   ├── css
│   │   │   └── styles.css
│   │   ├── img
│   │   │   └── borrar.txt
│   │   └── js
│   │       └── scripts.js
│   └── templates
│       ├── base.html
│       └── start.html
├── config.py
├── documentacion
│   ├── figma-link.txt
│   └── Proyecto Malvinas 2025_DEFINITIVO-1.pdf
├── README.md
├── requirements.txt
└── run.py
```

---

## 🧩 Bocetos visuales del proyecto (Figma)

Podés visualizar los diseños preliminares de la interfaz en el siguiente enlace:  
📌 **[Ver diseño en Figma](https://www.figma.com/design/lnTIY4ccpOcWNXkZkoarZG)**

---

## 📌 Notas finales

Este proyecto fue desarrollado en el marco del **Proyecto de Extensión UNRC 2025**, con el objetivo de aportar una herramienta informática útil, respetuosa y eficiente para la gestión de los veteranos de la Guerra de Malvinas.
