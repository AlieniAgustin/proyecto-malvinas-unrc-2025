USE malvinas_db;

-- FUERZAS
-- IDs: 1:Ejercito, 2:Fuerza Aerea, 3:Gendarmeria, 4:Marina
INSERT INTO fuerza (nombre) VALUES 
('Ejercito'), 
('Fuerza Aerea'), 
('Gendarmeria'), 
('Marina');

-- ROLES PARA AUTORIDADES
-- IDs: 1:Presidente, 2:Vicepresidente, etc.
INSERT INTO rol (nombre_rol) VALUES
('Presidente'),
('Vicepresidente'),
('Secretario'),
('Tesorero'),
('Secretario de Prensa'),
('Secretario de Obra Social'),
('Vocal Titular'),
('Vocal Suplente');

-- CAUSAS DE FALLECIMIENTO
-- IDs: 1:en combate, 2:post combate, 3:natural
INSERT INTO causa_fallecimiento (descripcion) VALUES
('en combate'),
('post combate'),
('natural');

-- LOCALIDADES 
-- IDs Provincias: 1:Buenos Aires, 5:Córdoba, 20:Santa Fe, 12:Mendoza, 22:Tierra del Fuego
INSERT INTO localidad(id_localidad, nombre_localidad, departamento, id_provincia, codigo_postal) VALUES
(1, "Rio Cuarto", "Rio Cuarto", 5, "X5806"),
(2, "La Plata", "La Plata", 1, "B1900"),
(3, "Rosario", "Rosario", 20, "S2000"),
(4, "Mendoza", "Capital", 12, "M5500"),
(5, "Ushuaia", "Ushuaia", 22, "V9410");

-- AGRUPACIÓN (Usa la localidad 1: Rio Cuarto)
INSERT INTO agrupacion(id_agrupacion, nombre_agrupacion, direccion, mail, localidad_agrupacion) VALUES
(1, "Agrupación Veteranos de Guerra de Malvinas 'Operativo Virgen del Rosario'", "Luis Pasteur 260", "vdeguerrademalvinasrioiv@gmail.com", 1);

-- DATOS DE LA AGRUPACIÓN
INSERT INTO telefono_agrupacion(id_agrupacion, telefono) VALUES
(1, "0358 465-1234");

INSERT INTO red_social(nombre, link, id_agrupacion) VALUES
('Facebook', 'https://www.facebook.com/veteranos.rioiv', 1),
('Instagram', 'https://www.instagram.com/veteranos.rioiv', 1);

-- ADMINISTRADOR (Usa la agrupacion 1)
INSERT INTO administrador(agrupacion, email, psswd) VALUES
(1, "veteranos@virgendelrosario.admin", "veteranos@admin");

-- -----------------------------------------------------
-- Creación de Personas y Veteranos para pruebas
-- -----------------------------------------------------

-- Se crean 5 personas que luego serán veteranos
INSERT INTO persona (dni, nombre, apellido, genero) VALUES
('14111222', 'Juan Carlos', 'Pérez', 'masculino'),       -- Veterano completo y vivo
('15333444', 'Carlos Alberto', 'Gómez', 'masculino'),   -- Veterano de otra fuerza y provincia
('16555666', 'Luis María', 'Fernández', 'masculino'),   -- Veterano que estará fallecido
('17777888', 'Miguel Ángel', 'Torres', 'masculino'),    -- Veterano con DATOS INCOMPLETOS
('18999000', 'Roberto', 'Díaz', 'masculino');         -- Veterano que reside en otro lugar

-- Ahora se crean los registros de VETERANO, vinculando a las personas y añadiendo datos específicos
INSERT INTO veterano (dni_veterano, fecha_nacimiento, localidad_nacimiento, localidad_residencia, id_agrupacion, id_fuerza) VALUES
-- Juan Pérez: Nació y vive en Río Cuarto (Córdoba). Del Ejército.
('14111222', '1962-05-10', 1, 1, 1, 1),
-- Carlos Gómez: Nació en La Plata (BsAs), vive allí. De Fuerza Aérea.
('15333444', '1963-08-22', 2, 2, 1, 2),
-- Luis Fernández: Nació en Rosario (Santa Fe). De la Marina.
('16555666', '1960-11-03', 3, 3, 1, 4),
-- Miguel Torres: Nació en Mendoza. DATOS INCOMPLETOS A PROPÓSITO (fuerza y fecha_nacimiento son NULL).
('17777888', NULL, 4, 4, 1, NULL),
-- Roberto Díaz: Nació en Ushuaia (Tierra del Fuego) pero RESIDE en Río Cuarto. De Gendarmería.
('18999000', '1961-02-15', 5, 1, 1, 3);

-- -----------------------------------------------------
-- Tablas que dependen de la existencia de Veteranos
-- -----------------------------------------------------

-- REGISTRO DE FALLECIDO
-- Se registra a Luis Fernández como fallecido
INSERT INTO fallecido (dni_veterano, fecha_fallecimiento, id_causa) VALUES
('16555666', '2010-06-18', 2); -- Causa 2: post combate

-- AUTORIDADES DE LA AGRUPACIÓN
-- Se asignan roles a dos de los veteranos vivos
INSERT INTO autoridad (dni_autoridad, id_rol) VALUES
('14111222', 1), -- Juan Pérez es Presidente (Rol ID 1)
('15333444', 2); -- Carlos Gómez es Vicepresidente (Rol ID 2)
