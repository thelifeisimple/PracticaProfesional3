from flask import Flask, g, render_template,jsonify, url_for, flash
from flask import request, redirect, make_response
from flask import session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import (MetaData, Table, Column,
                        Integer, String, Sequence,
                        create_engine,
                        insert)
from functools import wraps
from database_setup import Base, CursoRelacion, Curso, User, Nodo, Lugar, TablaRelacion, Alumno, Estudio, Profesor
import random
import string
import json
import datetime
import hashlib


app = Flask(__name__)

# Connect to Database and create dtabase session
engine = create_engine('sqlite:///inscripciones_nahual.db?check_same_thread=False')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

#Inicio de instcripcion al curso
@app.route('/test', methods=['GET','POST'])
def inscripcion():

    if request.method == 'GET':
        return render_template('test.htm')
    else:
        print ("Inside Post")
        if request.method == 'POST':

            nuevoAlumno = Alumno(
            nombre = request.form['nombre'],
            apellido = request.form['apellido'])
            
            session.add(nuevoAlumno)
            session.commit()

            return render_template('test.htm')

# Mostrar todo
@app.route('/', methods = ['GET'])
def home ():
    return render_template('login.html')

@app.route('/public/', methods = ['GET'])
def showMain():
    #posts = session.query(User).all()
    return render_template('administracion.html')
    #if 'username' in login_session:
    #    username = login_session['username']
    #    return render_template('administracion.html', posts = posts, username = username)
    #else:
        #return render_template('administracion.html', posts = posts)

if __name__ == '__main__':
    
    app.secret_key = 'secret key'
    app.debug = False
    app.run(host = '0.0.0.0', port = 8000, debug=True)
    