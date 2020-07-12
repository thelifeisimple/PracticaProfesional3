import sys
import db.DateTime
import sqlalchemy
from sqlalchemy import Column, db.Integer, db.String, db.DateTime, Boolean, db.ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
Base = declarative_base()

#Falta oregnizar exactamente los datos en diferentes tabla

   
class Pais (db.Model):
    __tablename__ = 'pais'

    pais_id = db.Column(db.Integer, primary_key=True)
    pais_nombre  = db.Column(db.String, nullable=False)
    pais_nacionalidad  = db.Column(db.String, nullable=False)
    # relaciones


class Ciudad (db.Model):
    __tablename__ = 'ciudad'

    ciud_id = db.Column(db.Integer, primary_key=True)
    ciud_nombre = db.Column(db.String, nullable=False)
    ciud_pais_id = db.Column(db.Integer, db.ForeignKey('pais.pais_id'))
    # relaciones
    pais = relationship('Pais')


class Nodo(db.Model):
    __tablename__ = 'nodo'

    nodo_id = db.Column(db.Integer, primary_key = True)
    nodo_nombre = db.Column(db.String, nullable = False)
    nodo_ciud_id = db.Column(db.Integer, db.ForeignKey('ciudad.ciud_id'))
    nodo_fecha_alta  = db.Column(db.DateTime, nullable = False)
    nodo_estado = db.Column(db.String, nullable = False)
    nodo_fecha_modif = db.Column(db.DateTime, nullable = True)
    nodo_usuario_modif = db.Column(db.String, nullable = True)
    # relaciones
    ciudad = relationship('Ciudad')


class Rol(db.Model):
    __tablename__ = 'rol'

    rol_id = db.Column(db.Integer, primary_key = True)
    rol_nombre =db.Column(db.String, nullable = False)
    rol_estado = db.Column(Boolean, nullable = False)
    # relaciones

class Nivel(db.Model):
    __tablename__ = 'nivel'

    nive_id = db.Column(db.Integer, primary_key = True)
    nive_nombre =db.Column(db.String, nullable = False)
    # relaciones


class Profesor(db.Model):
    __tablename__ = 'profesor'

    prof_id = db.Column(db.Integer, primary_key = True)
    prof_dni = db.Column(db.String, nullable = False)
    prof_nombre = db.Column(db.String, nullable = False)
    prof_apellido = db.Column(db.String, nullable = False)
    prof_estado = db.Column(Boolean, nullable = False)
    prof_direccion =  db.Column(db.String, nullable = False)
    prof_ciud_id =  db.Column(db.Integer, db.ForeignKey('ciudad.ciud_id'))
    prof_telefono =  db.Column(db.String(20), nullable = False)
    prof_email =  db.Column(db.String, nullable = False)
    prof_twitter = db.Column(db.String, nullable = True)
    prof_instagram = db.Column(db.String, nullable = True)
    prof_linkedin = db.Column(db.String, nullable = True)
    prof_facebook = db.Column(db.String, nullable = True)
    prof_estado = db.Column(db.String, nullable = False)
    prof_fecha_alta = db.Column(db.DateTime, nullable = False)
    prof_fecha_modif = db.Column(db.DateTime, nullable = True)
    prof_usuario_modif = db.Column(db.String, nullable = True)
    # relaciones
    ciudad = relationship('Ciudad')

class Curso(db.Model):
    __tablename__ = 'curso'

    curs_id = db.Column(db.Integer, primary_key = True)
    curs_nombre = db.Column(db.String, nullable = False)
    curs_detalle = db.Column(db.String, nullable = False)
    curs_estado = db.Column(db.String, nullable = False)
    # relaciones
  
class Alumno(db.Model):
    __tablename__ = 'alumno'

    alum_id = db.Column(db.Integer, primary_key = True )
    alum_dni = db.Column(db.String, nullable = False )
    alum_nombre= db.Column(db.String, nullable = False)
    alum_apellido= db.Column(db.String, nullable = False)
    alum_email= db.Column(db.String, nullable = False)
    alum_nacionalidad_id = db.Column(db.Integer , db.ForeignKey('pais.pais_id'))
    alum_ciud_residencia_id =db.Column(db.Integer, db.ForeignKey('ciudad.ciud_id'))
    alum_telefono = db.Column(db.Integer, nullable = True)
    alum_fecha_nacimiento = db.Column(db.String, nullable = False)
    alum_nodo_id  = db.Column(db.Integer, db.ForeignKey('nodo.nodo_id'))
    alum_dispositivo = db.Column(db.Integer, nullable = False)
    alum_estado = db.Column(db.String, nullable = False)
    alum_fecha_alta = db.Column(db.DateTime, nullable = False)
    alum_fecha_modif = db.Column(db.DateTime, nullable = True)
    alum_usuario_modif = db.Column(db.String, nullable = True)
    # relaciones
    nodo = relationship('Nodo')
    nacionalidad = relationship('Pais')
    ciudad = relationship('Ciudad')
    experiencia = relationship('Alumno_Experiencia')
    estudio = relationship('Alumno_Estudio')

