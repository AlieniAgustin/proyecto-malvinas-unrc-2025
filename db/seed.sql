USE malvinas_db;

-- FUERZAS
INSERT INTO fuerza (nombre) VALUES 
('Ejercito'), 
('Fuerza Aerea'), 
('Gendarmeria'), 
('Armada'),
('Prefectura');

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
('En combate'),
('Luego del conflicto'),
('Natural');

-- AGRUPACIÓN (Usa la localidad 14098230: Rio Cuarto)
INSERT INTO agrupacion(id_agrupacion, nombre_agrupacion, direccion, mail, localidad_agrupacion) VALUES
(1, "Agrupacion Veteranos de Guerra de Malvinas 'Operativo Virgen del Rosario'", "Luis Pasteur 260", "vdeguerrademalvinasrioiv@gmail.com", '14098230'); -- El ID 14098230 es el de Río Cuarto en la API Georef

-- DATOS DE LA AGRUPACIÓN
INSERT INTO telefono_agrupacion(id_agrupacion, telefono) VALUES
(1, "0358 465-1234");

INSERT INTO red_social(nombre, link, id_agrupacion) VALUES
('Facebook', 'https://www.facebook.com/avgmalvinasrioiv/', 1),
('Instagram', 'https://www.instagram.com/vgmovirgendelrosariorioiv/', 1);

-- ADMINISTRADOR (Usa la agrupacion 1)
INSERT INTO administrador(agrupacion, email, psswd) VALUES
(1, "vdeguerrademalvinasrioiv@gmail.com", "prueba123"); -- contraseña en texto plano para facilitar pruebas;