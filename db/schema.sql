SET sql_mode = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION';
 
CREATE DATABASE IF NOT EXISTS malvinas_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE malvinas_db;

DROP TABLE IF EXISTS persona;
CREATE TABLE persona(
  dni VARCHAR(8) NOT NULL,
  nombre VARCHAR(50) NOT NULL,
  apellido VARCHAR(50) NOT NULL,
  genero ENUM('masculino','femenino','otro','no especificado') NOT NULL,
  CONSTRAINT pk_persona PRIMARY KEY(dni)
);

DROP TABLE IF EXISTS telefono_persona;
CREATE TABLE telefono_persona(
  dni VARCHAR(8) NOT NULL,
  telefono VARCHAR(30) NOT NULL,
  CONSTRAINT pk_telefono_persona PRIMARY KEY(dni,telefono),
  CONSTRAINT fk_telefono_persona FOREIGN KEY(dni) 
    REFERENCES persona(dni) ON DELETE CASCADE ON UPDATE CASCADE
);

DROP TABLE IF EXISTS fuerza;
CREATE TABLE fuerza(
  id_fuerza INT AUTO_INCREMENT NOT NULL,
  nombre ENUM ('Ejercito', 'Fuerza Aerea', 'Gendarmeria', 'Marina') NOT NULL UNIQUE, -- revisar si eran estas las fuerzas
  CONSTRAINT pk_fuerza PRIMARY KEY(id_fuerza)
);

DROP TABLE IF EXISTS provincia;
CREATE TABLE provincia(
  id_provincia INT AUTO_INCREMENT NOT NULL,
  nombre VARCHAR(100) NOT NULL,
  CONSTRAINT pk_provincia PRIMARY KEY(id_provincia),
  CONSTRAINT uq_provincia_nombre UNIQUE(nombre)
);

INSERT INTO provincia (nombre) VALUES
('Buenos Aires'), ('Catamarca'), ('Chaco'), ('Chubut'), ('Córdoba'), 
('Corrientes'), ('Entre Ríos'), ('Formosa'), ('Jujuy'), ('La Pampa'), 
('La Rioja'), ('Mendoza'), ('Misiones'), ('Neuquén'), ('Río Negro'), 
('Salta'), ('San Juan'), ('San Luis'), ('Santa Cruz'), ('Santa Fe'), 
('Santiago del Estero'), ('Tierra del Fuego'), ('Tucumán'), 
('Ciudad Autónoma de Buenos Aires');

DROP TABLE IF EXISTS localidad;
CREATE TABLE localidad(
  id_localidad INT AUTO_INCREMENT NOT NULL,
  nombre_localidad VARCHAR(100) NOT NULL,
  departamento VARCHAR(100),
  id_provincia INT NOT NULL,
  codigo_postal VARCHAR(20),
  CONSTRAINT pk_localidad PRIMARY KEY(id_localidad),
  CONSTRAINT fk_provincia FOREIGN KEY(id_provincia)
    REFERENCES provincia(id_provincia)
);

DROP TABLE IF EXISTS agrupacion;
CREATE TABLE agrupacion(
  id_agrupacion INT NOT NULL,
  nombre_agrupacion VARCHAR(100) NOT NULL,
  direccion VARCHAR(255),
  mail VARCHAR(100),
  localidad_agrupacion INT NOT NULL,
  CONSTRAINT pk_agrupacion PRIMARY KEY(id_agrupacion),
  CONSTRAINT fk_localidad FOREIGN KEY(localidad_agrupacion)
    REFERENCES localidad(id_localidad)
);

DROP TABLE IF EXISTS grado;
CREATE TABLE grado(
  id_grado INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  id_fuerza INT NOT NULL,
  CONSTRAINT fk_grado_fuerza FOREIGN KEY (id_fuerza)
    REFERENCES fuerza(id_fuerza) ON DELETE CASCADE ON UPDATE CASCADE
);

