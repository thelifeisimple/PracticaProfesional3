---------------Tablas parametrizaciones
CREATE TABLE pais (
	pais_id	INTEGER PRIMARY KEY AUTOINCREMENT,
	pais_nombre	VARCHAR(50) NOT NULL, 
	pais_nacionalidad VARCHAR(50) NOT NULL
);

INSERT INTO main.Pais (pais_id, pais_nombre, pais_nacionalidad) VALUES ('1', 'Argentina','argentina');
INSERT INTO main.Pais (pais_id, pais_nombre, pais_nacionalidad) VALUES ('2', 'Bolivia','boliviana');
INSERT INTO main.Pais (pais_id, pais_nombre, pais_nacionalidad) VALUES ('3', 'Brasil','brasilera');
INSERT INTO main.Pais (pais_id, pais_nombre, pais_nacionalidad) VALUES ('4', 'Chile','chilena');
INSERT INTO main.Pais (pais_id, pais_nombre, pais_nacionalidad) VALUES ('5', 'Colombia','colombiana');
INSERT INTO main.Pais (pais_id, pais_nombre, pais_nacionalidad) VALUES ('6', 'Ecuador','ecuatoriana');
INSERT INTO main.Pais (pais_id, pais_nombre, pais_nacionalidad) VALUES ('7', 'Mexico','mexicana');
INSERT INTO main.Pais (pais_id, pais_nombre, pais_nacionalidad) VALUES ('8', 'Paraguay','paraguaya');
INSERT INTO main.Pais (pais_id, pais_nombre, pais_nacionalidad) VALUES ('9', 'Uruguay','uruguaya');
INSERT INTO main.Pais (pais_id, pais_nombre, pais_nacionalidad) VALUES ('10', 'Venezuela','venezolana');


CREATE TABLE ciudad (
	ciud_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	ciud_nombre VARCHAR(250) NOT NULL, 
	ciud_pais_id INTEGER NOT NULL,
	FOREIGN KEY(ciud_pais_id) REFERENCES Pais(pais_id)
);



CREATE TABLE nodo (
	nodo_id	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	nodo_nombre	VARCHAR(50) NOT NULL,
	nodo_ciud_id	INTEGER NOT NULL,
	nodo_fecha_alta	DATETIME NOT NULL,
	FOREIGN KEY(nodo_ciud_id) REFERENCES Ciudad(ciud_id)
);

INSERT INTO main.Pais (pais_id, pais_nombre, pais_nacionalidad) VALUES ('1', 'Argentina','argentina');
INSERT INTO main.Pais (pais_id, pais_nombre, pais_nacionalidad) VALUES ('2', 'Bolivia','boliviana');
INSERT INTO main.Pais (pais_id, pais_nombre, pais_nacionalidad) VALUES ('3', 'Brasil','brasilera');
INSERT INTO main.Pais (pais_id, pais_nombre, pais_nacionalidad) VALUES ('4', 'Chile','chilena');
INSERT INTO main.Pais (pais_id, pais_nombre, pais_nacionalidad) VALUES ('5', 'Colombia','colombiana');
INSERT INTO main.Pais (pais_id, pais_nombre, pais_nacionalidad) VALUES ('6', 'Ecuador','ecuatoriana');
INSERT INTO main.Pais (pais_id, pais_nombre, pais_nacionalidad) VALUES ('7', 'Mexico','mexicana');
INSERT INTO main.Pais (pais_id, pais_nombre, pais_nacionalidad) VALUES ('8', 'Paraguay','paraguaya');
INSERT INTO main.Pais (pais_id, pais_nombre, pais_nacionalidad) VALUES ('9', 'Uruguay','uruguaya');
INSERT INTO main.Pais (pais_id, pais_nombre, pais_nacionalidad) VALUES ('10', 'Venezuela','venezolana');

 CREATE TABLE rol (
	rol_id	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	rol_nombre	INTEGER NOT NULL,
	rol_estado	Boolean NOT NULL DEFAULT 1
)
---------------Tablas Sistema
CREATE TABLE profesor (
	prof_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	prof_dni INTEGER NOT NULL, 
	prof_nombre VARCHAR(50) NOT NULL, 
	prof_direccion    VARCHAR(100) NOT NULL, 
	prof_ciud_id	INTEGER NOT NULL,
	prof_telefono    VARCHAR(20) NOT NULL, 
	prof_email    VARCHAR(50) NOT NULL, 
	prof_twitter VARCHAR(50), 
	prof_instagram VARCHAR(50), 
	prof_linkedin VARCHAR(50), 
	prof_facebook VARCHAR(50),
	FOREIGN KEY(prof_ciud_id) REFERENCES Ciudad(ciud_id)

);

