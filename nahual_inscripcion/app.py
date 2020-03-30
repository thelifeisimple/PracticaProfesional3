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

@app.route('/login', methods= ['GET', 'POST'] )
def login():

    if request.method == 'GET':
        state = ''.join(random.choice(
                string.ascii_uppercase + string.digits) for x in range(50))
        #store it in session for later use
        login_session['state'] = state
        return render_template('login.html', STATE = state)
    else:
        if request.method == 'POST':
            print("Dentro del POST login")

            user = session.query(user).filter_by(
                username = request.form['username'],
                password = request.form['password']).first()

        if not user:
            error = "Usuario no registrado"
            return render_template('login.html', error = error)
        else:
            print ("Dentro del user")
            login_session['username'] = request.form['username']
            return render_template('admin.htm', username = login_session['username'])


def login_required(f):
    @wraps(f)
    def decorated_funtion(*args, **kwargs):
        if 'username' not in login_session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_funtion

def make_salt():
    return ''.join(random.choice(
        string.ascii_uppercase + string.digits) for x in range(50))

def make_pw_hash(name, pw, salt = None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256((name + pw + salt).encode('utf-8')).hexdigest()
    return '%s,%s' % (salt, h)

def valid_pw(name, password, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(name,password,salt)


@app.route('/logout')
def logout():
    
    del login_session ['username']

    return render_template('pagPrincipalNahual.htm')

#Inicio de instcripcion al curso
@app.route('/inscripcion', methods=['GET','POST'])
def inscripcion():

    print ("inside GET")
    
    if request.method == 'GET':
        return render_template('formulario1.htm')
        
    else:
        print ("inside Post")

        if request.method == 'POST':

            nuevoAlumno = Alumno(
            nombre = request.form['nombre'],
            apellido = request.form['apellido'],
            email = request.form['email'],
            dni = request.form['dni'],
            fecha_nac = request.form['fecha_nac'],
            nacionalidad = request.form['nacionalidad'],
            telefono = request.form['telefono'],
            residencia = request.form['residencia'],
            otro = request.form['otro'],
            nombre_nodo = request.form['nombre_nodo'],
            trabaja_actualmente = request.form['trabaja_actualmente'],
            donde_trabaja = request.form['donde_trabaja'])
            session.add(nuevoAlumno)
            session.commit()

            return redirect(url_for('formulario2.htm'))

@app.route('/inscripcionII', methods=['GET','POST'])
def inscripcionII():
    
    if request.method == 'GET':
        return render_template('formulario1.htm')
    else:

        if request.method == 'POST':

            nuevoAlumno2 = Alumno (
            dispositivo = request.form['dispositivo'],
            experiencia_sistemas = request.form['experiencia_sistemas'],
            lugar_experiencia = request.form['lugar_experiencia'],
            trabajo_sistemas = request.form['trabajo_sistemas'],
            nivel_educacion = request.form['nivel_educacion'],
            donde_conoce_Nahual = request.form['donde_conoce_Nahual'])
            session.add(nuevoAlumno2)
            session.commit()

            nuevoAlumnoEstudio = Estudio (
            nivel_educacion = request.form['nivel_educacion'],
            donde_conoce_Nahual = request.form['donde_conoce_Nahual'])
            session.add(nuevoAlumnoEstudio)
            session.commit()

            return redirect(url_for('formulario2.htm'))


@app.route('/inscripcionIII', methods=['GET','POST'])
def inscripcionIII():
    
    if request.method == 'GET':
        return render_template('formulario3.htm')
    else:
        if request.method == 'POST':

            nuevoAlumno3 = Alumno (
            motivaciones = request.form['motivaciones'],
            afect_nahual = request.form['afect_nahual'],
            interv_Nahual = request.form['interv_Nahual'])
            session.add(nuevoAlumno3)
            session.commit()

            return redirect(url_for('formulario3.htm'))


# Crear usuario
@app.route('/registrar', methods=['GET','POST'])
def registrar():

    if request.method == 'GET':
        return render_template('addUser.htm')
    else:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']

            pw_hash = make_pw_hash(username, password)
            nuevoUsuario = User(
                username = username,
                email = email,
                pw_hash = pw_hash)
            session.add(nuevoUsuario)
            session.commit()
            login_session ['username'] = request.form['username']
            return redirect(url_for('showMain'))

# Borrar User
@app.route('/inscripciones/eliminar/<int:id>', methods =['GET', 'POST'])
def eliminarUser(id):

    post =session.query(User).filer_by(id=id).one()

    if request.method == 'GET':
        return render_template('addLow.htm', post = post)
    else:
        if request.method == 'POST':
            session.delete(post)  
            session.commmit()
            return redirect(url_for('ShowMain'))

# Crear Nodo
@app.route('/agregarNodo', methods=['GET','POST'])
def agregarNodo():

    if request.method == 'GET':
        return render_template('addNode.htm')
    else:
        if request.method == 'POST':
            post = Nodo (
                nodoname = request.form['nodoname'],
                dateCreation = datetime.datetime.now())
            session.add(post)
            session.commit()
            return redirect(url_for('showMain'))

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
    
    