class Alumno_Experiencia(db.Model):
    __tablename__ = 'alumno_experiencia'
    alex_id = db.Column(db.Integer, primary_key = True)
    alex_alum_id = db.Column(db.Integer, db.ForeignKey('alumno.alum_id'))
    alex_trabajo = db.Column(db.Integer, nullable = False)
    alex_sistemas = db.Column(db.Integer, nullable = False)
    alex_trabajo_lugar = db.Column(db.String, nullable = False)
    alex_sistemas_exp = db.Column(db.Integer, nullable = False)
    alex_sistemas_lugar = db.Column(db.String, nullable = False)
    alex_motivacion = db.Column(db.String, nullable = False)
    alex_afectacion = db.Column(db.String, nullable = False)
    alex_intervencion = db.Column(db.String, nullable = False)
    # relaciones
    alumno = relationship('Alumno')


class Alumno_Estudio(db.Model):

    __tablename__ = 'alumno_estudio'
    ales_id = db.Column(db.Integer, primary_key = True)
    ales_alum_id = db.Column(db.Integer, db.ForeignKey('alumno.alum_id'))
    ales_nivel_educacion_id = db.Column(db.Integer, db.ForeignKey('nivel.nive_id'))
    ales_nahual = db.Column(db.String, nullable = False)
    ales_estudia = db.Column(db.Integer, nullable = False)
    # relaciones
    alumno = relationship('Alumno')
    nivel = relationship('Nivel')





class Curso_Alumno(db.Model):
    __tablename__ = 'curso_alumno'

    cual_id = db.Column(db.Integer, primary_key = True)
    cual_cuno_id = db.Column(db.Integer, db.ForeignKey('curso_nodo.cuno_id'))
    # cual_nodo_id = db.Column(db.Integer, db.ForeignKey('nodo.nodo_id'))
    cual_alum_id = db.Column(db.Integer, db.ForeignKey('alumno.alum_id'))
    cual_estado = db.Column(db.String, nullable = False)
    cual_fecha_alta = db.Column(db.DateTime, nullable = False)
    cual_fecha_firma = db.Column(db.DateTime, nullable = True)
    cual_prof_firma_id = db.Column(db.Integer, db.ForeignKey('profesor.prof_id'))
    cual_nota_final = db.Column(db.Integer, nullable = False)    
    # relaciones
    cursoNodo = relationship('Curso_Nodo')
    alumno = relationship('Alumno')
    profesor = relationship('Profesor')

    
class Curso_Nodo (db.Model):
    __tablename__ = 'curso_nodo'

    cuno_id = db.Column(db.Integer, primary_key = True)
    cuno_curs_id = db.Column(db.Integer, db.ForeignKey('curso.curs_id'))
    cuno_nodo_id = db.Column(db.Integer, db.ForeignKey('nodo.nodo_id'))
    cuno_prof_id = db.Column(db.Integer, db.ForeignKey('profesor.prof_id'))
    cuno_estado = db.Column(db.String, nullable = False)
    cuno_anio = db.Column(db.Integer, nullable = False)
    cuno_cuatrimestre = db.Column(db.Integer, nullable = False)
    # relaciones
    curso = relationship('Curso')
    nodo = relationship('Nodo')
    profesor = relationship('Profesor')

    
class Usuario(db.Model):
    __tablename__ = 'usuario'

    usua_id = db.Column(db.Integer, primary_key = True)
    usua_codigo = db.Column(db.String, nullable = False)
    usua_nombre = db.Column(db.String, nullable = False)
    usua_apellido = db.Column(db.String, nullable = False)
    usua_clave = db.Column(db.String, nullable = False)
    usua_rol_id = db.Column(db.Integer, db.ForeignKey('rol.rol_id'))
    usua_email = db.Column(db.String, nullable = False)
    usua_telefono = db.Column(db.String, nullable = False)
    usua_fecha_nacimiento = db.Column(db.String, nullable = False)
    usua_fecha_alta = db.Column(db.DateTime, nullable = False)
    usua_fecha_ult_ingreso = db.Column(db.DateTime, nullable = False)
    usua_estado  = db.Column(db.String, nullable = False)
    usua_residencia_ciud_id = db.Column(db.Integer, db.ForeignKey('ciudad.ciud_id'))
    # relaciones
    rol = relationship('Rol')
    ciudad = relationship('Ciudad')

engine = sqlalchemy.create_engine('sqlite:///inscripciones_nahual.db')
Base.metadata.create_all(engine)        