DROP TABLE IF EXISTS veterano;
CREATE TABLE veterano(
  dni_veterano VARCHAR(8) NOT NULL,
  direccion VARCHAR(255),
  nro_beneficio_nacional VARCHAR(50),
  funcion VARCHAR(100),
  secuelas TEXT,
  fecha_nacimiento DATE,
  mail VARCHAR(100),
  localidad_nacimiento INT,
  localidad_residencia INT,
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

DROP TABLE IF EXISTS documento;
CREATE TABLE documento(
  id_documento INT AUTO_INCREMENT NOT NULL,
  nombre VARCHAR(255) NOT NULL,
  descripcion TEXT,
  ruta_archivo VARCHAR(255) NOT NULL,
  CONSTRAINT pk_documento PRIMARY KEY(id_documento)
);

INSERT INTO documento (nombre, descripcion, ruta_archivo) VALUES
('Prueba de PDF', 'Documento para probar como se ve el PDF', 'static/docs/der.png');

DROP TABLE IF EXISTS administrador;
CREATE TABLE administrador(
	agrupacion INT NOT NULL,
	email VARCHAR(255) NOT NULL,
    psswd VARCHAR(50) NOT NULL,
    CONSTRAINT pk_administrador PRIMARY KEY(agrupacion),
    CONSTRAINT ck_password_length CHECK(LENGTH(psswd) >= 8),
    CONSTRAINT fk_agrupacion FOREIGN KEY (agrupacion) 
		REFERENCES agrupacion(id_agrupacion) ON DELETE CASCADE ON UPDATE CASCADE
);

DROP TABLE IF EXISTS foto;
CREATE TABLE foto(
  id_foto INT AUTO_INCREMENT PRIMARY KEY,
  dni_veterano VARCHAR(8) NOT NULL,
  ruta_foto VARCHAR(255) NOT NULL,
  CONSTRAINT fk_dni_veterano FOREIGN KEY (dni_veterano)
    REFERENCES veterano(dni_veterano) ON DELETE CASCADE ON UPDATE CASCADE
);

DROP TABLE IF EXISTS rol;
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

DROP TABLE IF EXISTS autoridad;
CREATE TABLE autoridad (
  dni_autoridad VARCHAR(8) NOT NULL,
  id_rol INT NOT NULL,
  CONSTRAINT pk_autoridad PRIMARY KEY(dni_autoridad),
  CONSTRAINT fk_autoridad_veterano FOREIGN KEY (dni_autoridad)
    REFERENCES veterano(dni_veterano) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_autoridad_rol FOREIGN KEY (id_rol)
    REFERENCES rol(id_rol) ON DELETE CASCADE ON UPDATE CASCADE
);

DROP TABLE IF EXISTS causa_fallecimiento;
CREATE TABLE causa_fallecimiento (
  id_causa INT AUTO_INCREMENT PRIMARY KEY,
  descripcion ENUM(
    'en combate',
    'post combate',
    'natural'
  ) NOT NULL UNIQUE
);

DROP TABLE IF EXISTS fallecido;
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

DROP TABLE IF EXISTS familiar;
CREATE TABLE familiar(
  dni_familiar VARCHAR(8) NOT NULL,
  CONSTRAINT pk_familiar PRIMARY KEY(dni_familiar),
  CONSTRAINT fk_familiar_persona FOREIGN KEY (dni_familiar)
    REFERENCES persona(dni) ON DELETE CASCADE ON UPDATE CASCADE
);

DROP TABLE IF EXISTS familiarveterano;
CREATE TABLE familiarveterano(
  dni_familiar VARCHAR(8) NOT NULL,
  dni_veterano VARCHAR(8) NOT NULL,
  CONSTRAINT pk_familiarveterano PRIMARY KEY(dni_familiar,dni_veterano),
  CONSTRAINT fk_familiarveterano_veterano FOREIGN KEY (dni_veterano)
    REFERENCES veterano(dni_veterano) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_familiarveterano_familiar FOREIGN KEY (dni_familiar)
    REFERENCES persona(dni) ON DELETE CASCADE ON UPDATE CASCADE
);

DROP TABLE IF EXISTS redsocial;
CREATE TABLE redsocial(
  id_red_social INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  link VARCHAR(255) NOT NULL,
  id_agrupacion INT NOT NULL,
  CONSTRAINT fk_red_social_agrupacion FOREIGN KEY (id_agrupacion)
    REFERENCES agrupacion(id_agrupacion) ON DELETE CASCADE ON UPDATE CASCADE
);


