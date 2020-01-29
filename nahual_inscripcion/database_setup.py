import sys
import datetime
import sqlalchemy
from sqlalchemy import Column, Integer, String, DataTime, Boolean #,foreignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationshipsql
from sqlalchemy import creat_engine

Base = declarative_base()

#Falta oregnizar exactamente los datos en diferentes tabla


class Cursos_Relacional(Base):
    __tablename__ = 'cursosRelacional'

    id_curso = Column(Integer, primary_key = True)
    id_alumna = Column(Integer, primary_key = True)
    #fecha_inscripcion

class Curso(Base):
    __tablename__ = 'curso'

    id_curso = Column(Integer, primary_key = True)
    name_curso = Column(Integer, nullable = False)
    anio = Column(DataTime, nullable = False)
    cuatrimestre = Column(Integer, nullable = False)

class Lugares (Base):
    __tablename__ = 'lugares'

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
    fecha_creacion = Column(DataTime, nullable = False)
    fecha_ultimo_ingreso = Column(DataTime, nullable = False)
    state_user = Column(Boolean, nullable = False)

class 

class TablaRelacional(Base):
    __tablename__ = 'tablaRelacion'

    id_nodo = Column(Integer, primary_key = True)
    id_curso = Column(Integer, primary_key = True)
    id_profe = Column(Integer, primary_key = True)

class Nodo(Base):
    __tablename__ = 'nodos'

    id_nodo = Column(Integer, primary_key = True)
    id_pais = Column(Integer, nullable = False)
    nodoname =Column(String(50), nullable = False)
    dateCreation = Column(DataTime, nullable = False)

class Estudio(Base):

    __tablename__ = ''

class Profesores(Base):
    __tablename__ = 'profesores'

    id_profesor = Column(Integer, primary_key = True)
    nombre_profesor = Column(String(50), nullable = False)

engine = sqlalchemy.create_engine('sqlite:///data/inscripciones.db')
Base.metadata.create_all(engine)        