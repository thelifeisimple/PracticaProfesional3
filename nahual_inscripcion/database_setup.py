import sys
import datetime
import sqlalchemy
from sqlalchemy import Column, Integer, String, DateTime, Boolean ,foreignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

#Falta oregnizar exactamente los datos en diferentes tabla


class CursoRelacion(Base):
    __tablename__ = 'cursoRelacion'

    id_curso = Column(Integer, primary_key = True)
    id_alumna = Column(Integer, primary_key = True)
    #fecha_inscripcion

class Curso(Base):
    __tablename__ = 'curso'

    id_curso = Column(Integer, primary_key = True)
    name_curso = Column(Integer, nullable = False)
    anio = Column(DateTime, nullable = False)
    cuatrimestre = Column(Integer, nullable = False)

class Lugar (Base):
    __tablename__ = 'lugar'

    id_ciudad = Column(Integer, primary_key=True)
    name_ciudad = Column(String(250), nullable=False)
    id_pais = Column(Integer, nullable = False)
    name_pais = Column(String(250), nullable=False)
    
class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key = True)
    username = Column(String(50), nullable = False)
    password = Column(String(250), nullable = False)
    roll = Column(String(250), nullable = False)
    fecha_creacion = Column(DateTime, nullable = False)
    fecha_ultimo_ingreso = Column(DateTime, nullable = False)
    state_user = Column(Boolean, nullable = False)
    id_ciudad = Column(Integer, foreign_key=True)


class TablaRelacion(Base):
    __tablename__ = 'tablaRelacion'

    id_nodo = Column(Integer, primary_key = True)
    id_curso = Column(Integer, primary_key = True)
    id_profe = Column(Integer, primary_key = True)

class Nodo(Base):
    __tablename__ = 'nodos'

    id_nodo = Column(Integer, primary_key = True)
    id_pais = Column(Integer, nullable = False)
    nodoname =Column(String(50), nullable = False)
    dateCreation = Column(DateTime, nullable = False)

class Alumno(Base):
    __tablename__ = 'alumno'

    dni = Column(Integer, primary_key = True)
    nombre= Column(String, nullable = False)
    apellido= Column(String, nullable = False)
    nombre_nodo =Column(String(50), nullable = False)
    fecha_Alta = Column(DateTime, nullable = False)
    telefono = Column(Integer, nullable = True)
    fecha_nac = Column(DateTime, nullable = False)
    estado = Column(Boolean, nullable = False)
    trabaja_actualmente = Column(Boolean, nullable = False)
    trabajo_sistemas = Column(Boolean, nullable = False)
    lugar_trabajo = Column(String, nullable = False)
    experiencia_sistemas = Column(Boolean, nullable = False)
    lugar_experiencia = Column(String, nullable = False)
    id_estudio = Column(Integer, foreign_key = True)
    dispositivo = Column(Boolean, nullable = False)
    motivaciones = Column(String, nullable = False)
    afect_nahual = Column(String, nullable = False)
    interv_Nahual = Column(String, nullable = False)

class Estudio(Base):

    __tablename__ = 'estudio'
    id_estudio = Column(Integer, primary_key = True)
    nivel_educacion = Column(String, nullable = False)
    dni = Column(Integer, foreign_key = True)
    donde_conoce_Nahual = Column(Boolean, nullable = False)

class Profesor(Base):
    __tablename__ = 'profesor'

    id_profesor = Column(Integer, primary_key = True)
    nombre_profesor = Column(String(50), nullable = False)

engine = sqlalchemy.create_engine('sqlite:///inscripciones_nahual.db')
Base.metadata.create_all(engine)        