CREATE TABLE curso (
	curs_id INTEGER PRIMARY KEY AUTOINCREMENT,
	curs_nombre INTEGER NOT NULL, 
	curs_anio integer NOT NULL, 
	curs_cuatrimestre INTEGER NOT NULL,
	curs_estado	Boolean DEFAULT 1
);


CREATE TABLE alumno (
	alum_dni	INTEGER PRIMARY KEY AUTOINCREMENT,
	alum_nombre	varchar(50) NOT NULL,
	alum_apellido	varchar(50) NOT NULL,
	alum_fecha_Alta	DATETIME NOT NULL,
	alum_telefono	INTEGER,
	alum_fecha_Nacimiento DATETIME NOT NULL,
	alum_email	varchar(50) NOT NULL,
	alum_nacionalidad_id	integer NOT NULL,
	alum_ciud_residencia_id integer NOT NULL,
	alum_estado	Boolean DEFAULT 1,
	alum_dispositivo	varchar(50) NOT NULL,
	alum_nodo_elegido_id	INTEGER NOT NULL,
	FOREIGN KEY(alum_nacionalidad_id) REFERENCES Pais(pais_id),
	FOREIGN KEY(alum_nodo_elegido_id) REFERENCES Nodo(nodo_id)
	FOREIGN KEY(alum_ciud_residencia_id) REFERENCES Ciudad(ciud_id)
);

CREATE TABLE alumno_estudio (
	ales_id	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	ales_alum_dni	INTEGER NOT NULL,
	ales_nivel_educacion	varchar(50) NOT NULL,
	ales_donde_conoce_Nahual	varchar(50) NOT NULL,
	ales_estudia_actualmente Boolean NOT NULL,
	FOREIGN KEY(ales_alum_dni) REFERENCES alumno(alum_dni)
	);

CREATE TABLE alumno_axperiencia (
	alex_id	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	alex_alum_dni	INTEGER NOT NULL,
	alex_trabaja_actualmente	Boolean NOT NULL,
	alex_trabajo_sistemas	Boolean NOT NULL,
	alex_lugar_trabajo	varchar(50) NOT NULL,
	alex_experiencia_sistemas	varchar(100) NOT NULL,
	alex_lugar_experiencia	varchar(50) NOT NULL,
	alex_motivaciones	TEXT NOT NULL,
	alex_afect_nahual	TEXT NOT NULL,
	alex_interv_Nahual	TEXT NOT NULL,
	FOREIGN KEY(alex_alum_dni) REFERENCES alumno(alum_dni)
);


CREATE TABLE curso_alumno (
	cual_curs_id INTEGER NOT NULL, 
	cual_nodo_id INTEGER NOT NULL, 
	cual_alum_id INTEGER NOT NULL, 
	cual_fecha_alta DATETIME NOT NULL, 
	cual_fecha_firma DATETIME, 
	cual_prof_firma_id INTEGER, 
	cual_nota_final smallint default 0,
	PRIMARY KEY (cual_curs_id, cual_nodo_id, cual_alum_id),
	FOREIGN KEY(cual_alum_id) REFERENCES alumno(alum_dni),
	FOREIGN KEY(cual_curs_id) REFERENCES curso(curs_id),
	FOREIGN KEY(cual_nodo_id) REFERENCES nodo(nodo_id),
	FOREIGN KEY(cual_prof_firma_id) REFERENCES profesor(prof_id)
);


CREATE TABLE curso_nodo (
	cuno_curs_id INTEGER NOT NULL, 
	cuno_nodo_id INTEGER NOT NULL, 
	cuno_pro_id INTEGER NOT NULL, 
	cuno_estado	Boolean DEFAULT 1,
	PRIMARY KEY (cuno_curs_id, cuno_nodo_id)
);


CREATE TABLE usuario (
	usua_id	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	usua_codigo	varchar UNIQUE,
	usua_clave	VARCHAR(250) NOT NULL,
	usua_rol_id	VARCHAR(30) NOT NULL,
	usua_nombre	VARCHAR(50) NOT NULL,
	usua_apellido	varchar,
	usua_email	VARCHAR(50) NOT NULL,
    usua_fecha_nacimiento varchar(16) NOT NULL,
	usua_fecha_alta	DATETIME,
	usua_fecha_ult_ingreso	DATETIME ,
	usua_estado	BOOLEAN NOT NULL,
	usua_residencia_ciud_id	REAL NOT NULL,
	usua_telefono	varchar,
	FOREIGN KEY(usua_rol_id) REFERENCES rol(rol_id)
);


