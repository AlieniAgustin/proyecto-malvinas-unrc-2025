SET sql_mode = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION';
SET FOREIGN_KEY_CHECKS = 0; -- Desactiva la revisión de dependencias

CREATE DATABASE IF NOT EXISTS malvinas_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE malvinas_db;

-- Borra todas las tablas sin importar el orden
DROP TABLE IF EXISTS familiar_veterano;
DROP TABLE IF EXISTS familiar;
DROP TABLE IF EXISTS fallecido;
DROP TABLE IF EXISTS causa_fallecimiento;
DROP TABLE IF EXISTS autoridad;
DROP TABLE IF EXISTS rol;
DROP TABLE IF EXISTS administrador;
DROP TABLE IF EXISTS documento;
DROP TABLE IF EXISTS veterano;
DROP TABLE IF EXISTS grado;
DROP TABLE IF EXISTS telefono_agrupacion;
DROP TABLE IF EXISTS agrupacion;
DROP TABLE IF EXISTS localidad;
DROP TABLE IF EXISTS provincia;
DROP TABLE IF EXISTS fuerza;
DROP TABLE IF EXISTS telefono_persona;
DROP TABLE IF EXISTS persona;
DROP TABLE IF EXISTS red_social;

CREATE TABLE persona(
  dni VARCHAR(8) NOT NULL,
  nombre VARCHAR(50) NOT NULL,
  apellido VARCHAR(50) NOT NULL,
  genero ENUM('masculino','femenino','otro','no especificado') NOT NULL,
  CONSTRAINT pk_persona PRIMARY KEY(dni)
);

