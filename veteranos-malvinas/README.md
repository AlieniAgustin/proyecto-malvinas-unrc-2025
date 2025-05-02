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
  - X (para templates, DEFINIR QUIEN ES X)
  - Figma (bocetos gráficos de interfaz)

---

## 📁 Estructura del Proyecto

```
veteranos-malvinas/
│
├── app/                      # Código principal de la aplicación
│   ├── __init__.py           # Inicialización de la app Flask
│   ├── routes/               # Módulos de rutas
│   │   └── main_routes.py
│   ├── templates/            # Archivos HTML con Jinja2 (motor de plantillas de Flask)
│   │   ├── base.html
│   │   ├── index.html
│   │   └── ...
│   ├── static/               # Recursos estáticos
│   │   ├── css/
│   │   │   └── styles.css
│   │   ├── js/
│   │   │   └── scripts.js
│   │   └── img/
│   ├── models/               # Modelos de datos
│   │   └── veterano.py
│   ├── forms/                # Formularios (opcional)
│   │   └── veterano_form.py
│   └── utils/                # Funciones auxiliares
│       └── db.py
│
├── config.py                 # Configuración general
├── run.py                    # Punto de inicio de la aplicación
├── requirements.txt          # Lista de dependencias
├── .gitignore                # Archivos ignorados por Git
├── README.md                 # Este archivo
├── figma-link.txt           # 🔗 Enlace al boceto gráfico en Moqups
└── documentacion/            # 📄 PDF con requerimientos del proyecto
    └── requerimientos.pdf
```

---

## 🧩 Bocetos visuales del proyecto (Figma)

Podés visualizar los diseños preliminares de la interfaz en el siguiente enlace:  
📌 **[Ver diseño en Figma](https://www.figma.com/design/lnTIY4ccpOcWNXkZkoarZG)**

---

## 📌 Notas finales

Este proyecto fue desarrollado en el marco del **Proyecto de Extensión UNRC 2025**, con el objetivo de aportar una herramienta informática útil, respetuosa y eficiente para la gestión de los veteranos de la Guerra de Malvinas.
