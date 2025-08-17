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
  id_agrupacion INT AUTO_INCREMENT NOT NULL,
  nombre_agrupacion VARCHAR(100) NOT NULL,
  direccion VARCHAR(255),
  mail VARCHAR(100),
  localidad_agrupacion INT NOT NULL,
  CONSTRAINT pk_agrupacion PRIMARY KEY(id_agrupacion),
  CONSTRAINT fk_localidad FOREIGN KEY(localidad_agrupacion)
    REFERENCES localidad(id_localidad)
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
  -- id_grado INT, DESCOMENTAR CUANDO ESTE LA TABLA GRADO
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
  --CONSTRAINT fk_veterano_grado FOREIGN KEY(id_grado) 
    --REFERENCES grado(id_grado) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT fk_veterano_fuerza FOREIGN KEY(id_fuerza) 
    REFERENCES fuerza(id_fuerza) ON DELETE SET NULL ON UPDATE CASCADE
);

