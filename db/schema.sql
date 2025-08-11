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


