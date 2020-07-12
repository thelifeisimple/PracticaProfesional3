import sys
import datetime
import sqlalchemy
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine



Base = declarative_base()

#Falta oregnizar exactamente los datos en diferentes tabla

   
class Pais (Base):
    __tablename__ = 'pais'

    pais_id = Column(Integer, primary_key=True)
    pais_nombre  = Column(String(50), nullable=False)
    pais_nacionalidad  = Column(String(50), nullable=False)


class Ciudad (Base):
    __tablename__ = 'ciudad'

    ciud_id = Column(Integer, primary_key=True)
    ciud_nombre = Column(String(50), nullable=False)
    ciud_pais_id = Column(Integer, ForeignKey('pais.pais_id'))
    # relaciones
    pais = relationship('Pais')


class Nodo(Base):
    __tablename__ = 'nodo'

    nodo_id = Column(Integer, primary_key = True)
    nodo_nombre = Column(String(50), nullable = False)
    nodo_ciud_id = Column(Integer, ForeignKey('ciudad.ciud_id'))
    nodo_fecha_alta  = Column(DateTime, nullable = False)
    nodo_estado = Column(String, nullable = False)
    nodo_fecha_modif = Column(DateTime, nullable = True)
    nodo_usuario_modif = Column(String, nullable = True)
    # relaciones
    ciudad = relationship('Ciudad')


class Rol(Base):
    __tablename__ = 'rol'

    rol_id = Column(Integer, primary_key = True)
    rol_nombre =Column(String(50), nullable = False)
    rol_estado = Column(Boolean, nullable = False)

class Nivel(Base):
    __tablename__ = 'nivel'

    nive_id = Column(Integer, primary_key = True)
    nive_nombre =Column(String(50), nullable = False)


class Profesor(Base):
    __tablename__ = 'profesor'

    prof_id = Column(Integer, primary_key = True)
    prof_dni = Column(String, nullable = False)
    prof_nombre = Column(String(50), nullable = False)
    prof_apellido = Column(String(50), nullable = False)
    prof_estado = Column(Boolean, nullable = False)
    prof_direccion =  Column(String(50), nullable = False)
    prof_ciud_id =  Column(Integer, ForeignKey('ciudad.ciud_id'))
    prof_telefono =  Column(String(20), nullable = False)
    prof_email =  Column(String(50), nullable = False)
    prof_twitter = Column(String(50), nullable = True)
    prof_instagram = Column(String(50), nullable = True)
    prof_linkedin = Column(String(50), nullable = True)
    prof_facebook = Column(String(50), nullable = True)
    prof_estado = Column(String, nullable = False)
    prof_fecha_alta = Column(DateTime, nullable = False)
    prof_fecha_modif = Column(DateTime, nullable = True)
    prof_usuario_modif = Column(String, nullable = True)

    # relaciones
    ciudad = relationship('Ciudad')

class Curso(Base):
    __tablename__ = 'curso'

    curs_id = Column(Integer, primary_key = True)
    curs_nombre = Column(String, nullable = False)
    curs_detalle = Column(String, nullable = False)
    curs_estado = Column(String, nullable = False)
    # relaciones
  
class Alumno(Base):
    __tablename__ = 'alumno'

    alum_id = Column(Integer, primary_key = True )
    alum_dni = Column(String, nullable = False )
    alum_nombre= Column(String, nullable = False)
    alum_apellido= Column(String, nullable = False)
    alum_email= Column(String, nullable = False)
    alum_nacionalidad_id = Column(Integer , ForeignKey('pais.pais_id'))
    alum_ciud_residencia_id =Column(Integer, ForeignKey('ciudad.ciud_id'))
    alum_telefono = Column(Integer, nullable = True)
    alum_fecha_nacimiento = Column(String, nullable = False)
    alum_nodo_id  = Column(Integer, ForeignKey('nodo.nodo_id'))
    alum_dispositivo = Column(Integer, nullable = False)
    alum_estado = Column(String, nullable = False)
    alum_fecha_alta = Column(DateTime, nullable = False)
    alum_fecha_modif = Column(DateTime, nullable = True)
    alum_usuario_modif = Column(String, nullable = True)
    # relaciones
    nodo = relationship('Nodo')
    nacionalidad = relationship('Pais')
    ciudad = relationship('Ciudad')
    experiencia = relationship('Alumno_Experiencia')
    estudio = relationship('Alumno_Estudio')