CREATE TABLE telefono_persona(
  dni VARCHAR(8) NOT NULL,
  telefono VARCHAR(30) NOT NULL,
  CONSTRAINT pk_telefono_persona PRIMARY KEY(dni,telefono),
  CONSTRAINT fk_telefono_persona FOREIGN KEY(dni) 
    REFERENCES persona(dni) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE fuerza(
  id_fuerza INT AUTO_INCREMENT NOT NULL,
  nombre ENUM ('Ejercito', 'Fuerza Aerea', 'Gendarmeria', 'Armada', 'Prefectura') NOT NULL UNIQUE,
  CONSTRAINT pk_fuerza PRIMARY KEY(id_fuerza)
);

CREATE TABLE provincia(
  id_provincia INT NOT NULL, -- ID de la API Georef
  nombre VARCHAR(100) NOT NULL,
  CONSTRAINT pk_provincia PRIMARY KEY(id_provincia)
);

CREATE TABLE localidad(
  id_localidad VARCHAR(11) NOT NULL, -- ID de la API Georef
  nombre_localidad VARCHAR(100) NOT NULL,
  departamento VARCHAR(100),
  id_provincia INT NOT NULL,
  CONSTRAINT pk_localidad PRIMARY KEY(id_localidad),
  CONSTRAINT fk_provincia FOREIGN KEY(id_provincia)
    REFERENCES provincia(id_provincia)
);

CREATE TABLE agrupacion(
  id_agrupacion INT NOT NULL,
  nombre_agrupacion VARCHAR(100) NOT NULL,
  direccion VARCHAR(255),
  mail VARCHAR(100),
  localidad_agrupacion VARCHAR(11) NOT NULL,
  CONSTRAINT pk_agrupacion PRIMARY KEY(id_agrupacion),
  CONSTRAINT fk_localidad FOREIGN KEY(localidad_agrupacion)
    REFERENCES localidad(id_localidad)
);

CREATE TABLE telefono_agrupacion(
  id_agrupacion INT NOT NULL, 
  telefono VARCHAR(30) NOT NULL, 
    CONSTRAINT pk_telefono_agrupacion PRIMARY KEY (id_agrupacion, telefono),
    CONSTRAINT fk_telefono_agrupacion FOREIGN KEY (id_agrupacion) 
      REFERENCES agrupacion(id_agrupacion)
);

CREATE TABLE grado(
  id_grado INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  id_fuerza INT NOT NULL,
  CONSTRAINT fk_grado_fuerza FOREIGN KEY (id_fuerza)
    REFERENCES fuerza(id_fuerza) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE veterano(
  dni_veterano VARCHAR(8) NOT NULL,
  direccion VARCHAR(255),
  codigo_postal_residencia VARCHAR(20),
  nro_beneficio_nacional VARCHAR(50),
  funcion TEXT,
  secuelas TEXT,
  fecha_nacimiento DATE,
  mail VARCHAR(100),
  localidad_nacimiento VARCHAR(11),
  localidad_residencia VARCHAR(11),
  id_agrupacion INT,
  id_grado INT,
  id_fuerza INT,
  CONSTRAINT pk_veterano PRIMARY KEY(dni_veterano),
  CONSTRAINT uq_veterano_nro_beneficio_nacional UNIQUE(nro_beneficio_nacional),
  CONSTRAINT fk_veterano_persona FOREIGN KEY(dni_veterano)
    REFERENCES persona(dni) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_veterano_localidad_nacimiento FOREIGN KEY(localidad_nacimiento) 
    REFERENCES localidad(id_localidad) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT fk_veterano_localidad_residencia FOREIGN KEY(localidad_residencia) 
    REFERENCES localidad(id_localidad) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT fk_veterano_agrupacion FOREIGN KEY(id_agrupacion) 
    REFERENCES agrupacion(id_agrupacion) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT fk_veterano_grado FOREIGN KEY(id_grado) 
    REFERENCES grado(id_grado) ON DELETE SET NULL ON UPDATE CASCADE, 
  CONSTRAINT fk_veterano_fuerza FOREIGN KEY(id_fuerza) 
    REFERENCES fuerza(id_fuerza) ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE documento(
  id_documento INT AUTO_INCREMENT NOT NULL,
  nombre VARCHAR(255) NOT NULL,
  descripcion TEXT,
  ruta_archivo VARCHAR(255) NOT NULL,
  CONSTRAINT pk_documento PRIMARY KEY(id_documento)
);

CREATE TABLE administrador(
  agrupacion INT NOT NULL,
  email VARCHAR(255) NOT NULL,
    psswd VARCHAR(50) NOT NULL,
    CONSTRAINT pk_administrador PRIMARY KEY(agrupacion),
    CONSTRAINT ck_password_length CHECK(LENGTH(psswd) >= 8),
    CONSTRAINT fk_agrupacion FOREIGN KEY (agrupacion) 
    REFERENCES agrupacion(id_agrupacion) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE rol (
  id_rol INT AUTO_INCREMENT PRIMARY KEY,
  nombre_rol ENUM(
    'Presidente',
    'Vicepresidente',
    'Secretario',
    'Tesorero',
    'Secretario de Prensa',
    'Secretario de Obra Social',
    'Vocal Titular',
    'Vocal Suplente'
  ) NOT NULL UNIQUE
);

CREATE TABLE autoridad (
  dni_autoridad VARCHAR(8) NOT NULL,
  id_rol INT NOT NULL,
  CONSTRAINT pk_autoridad PRIMARY KEY(dni_autoridad),
  CONSTRAINT fk_autoridad_veterano FOREIGN KEY (dni_autoridad)
    REFERENCES veterano(dni_veterano) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_autoridad_rol FOREIGN KEY (id_rol)
    REFERENCES rol(id_rol) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE causa_fallecimiento (
  id_causa INT AUTO_INCREMENT PRIMARY KEY,
  descripcion ENUM(
    'En combate',
    'Luego del conflicto',
    'Natural'
  ) NOT NULL UNIQUE
);

CREATE TABLE fallecido (
  dni_veterano VARCHAR(8) NOT NULL,
  fecha_fallecimiento DATE NOT NULL,
  id_causa INT,
  CONSTRAINT pk_fallecido PRIMARY KEY(dni_veterano),
  CONSTRAINT fk_fallecido_veterano FOREIGN KEY (dni_veterano)
    REFERENCES veterano(dni_veterano) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_fallecido_causa FOREIGN KEY (id_causa)
    REFERENCES causa_fallecimiento(id_causa) ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE familiar(
  dni_familiar VARCHAR(8) NOT NULL,
  CONSTRAINT pk_familiar PRIMARY KEY(dni_familiar),
  CONSTRAINT fk_familiar_persona FOREIGN KEY (dni_familiar)
    REFERENCES persona(dni) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE familiar_veterano(
  dni_familiar VARCHAR(8) NOT NULL,
  dni_veterano VARCHAR(8) NOT NULL,
  CONSTRAINT pk_familiarveterano PRIMARY KEY(dni_familiar,dni_veterano),
  CONSTRAINT fk_familiarveterano_veterano FOREIGN KEY (dni_veterano)
    REFERENCES veterano(dni_veterano) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_familiarveterano_familiar FOREIGN KEY (dni_familiar)
    REFERENCES persona(dni) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE red_social(
  id_red_social INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  link VARCHAR(255) NOT NULL,
  id_agrupacion INT NOT NULL,
  CONSTRAINT fk_red_social_agrupacion FOREIGN KEY (id_agrupacion)
    REFERENCES agrupacion(id_agrupacion) ON DELETE CASCADE ON UPDATE CASCADE
);

SET FOREIGN_KEY_CHECKS = 1; -- Reactiva la revisión de dependencias
