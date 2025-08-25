USE malvinas_db;

INSERT INTO persona VALUES
  ('46332866','Agustin','Alieni','masculino'),
  ('12345678','Julian','Varea','masculino'),
  ('12345679','Lionel','Messi','masculino'),
  ('12345680','Diego','Maradona','masculino'),
  ('12345681','Julian','Conde','masculino');

INSERT INTO telefono_persona VALUES
  ('46332866','+5492664031963'),
  ('46332866','+549358920384'),
  ('12345678','+549358123123');

INSERT INTO localidad(nombre_localidad, departamento, id_provincia, codigo_postal) VALUES
("Rio Cuarto", "Rio Cuarto", 5, "X5806");

INSERT INTO agrupacion(id_agrupacion, nombre_agrupacion, direccion, mail, localidad_agrupacion) VALUES
(1, "Agrupación Veteranos de Guerra de Malvinas 'Operativo Virgen del Rosario'", "Luis Pasteur 260", "vdeguerrademalvinasrioiv@gmail.com",
1);

INSERT INTO administrador(agrupacion, email, psswd) VALUES
(1, "veteranos@virgendelrosario.admin", "veteranos@admin");