class Alumno_Experiencia(Base):
    __tablename__ = 'alumno_experiencia'
    alex_id = Column(Integer, primary_key = True)
    alex_alum_id = Column(Integer, ForeignKey('alumno.alum_id'))
    alex_trabajo = Column(Integer, nullable = False)
    alex_sistemas = Column(Integer, nullable = False)
    alex_trabajo_lugar = Column(String, nullable = False)
    alex_sistemas_exp = Column(Integer, nullable = False)
    alex_sistemas_lugar = Column(String, nullable = False)
    alex_motivacion = Column(String, nullable = False)
    alex_afectacion = Column(String, nullable = False)
    alex_intervencion = Column(String, nullable = False)
    # relaciones
    alumno = relationship('Alumno')


class Alumno_Estudio(Base):

    __tablename__ = 'alumno_estudio'
    ales_id = Column(Integer, primary_key = True)
    ales_alum_id = Column(Integer, ForeignKey('alumno.alum_id'))
    ales_nivel_educacion_id = Column(Integer, ForeignKey('nivel.nive_id'))
    ales_nahual = Column(String, nullable = False)
    ales_estudia = Column(Integer, nullable = False)
    # relaciones
    alumno = relationship('Alumno')
    nivel = relationship('Nivel')





class Curso_Alumno(Base):
    __tablename__ = 'curso_alumno'

    cual_id = Column(Integer, primary_key = True)
    cual_cuno_id = Column(Integer, ForeignKey('curso_nodo.cuno_id'))
    # cual_nodo_id = Column(Integer, ForeignKey('nodo.nodo_id'))
    cual_alum_id = Column(Integer, ForeignKey('alumno.alum_id'))
    cual_estado = Column(String, nullable = False)
    cual_fecha_alta = Column(DateTime, nullable = False)
    cual_fecha_firma = Column(DateTime, nullable = True)
    cual_prof_firma_id = Column(Integer, ForeignKey('profesor.prof_id'))
    cual_nota_final = Column(Integer, nullable = False)    
    # relaciones
    # curso = relationship('Curso')
    cursoNodo = relationship('Curso_Nodo')
    alumno = relationship('Alumno')
    profesor = relationship('Profesor')

    
class Curso_Nodo (Base):
    __tablename__ = 'curso_nodo'

    cuno_id = Column(Integer, primary_key = True)
    cuno_curs_id = Column(Integer, ForeignKey('curso.curs_id'))
    cuno_nodo_id = Column(Integer, ForeignKey('nodo.nodo_id'))
    cuno_prof_id = Column(Integer, ForeignKey('profesor.prof_id'))
    cuno_estado = Column(String, nullable = False)
    cuno_anio = Column(Integer, nullable = False)
    cuno_cuatrimestre = Column(Integer, nullable = False)

    # relaciones
    curso = relationship('Curso')
    nodo = relationship('Nodo')
    profesor = relationship('Profesor')

    
class Usuario(Base):
    __tablename__ = 'usuario'

    usua_id = Column(Integer, primary_key = True)
    usua_codigo = Column(String, nullable = False)
    usua_nombre = Column(String, nullable = False)
    usua_apellido = Column(String, nullable = False)
    usua_clave = Column(String, nullable = False)
    usua_rol_id = Column(Integer, ForeignKey('rol.rol_id'))
    usua_email = Column(String, nullable = False)
    usua_telefono = Column(String, nullable = False)
    usua_fecha_nacimiento = Column(String, nullable = False)
    usua_fecha_alta = Column(DateTime, nullable = False)
    usua_fecha_ult_ingreso = Column(DateTime, nullable = False)
    usua_estado  = Column(String, nullable = False)
    usua_residencia_ciud_id = Column(Integer, ForeignKey('ciudad.ciud_id'))
    # relaciones
    rol = relationship('Rol')
    ciudad = relationship('Ciudad')

engine = sqlalchemy.create_engine('sqlite:///inscripciones_nahual.db')
Base.metadata.create_all(engine)        