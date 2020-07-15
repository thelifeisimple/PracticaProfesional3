from flask import Flask, g, render_template,jsonify, url_for, flash
from flask import request, redirect, make_response
from flask import session as login_session
from wtforms import Form, BooleanField, StringField, PasswordField, validators
#from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import (MetaData, Table, Column, Integer, String, Sequence, create_engine, insert, ForeignKey)
from functools import wraps
from database_setup import Base, Curso, Curso_Alumno, Nivel, Nodo, Curso_Nodo, Usuario, Pais, Ciudad, Alumno, Alumno_Experiencia, Alumno_Estudio, Profesor, Rol
from datetime import timedelta
import random
import string
import json
import datetime
import hashlib
import sys
#import os

app = Flask(__name__)
#nuevo
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///inscripciones_nahual.db?check_same_thread=False' #os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])  #(os.getenv("DATABASE_URL"))
DBSession = sessionmaker(bind=engine)
session = DBSession()
# session.init_app(app)

# viejo
# Connect to Database and create dtabase session
# engine = create_engine('sqlite:///inscripciones_nahual.db?check_same_thread=False')
# Base.metadata.bind = engine

# DBSession = sessionmaker(bind=engine)
# session = DBSession()

@app.before_request
def before_request():
    now = datetime.datetime.now()

    try:
        last_active = login_session['last_active']
        delta = now - last_active
        if delta.seconds > 1800:
            login_session['last_active'] = now
            del login_session ['sesion-usuario'] 
            # return logout('Tu sesion ha expirado despues de 30 minutos. Debes loguearte de nuevo')
            return render_template('login.htm', msg = 'Tu sesion ha expirado.')
    except:
        try:
            login_session['last_active'] = now
        except:
            pass

@app.route('/login', methods= ['GET', 'POST'] )
def login():

    if 'sesion-usuario' not in login_session:

        if request.method == 'GET':
            state = ''.join(random.choice(
                    string.ascii_uppercase + string.digits) for x in range(50))
            #store it in session for later use
            login_session['state'] = state
            return render_template('login.htm', STATE = state)
        else:
            if request.method == 'POST':
                print("Dentro del POST login - action:" + request.form['action'])

                if request.form['action'] == 'login':

                    UsuarioDB = session.query(Usuario).filter_by(usua_email = request.form['form-email']).first()

                    if UsuarioDB and valid_pw(request.form['form-email']
                                        , request.form['form-clave']
                                        , UsuarioDB.usua_clave):
                
                        session.permanent = True
                        login_session['last_active'] = datetime.datetime.now()

                        print("login correcto para usuario:" + request.form['form-email'])
                        login_session['sesion-usuario'] = UsuarioDB.usua_email
                        login_session['sesion-clave'] = UsuarioDB.usua_clave
                        login_session['sesion-nombre'] = UsuarioDB.usua_nombre + " " + UsuarioDB.usua_apellido 

                        UsuarioDB.usua_fecha_ult_ingreso = datetime.datetime.now()
                        session.commit()

                        
                        return redirect(url_for('administracion'))

                    else:
                        error = "Usuario o clave incorrecta"
                        return render_template('login.htm', error = error
                                                        , usuario = request.form['form-email']
                                                        , clave= request.form['form-clave'])        
                else:
                    if request.form['action'] == 'registrar':
                        # registrar
                        return redirect(url_for('registrarUsuario'))
                    else:
                        # Cancelar
                        return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))

    

def login_required(f):
    @wraps(f)
    def decorated_funtion(*args, **kwargs):
        if 'sesion-usuario' not in login_session:
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
    
    print ('logout')
    del login_session ['sesion-usuario'] 

    return redirect(url_for('login')) 
    #return render_template('pagPrincipalNahual.htm')


# Mostrar todo
@app.route('/', methods = ['GET'])
def index():
    if 'sesion-usuario' not in login_session:
        return render_template('index.html')
    else:
        return render_template('index.html', sesion_usuario=login_session ['sesion-usuario'])
    
@app.route('/showMain/', methods = ['GET'])
@login_required
def showMain():
    #posts = session.query(User).all()
    return render_template('administracion.htm')
    #if 'username' in login_session:
    #    username = login_session['username']
    #    return render_template('administracion.html', posts = posts, username = username)
    #else:
        #return render_template('administracion.html', posts = posts)


# editar usuario
@app.route('/editarUsuario', methods=['GET','POST'])
@login_required
def editarUsuario():

    username = login_session['sesion-usuario']
    password = login_session['sesion-clave']
    ciudadListDB = session.query(Ciudad).all()


    if request.method == 'GET':
        usuarioDB = session.query(Usuario).filter_by(usua_email = username).first()

        return render_template('editarUsuario.htm', usuario = usuarioDB
                                                  , ciudadList = ciudadListDB)

    else:
        if request.method == 'POST':

            if request.form['action'] == 'registrar':
                
                usuarioDB = session.query(Usuario).filter_by(usua_email = username).first()

                if not usuarioDB:
                    error = 'Ups! No encontro el usuario, reinicie la sesion por favor'
                    return render_template('editarUsuario.htm', error =  error
                                                            , ciudadList = ciudadListDB
                                                            , email = usuarioDB.usua_email
                                                            #, usuario=request.form['form-usuario']
                                                            , telefono = request.form['form-telefono']
                                                            , nombre = request.form['form-nombre']
                                                            , apellido = request.form['form-apellido']
                                                            , fecha_nacimiento = request.form['form-fecha-nac']            
                                                            , ciudadSelect = request.form['form-residencia'])

                usuario_clave =  request.form['form-clave']
                usuario_clave2 =  request.form['form-clave2']

                if len(usuario_clave)  > 0 or len(usuario_clave2) > 0 :

                    if usuario_clave != usuario_clave2:
                        error = 'Ups! la claves no coinciden'
                        return render_template('editarUsuario.htm', error =  error
                                                                , usuario = usuarioDB
                                                                , ciudadList = ciudadListDB
                                                                , email = usuarioDB.usua_email
                                                                #, usuario=request.form['form-usuario']
                                                                , telefono = request.form['form-telefono']
                                                                , nombre = request.form['form-nombre']
                                                                , apellido = request.form['form-apellido']
                                                                , fecha_nacimiento = request.form['form-fecha-nac']            
                                                                , ciudadSelect = request.form['form-residencia'])
                    else:
                        pw_hash = make_pw_hash(usuarioDB.usua_email, usuario_clave)
                        usuarioDB.usua_clave = pw_hash


                usuarioDB.usua_nombre = request.form['form-nombre']
                usuarioDB.usua_apellido = request.form['form-apellido']
                usuarioDB.usua_telefono = request.form['form-telefono']
                usuarioDB.usua_fecha_nacimiento = request.form['form-fecha-nac']      
                usuarioDB.usua_residencia_ciud_id = request.form['form-residencia']

                session.commit()

                return redirect(url_for('administracion'))
                
                    
            else:
                #cancelar
                return redirect(url_for('administracion'))


# Crear usuario
@app.route('/registrarUsuario', methods=['GET','POST'])
def registrarUsuario():

    ciudadListDB = session.query(Ciudad).all()

    if request.method == 'GET':
        return render_template('registrarUsuario.htm',  ciudadList = ciudadListDB
)
    else:
        if request.method == 'POST':

            if request.form['action'] == 'registrar':

                usuario_email = request.form['form-email']
                usuario_clave =  request.form['form-clave']
                usuario_clave2 =  request.form['form-clave2']
                
                UsuarioDB = session.query(Usuario).filter_by(
				                    usua_email = usuario_email).first()
                

                if not UsuarioDB:
                    print ("no usuario")
                    if usuario_clave != usuario_clave2:
                        error = 'claves no coinciden'
                        return render_template('registrarUsuario.htm', error =  error
                                                            , ciudadList = ciudadListDB
                                                            #, post_usuario=request.form['form-usuario']
                                                            , post_clave = request.form['form-clave']
                                                            , post_email = request.form['form-email']
                                                            , post_telefono = request.form['form-telefono']
                                                            , post_nombre = request.form['form-nombre']
                                                            , post_apellido = request.form['form-apellido']
                                                            , post_fecha_nac = request.form['form-fecha-nac']            
                                                            , post_residencia = request.form['form-residencia'])
                    else:
                        pw_hash = make_pw_hash(usuario_email, usuario_clave)
                        nuevoUsuarioDB = Usuario(usua_email = usuario_email,
                                                #usua_codigo = usuario,
                                                usua_clave = pw_hash,
                                                usua_nombre = request.form['form-nombre'],
                                                usua_apellido = request.form['form-apellido'],
                                                usua_telefono = request.form['form-telefono'],
                                                usua_fecha_nacimiento = request.form['form-fecha-nac'],
                                                usua_residencia_ciud_id = request.form['form-residencia'],
                                                usua_estado = 'Pendiente',
                                                usua_rol_id = int(4), #default CONSULTA
                                                usua_fecha_alta = datetime.datetime.now(),
                                                usua_fecha_ult_ingreso = datetime.datetime.now()
                                                )
                        session.add(nuevoUsuarioDB)
                        session.commit()


                        return redirect(url_for('login'))
                else:
                    print ("si usuario ya existe")

                    error = 'Nombre de usuario ya registrado'
                    return render_template('registrarUsuario.htm', error =  error
                                                          , ciudadList = ciudadListDB
                                                          #, post_usuario=request.form['form-usuario']
                                                          , post_clave = request.form['form-clave']
                                                          , post_email = request.form['form-email']
                                                          , post_telefono = request.form['form-telefono']
                                                          , post_nombre = request.form['form-nombre']
                                                          , post_apellido = request.form['form-apellido']
                                                          , post_fecha_nac = request.form['form-fecha-nac']            
                                                          , post_residencia = request.form['form-residencia'])
            else:
                #cancelar
                return redirect(url_for('login'))

# Borrar User
@app.route('/inscripciones/eliminar/<int:id>', methods =['GET', 'POST'])
def eliminarUser(id):

    post =session.query(Usuario).filer_by(id=id).one()

    if request.method == 'GET':
        return render_template('addLow.htm', post = post)
    else:
        if request.method == 'POST':
            session.delete(post)  
            session.commmit()
            return redirect(url_for('ShowMain'))

# Administrador
@app.route('/administracion', methods=['GET','POST'])
@login_required
def administracion():
    username = login_session['sesion-usuario']

    if request.method == 'GET':
        print("dentro del get administracion")
        return render_template('administracion.htm', username= username)
    else:
        if request.method == 'POST':
            print("dentro del post administracion " + request.form['action'])
            
            if request.form['action'] == "nodos":
                return redirect(url_for('administrarNodos'))
            if request.form['action'] == "profesores":
                return redirect(url_for('administrarProfesores'))
            if request.form['action'] == "alumnos":        
                return redirect(url_for('administrarAlumnos'))
            if request.form['action'] == "cursos":        
                return redirect(url_for('administrarCursos'))
            if request.form['action'] == "cursoNodo":        
                return redirect(url_for('administrarCursoNodo'))
            if request.form['action'] == "cursoAlumno":        
                return redirect(url_for('administrarCursoAlumno'))                
            if request.form['action'] == "salir":
                return redirect(url_for('logout'))
            if request.form['action'] == "editar":
                return redirect(url_for('editarUsuario'))
            if request.form['action'] == "inscripcion":
                return redirect(url_for('inscripcion'))
                


# Administrador
@app.route('/administracionFiltros', methods=['GET','POST'])
@login_required
def administracionFiltros():
    
    #usuario = login_session["sesion-usuario"]

    #poblar filtros globales
    nodoFiltroDB = session.query(Nodo).filter_by(nodo_estado='Activo').all()                           
    paisFiltroDB = session.query(Pais).all()
    nivelFiltroDB = session.query(Nivel).all()
    
    if request.method == 'GET':
        print("dentro del get administracionFiltros")

        return render_template('administracionFiltros.htm', paisList = paisFiltroDB
                                                          , nodoList = nodoFiltroDB
                                                          , nivelList = nivelFiltroDB)
    else:
        if request.method == 'POST':
            print("dentro del post administracionFiltros ")

            filtroNodo = request.form['form-nodo']
            # filtroAnio = request.form['form-anio']
            # filtroCuatrimestre = request.form['form-cuatrimestre']
            filtroEducacion = request.form['form-educacion']
            listaDB = session.query(Alumno, Nodo, Ciudad).filter_by(alum_nodo_id = filtroNodo).join(Alumno.nodo, Alumno.ciudad)

            return render_template('administracionFiltros.htm', nodoSelect = filtroNodo
                                                            #   , anioSelect = filtroAnio
                                                            #   , cuatrimestreSelect = filtroCuatrimestre
                                                              , educacionSelect = filtroEducacion
                                                              , nodoList = nodoFiltroDB
                                                              , paisList = paisFiltroDB
                                                              , nivelList = nivelFiltroDB
                                                              , listaBusqueda = listaDB)


# Administrador de Profesor
@app.route('/administrarProfesores', methods=['GET','POST'])
@login_required
def administrarProfesores():
    
    #usuario = login_session["sesion-usuario"]
    

    #poblar filtros globales
    profesorFiltroDB = session.query(Profesor).filter_by(prof_estado='Activo').all()  
    ciudadFiltroDB = session.query(Ciudad).all()
    
    if request.method == 'GET':
        print("dentro del get administrarProfesors")

        
        return render_template('administrarProfesores.htm', profesorList = profesorFiltroDB
                                                          , ciudadList = ciudadFiltroDB)
    else:
        if request.method == 'POST':
            print("dentro del post administrarProfesors ")

            if request.form["action"] == "agregar":
                return redirect(url_for('agregarProfesor'))
                
            if request.form['action'] == "eliminar":
                # if eliminarProfesor():
                print ("profesor: "+request.form.get['id'])
            else:
                filtroProfesor = request.form['form-profesor']
                filtroCiudad = request.form['form-ciudad']
                filtroEstado = request.form['form-estado']
                filtroDni = request.form['form-dni']

                sqlStatement = "select * from Profesor f, Ciudad c, Pais p where f.prof_ciud_id = c.ciud_id and p.pais_id = c.ciud_pais_id"            
                
                if filtroProfesor != "0" and filtroCiudad != "":
                    #listaDB = session.query(Alumno, Profesor, Ciudad).filter_by(alum_Profesor_id = filtroProfesor).join(Alumno.Profesor, Alumno.ciudad)
                    sqlStatement = sqlStatement + " and f.prof_id = " + filtroProfesor
                
                if filtroCiudad != "0" and filtroCiudad != "":
                    sqlStatement = sqlStatement + " and c.ciud_id = " + filtroCiudad

                if filtroEstado != "Todos" and filtroEstado != "":
                    sqlStatement = sqlStatement + " and f.prof_estado = '" + filtroEstado + "'"

                if filtroDni != "0" and filtroDni != "":
                    sqlStatement = sqlStatement + " and f.prof_dni = " + filtroDni
                
                #listaDB = session.query(Alumno, Profesor, Ciudad).filter_by(alum_Profesor_id = filtroProfesor).filter_by(alum_dni = filtroDni).join(Alumno.Profesor, Alumno.ciudad)
                print(sqlStatement)
                listaDB = session.execute(sqlStatement)
    
                return render_template('administrarProfesores.htm', profesorSelect = filtroProfesor
                                                                , ciudadSelect = filtroCiudad
                                                                , estadoSelect = filtroEstado
                                                                , dniSelect = filtroDni
                                                                , profesorList = profesorFiltroDB
                                                                , ciudadList = ciudadFiltroDB
                                                                , listaBusqueda = listaDB)

# Administrador de Profesor
@app.route('/profesor/<int:id>')
@login_required
def profesor(id):
    
    #usuario = login_session["sesion-usuario"]

    #poblar filtros globales
    profesorFiltroDB = session.query(Profesor).filter_by(prof_estado='Activo').all()  
    ciudadFiltroDB = session.query(Ciudad).all()

    print("dentro del post administrarProfesors")

    if request.form["action"] == "agregar":
        return redirect(url_for('agregarProfesor'))
        
    if request.form['action'] == "eliminar":
        # if eliminarProfesor():
        print ("profesor: "+ id)
    else:
        filtroProfesor = request.form['form-profesor']
        filtroCiudad = request.form['form-ciudad']
        filtroEstado = request.form['form-estado']
        filtroDni = request.form['form-dni']

        sqlStatement = "select * from Profesor f, Ciudad c, Pais p where f.prof_ciud_id = c.ciud_id and p.pais_id = c.ciud_pais_id"            
        
        if filtroProfesor != "0" and filtroCiudad != "":
            #listaDB = session.query(Alumno, Profesor, Ciudad).filter_by(alum_Profesor_id = filtroProfesor).join(Alumno.Profesor, Alumno.ciudad)
            sqlStatement = sqlStatement + " and f.prof_id = " + filtroProfesor
        
        if filtroCiudad != "0" and filtroCiudad != "":
            sqlStatement = sqlStatement + " and c.ciud_id = " + filtroCiudad

        if filtroEstado != "Todos" and filtroEstado != "":
            sqlStatement = sqlStatement + " and f.prof_estado = '" + filtroEstado + "'"

        if filtroDni != "0" and filtroDni != "":
            sqlStatement = sqlStatement + " and f.prof_dni = " + filtroDni
        
        #listaDB = session.query(Alumno, Profesor, Ciudad).filter_by(alum_Profesor_id = filtroProfesor).filter_by(alum_dni = filtroDni).join(Alumno.Profesor, Alumno.ciudad)
        print(sqlStatement)
        listaDB = session.execute(sqlStatement)

        return render_template('administrarProfesores.htm', profesorSelect = filtroProfesor
                                                        , ciudadSelect = filtroCiudad
                                                        , estadoSelect = filtroEstado
                                                        , dniSelect = filtroDni
                                                        , profesorList = profesorFiltroDB
                                                        , ciudadList = ciudadFiltroDB
                                                        , listaBusqueda = listaDB)

# Crear Profesor
@app.route('/agregarProfesor', methods=['GET','POST'])
@login_required
def agregarProfesor():

    if request.method == 'GET':
        ciudadListDB = session.query(Ciudad).all()
        return render_template('formProfesor.htm', actionSelect = "agregar"
                                                , ciudadList = ciudadListDB)
    else:
        if request.method == 'POST':
            profeDB = session.query(Profesor).filter_by(prof_dni = request.form['form-dni']).first()
            if profeDB:
                error = "Profesor ya registrado con el DNI ingresado."
                return render_template('error.htm', error = error)
            else:
                profesorDB = Profesor (
                    prof_dni = request.form['form-dni'],
                    prof_nombre = request.form['form-nombre'],
                    prof_apellido = request.form['form-apellido'],
                    prof_ciud_id = request.form['form-ciudad'],
                    prof_fecha_alta = datetime.datetime.now(),
                    prof_estado = request.form['form-estado'],
                    prof_telefono = request.form['form-telefono'],
                    prof_email = request.form['form-email'],
                    prof_direccion = request.form['form-direccion'],
                    prof_twitter = request.form['form-twitter'],
                    prof_linkedin = request.form['form-linkedin'],
                    prof_instagram = request.form['form-instagram'],
                    prof_facebook = request.form['form-facebook'],
                    prof_fecha_modif = datetime.datetime.now(),
                    prof_usuario_modif = login_session['sesion-usuario'])
                session.add(profesorDB)
                session.commit()
                msg = 'Operacion realizada con exito.'
                return render_template('success.htm', msg = msg)

# Ver Profesor
@app.route('/detalleProfesor', methods=['GET'])
@login_required
def detalleProfesor():

        id = request.args.get('id')
        profesorDB = session.query(Profesor).filter_by(prof_id = id).first()
        print (profesorDB)
        if profesorDB:
            ciudadListDB = session.query(Ciudad).all()

            return render_template('formProfesor.htm', actionSelect="detalle"
                                                 , profesorSelect = profesorDB
                                                , ciudadList = ciudadListDB)
        else:
            return render_template('error.htm', error= 'UPS...No se encontro el Profesor')

    

# Ver Profesor
@app.route('/editarProfesor', methods=['GET','POST'])
@login_required
def editarProfesor():

    if request.method == 'GET':
        id = request.args.get('id')
        ciudadListDB = session.query(Ciudad).all()
        #profesorDB = session.query(Profesor, Ciudad).filter_by(Profesor_id = Profesor).join(Profesor.ciudad).first()
        profesorDB = session.query(Profesor).filter_by(prof_id = id).first()
        if profesorDB:      
            return render_template('formProfesor.htm', actionSelect="editar"
                                                , profesorSelect = profesorDB
                                                , ciudadList = ciudadListDB)
        else:
            return render_template('error.htm', error= 'UPS...No se encontro el Profesor')                                                  
    else:
        if request.method == 'POST':
            profesorDB = session.query(Profesor).filter_by(prof_id= request.form['form-id']).first()

            #profesorDB.prof_dni = request.form['form-dni'],
            profesorDB.prof_nombre = request.form['form-nombre']
            profesorDB.prof_apellido = request.form['form-apellido']
            profesorDB.prof_ciud_id = request.form['form-ciudad']
            profesorDB.prof_estado = request.form['form-estado']
            profesorDB.prof_telefono = request.form['form-telefono']
            profesorDB.prof_email = request.form['form-email']
            profesorDB.prof_direccion = request.form['form-direccion']
            profesorDB.prof_twitter = request.form['form-twitter']
            profesorDB.prof_linkedin = request.form['form-linkedin']
            profesorDB.prof_instagram = request.form['form-instagram']
            profesorDB.prof_facebook = request.form['form-facebook']
            profesorDB.prof_fecha_modif = datetime.datetime.now()
            profesorDB.prof_usuario_modif = login_session['sesion-usuario']

            session.commit()

            msg = 'Operacion realizada con exito.'
            return render_template('success.htm', msg = msg)

# eliminar Profesor
@app.route('/eliminarProfesor', methods=['GET'])
@login_required
def eliminarProfesor():

    id = request.args.get('id')
    # update
    profesorDB = session.query(Profesor).filter_by(prof_id = id).first()
    if profesorDB:
        profesorDB.prof_estado = 'Inactivo'
        profesorDB.prof_fecha_modif = datetime.datetime.now()
        profesorDB.prof_usuario_modif = login_session['sesion-usuario']
        session.commit()
        msg = 'Operacion realizada con exito.'
        return render_template('success.htm', msg = msg)
        
    else:
        return render_template('error.htm', error='UPS...No se encontro el Profesor') 

 
# Administrador de Nodo
@app.route('/administrarNodos', methods=['GET','POST'])
@login_required
def administrarNodos():
    
    #usuario = login_session["sesion-usuario"]
    

    #poblar filtros globales
    nodoFiltroDB = session.query(Nodo).filter_by(nodo_estado='Activo').all()                           
    ciudadFiltroDB = session.query(Ciudad).all()
    
    if request.method == 'GET':
        print("dentro del get administrarNodos")

        return render_template('administrarNodos.htm', nodoList = nodoFiltroDB
                                                     , ciudadList = ciudadFiltroDB)
    else:
        if request.method == 'POST':
            print("dentro del post administrarNodos ")

            if request.form["action"] == "agregar":
                return redirect(url_for('agregarNodo'))
            else:    
                filtroNodo = request.form['form-nodo']
                filtroCiudad = request.form['form-ciudad']
                filtroEstado = request.form['form-estado']
                
                sqlStatement = "select * from Nodo n, Ciudad c, Pais p where n.nodo_ciud_id = c.ciud_id and p.pais_id = c.ciud_pais_id"            
                
                if filtroNodo != "0" and filtroNodo != "":
                    #listaDB = session.query(Alumno, Nodo, Ciudad).filter_by(alum_nodo_id = filtroNodo).join(Alumno.nodo, Alumno.ciudad)
                    sqlStatement = sqlStatement + " and n.nodo_id = " + filtroNodo
                
                if filtroCiudad != "0" and filtroCiudad != "":
                    sqlStatement = sqlStatement + " and c.ciud_id = " + filtroCiudad
                
                if filtroEstado != "Todos":
                    sqlStatement = sqlStatement + " and n.nodo_estado = '" + filtroEstado + "'"

                #listaDB = session.query(Alumno, Nodo, Ciudad).filter_by(alum_nodo_id = filtroNodo).filter_by(alum_dni = filtroDni).join(Alumno.nodo, Alumno.ciudad)
                print(sqlStatement)
                listaDB = session.execute(sqlStatement)
    
                return render_template('administrarNodos.htm', nodoSelect = filtroNodo
                                                                , ciudadSelect = filtroCiudad
                                                                , estadoSelect = filtroEstado
                                                                , nodoList = nodoFiltroDB
                                                                , ciudadList = ciudadFiltroDB
                                                                , listaBusqueda = listaDB)


# Crear Nodo
@app.route('/agregarNodo', methods=['GET','POST'])
@login_required
def agregarNodo():

    if request.method == 'GET':
        ciudadListDB = session.query(Ciudad).all()
        return render_template('formNodo.htm', actionSelect = "agregar"
                                             , ciudadList = ciudadListDB)
    else:
        if request.method == 'POST':
            nodoDB = session.query(Nodo).filter_by(nodo_nombre = request.form['form-nombre']).first()
            if nodoDB:
                error = "Nodo ya registrado con ese nombre."
                return render_template('error.htm', error = error)

            else:
                nodoDB = Nodo (
                    nodo_nombre = request.form['form-nombre'],
                    nodo_ciud_id = request.form['form-ciudad'],
                    nodo_fecha_alta = datetime.datetime.now(),
                    nodo_estado = request.form['form-estado'],
                    nodo_fecha_modif = datetime.datetime.now(),
                    nodo_usuario_modif = login_session['sesion-usuario'])
                session.add(nodoDB)
                session.commit()
                msg = 'Operacion realizada con exito.'
                return render_template('success.htm', msg = msg)

# Ver Nodo
@app.route('/detalleNodo', methods=['GET'])
@login_required
def detalleNodo():

        id = request.args.get('id')
        nodoDB = session.query(Nodo).filter_by(nodo_id = id).first()
        if nodoDB:
            ciudadListDB = session.query(Ciudad).all()

            return render_template('formNodo.htm', actionSelect="detalle"
                                                 , nodoSelect = nodoDB
                                                 , ciudadList = ciudadListDB)
        else:
            return render_template('error.htm', error= 'UPS...No se encontro el Nodo')

    

# Ver Nodo
@app.route('/editarNodo', methods=['GET','POST'])
@login_required
def editarNodo():

    if request.method == 'GET':
        id = request.args.get('id')
        ciudadListDB = session.query(Ciudad).all()
        nodoDB = session.query(Nodo).filter_by(nodo_id = id).first()
        if nodoDB:      
            return render_template('formNodo.htm', actionSelect="editar"
                                                , nodoSelect = nodoDB
                                                , ciudadList = ciudadListDB)
        else:
            return render_template('error.htm', error= 'UPS...No se encontro el Nodo')                                                  
    else:
        if request.method == 'POST':
            nodoDB = session.query(Nodo).filter_by(nodo_id= request.form['form-nodo']).first()
            nodoDB.nodo_nombre = request.form['form-nombre']
            nodoDB.nodo_ciud_id = request.form['form-ciudad']
            nodoDB.nodo_estado =  request.form['form-estado']
            nodoDB.nodo_fecha_modif = datetime.datetime.now()
            nodoDB.nodo_usuario_modif = login_session['sesion-usuario']
            session.commit()

            msg = 'Operacion realizada con exito.'
            return render_template('success.htm', msg = msg)

# eliminar Nodo
@app.route('/eliminarNodo', methods=['GET'])
@login_required
def eliminarNodo():

    id = request.args.get('id')
    # update
    nodoDB = session.query(Nodo).filter_by(nodo_id = id).first()
    if nodoDB:
        nodoDB.nodo_estado = 'Inactivo'
        nodoDB.nodo_fecha_modif = datetime.datetime.now()
        nodoDB.nodo_usuario_modif = login_session['sesion-usuario']
        session.commit()
        msg = 'Operacion realizada con exito.'
        return render_template('success.htm', msg = msg)

    else:
        return render_template('error.htm', error='UPS...No se encontro el Nodo') 




# Administrador de Curso
@app.route('/administrarCursos', methods=['GET','POST'])
@login_required
def administrarCursos():
    
    #poblar filtros globales
    cursoFiltroDB = session.query(Curso).filter_by(curs_estado='Activo').all()                           
    
    if request.method == 'GET':
        print("dentro del get administrarCursos")

        return render_template('administrarCursos.htm', cursoList = cursoFiltroDB)
    else:
        if request.method == 'POST':
            print("dentro del post administrarCursos ")

            if request.form["action"] == "agregar":
                return redirect(url_for('agregarCurso'))
            else:    
                filtroCurso = request.form['form-curso']
                # filtroAnio = request.form['form-anio']
                # filtroCuatrimestre = request.form['form-cuatrimestre']
                filtroEstado = request.form['form-estado']

                sqlStatement = "select * from Curso c where 1=1"
                
                if filtroCurso != "0" and filtroCurso != "":
                    #listaDB = session.query(Alumno, Curso, Ciudad).filter_by(alum_curs_id = filtroCurso).join(Alumno.curso, Alumno.ciudad)
                    sqlStatement = sqlStatement + " and c.curs_id = " + filtroCurso
                
                # if filtroAnio != "0" and filtroAnio != "":
                #     sqlStatement = sqlStatement + " and c.curs_anio = " + filtroAnio

                # if filtroCuatrimestre != "0" and filtroCuatrimestre != "":
                #     sqlStatement = sqlStatement + " and c.curs_cuatrimestre = " + filtroCuatrimestre
                
                if filtroEstado != "Todos":
                    sqlStatement = sqlStatement + " and c.curs_estado = '" + filtroEstado + "'"

                #listaDB = session.query(Alumno, Curso, Ciudad).filter_by(alum_curs_id = filtroCurso).filter_by(alum_dni = filtroDni).join(Alumno.curso, Alumno.ciudad)
                print(sqlStatement)
                listaDB = session.execute(sqlStatement)
    
                return render_template('administrarCursos.htm', cursoSelect = filtroCurso
                                                                # , anioSelect = filtroAnio
                                                                # , cuatrimestreSelect = filtroCuatrimestre
                                                                , estadoSelect = filtroEstado
                                                                , cursoList = cursoFiltroDB
                                                                , listaBusqueda = listaDB)


# Crear Curso
@app.route('/agregarCurso', methods=['GET','POST'])
@login_required
def agregarCurso():

    if request.method == 'GET':
        return render_template('formCurso.htm', actionSelect = "agregar")
    else:
        if request.method == 'POST':
            cursoDB = session.query(Curso).filter_by(curs_nombre = request.form['form-nombre']
                                                #    , curs_anio = request.form['form-anio']
                                                #    , curs_cuatrimestre = request.form['form-cuatrimestre']
                                                   ).first()
            if cursoDB:
                error = "Curso ya registrado con ese nombre para el anio y cuatrimestre."
                return render_template('error.htm', error = error)
            else:
                cursoDB = Curso (
                    curs_nombre = request.form['form-nombre'],
                    curs_anio = request.form['form-detalle'],
                    # curs_anio = request.form['form-anio'],
                    # curs_cuatrimestre = request.form['form-cuatrimestre'],
                    curs_estado = request.form['form-estado']
                    #curs_fecha_modif = datetime.datetime.now(),
                    #curs_usuario_modif = login_session['sesion-usuario'])
                )
                session.add(cursoDB)
                session.commit()
                msg = 'Operacion realizada con exito.'
                return render_template('success.htm', msg = msg)
# Ver Curso
@app.route('/detalleCurso', methods=['GET'])
@login_required
def detalleCurso():

        id = request.args.get('id')
        cursoDB = session.query(Curso).filter_by(curs_id = id).first()
        if cursoDB:
             

            return render_template('formCurso.htm', actionSelect="detalle"
                                                    , cursoSelect = cursoDB )
        else:
            return render_template('error.htm', error= 'UPS...No se encontro el Curso')

    

# Ver Curso
@app.route('/editarCurso', methods=['GET','POST'])
@login_required
def editarCurso():

    if request.method == 'GET':
        id = request.args.get('id')
        cursoDB = session.query(Curso).filter_by(curs_id = id).first()
        if cursoDB:      
            return render_template('formCurso.htm', actionSelect="editar"
                                                , cursoSelect = cursoDB )
        else:
            return render_template('error.htm', error= 'UPS...No se encontro el Curso')                                                  
    else:
        if request.method == 'POST':
            cursoDB = session.query(Curso).filter_by(curs_id= request.form['form-curso']).first()
            print( request.form['form-estado'])
            cursoDB.curs_nombre = request.form['form-nombre']
            cursoDB.curs_detalle = request.form['form-detalle']
            # cursoDB.curs_anio = request.form['form-anio']
            # cursoDB.curs_cuatrimestre = request.form['form-cuatrimestre']
            cursoDB.curs_estado =  request.form['form-estado']
            #cursoDB.curs_fecha_modif = datetime.datetime.now()
            #cursoDB.curs_usuario_modif = login_session['sesion-usuario']
            session.commit()

            msg = 'Operacion realizada con exito.'
            return render_template('success.htm', msg = msg)

# eliminar Curso
@app.route('/eliminarCurso', methods=['GET'])
@login_required
def eliminarCurso():

    id = request.args.get('id')
    # update
    cursoDB = session.query(Curso).filter_by(curs_id = id).first()
    if cursoDB:
        cursoDB.curs_estado = 'Inactivo'
        cursoDB.curs_fecha_modif = datetime.datetime.now()
        cursoDB.curs_usuario_modif = login_session['sesion-usuario']
        session.commit()
        msg = 'Operacion realizada con exito.'
        return render_template('success.htm', msg = msg)

    else:
        return render_template('error.htm', error='UPS...No se encontro el Curso') 


# Administrador de CursoNodo
@app.route('/administrarCursoNodo', methods=['GET','POST'])
@login_required
def administrarCursoNodo():
    
    # poblar filtros globales
    cursoFiltroDB = session.query(Curso).filter_by(curs_estado = 'Activo').all()                           
    nodoFiltroDB = session.query(Nodo).filter_by(nodo_estado = 'Activo').all()                           
    profesorFiltroDB = session.query(Profesor).filter_by(prof_estado = 'Activo').all()                               

    if request.method == 'GET':
        print("dentro del get administrarCursoNodo")

        return render_template('administrarCursoNodo.htm' , cursoList = cursoFiltroDB
                                                          , nodoList = nodoFiltroDB
                                                          , profesorList = profesorFiltroDB)
    else:
        if request.method == 'POST':
            print("dentro del post administrarCursoNodo ")

            if request.form["action"] == "agregar":
                return redirect(url_for('agregarCursoNodoNodo'))
            else:    
                filtroCurso = request.form['form-curso']
                filtroNodo = request.form['form-nodo']
                filtroAnio = request.form['form-anio']
                filtroCuatrimestre = request.form['form-cuatrimestre']
                filtroEstado = request.form['form-estado']
                filtroProfesor = request.form['form-profesor']


                sqlStatement = "select * from Curso_Nodo c, curso s, nodo n, profesor p where c.cuno_curs_id = s.curs_id and c.cuno_nodo_id = n.nodo_id and c.cuno_prof_id = p.prof_id"
                
                if filtroCurso != "0" and filtroCurso != "":
                    sqlStatement = sqlStatement + " and c.cuno_curs_id = " + filtroCurso
                
                if filtroNodo != "0" and filtroNodo != "":
                    sqlStatement = sqlStatement + " and c.cuno_nodo_id = " + filtroNodo

                if filtroProfesor != "0" and filtroProfesor != "":
                    sqlStatement = sqlStatement + " and c.cuno_prof_id = " + filtroProfesor
                
                if filtroAnio != "0" and filtroAnio != "":
                     sqlStatement = sqlStatement + " and c.cuno_anio = " + filtroAnio

                if filtroCuatrimestre != "0" and filtroCuatrimestre != "":
                     sqlStatement = sqlStatement + " and c.cuno_cuatrimestre = " + filtroCuatrimestre
                
                if filtroEstado != "Todos":
                    sqlStatement = sqlStatement + " and c.cuno_estado = '" + filtroEstado + "'"
                
                print(sqlStatement)
                listaDB = session.execute(sqlStatement)
    
                return render_template('administrarCursoNodo.htm', cursoSelect = filtroCurso
                                                                 , anioSelect = filtroAnio
                                                                 , cuatrimestreSelect = filtroCuatrimestre
                                                                 , profesorSelect = filtroProfesor
                                                                 , nodoSelect = filtroNodo
                                                                , estadoSelect = filtroEstado
                                                                , cursoList = cursoFiltroDB
                                                                , nodoList = nodoFiltroDB
                                                                , profesorList = profesorFiltroDB
                                                                , listaBusqueda = listaDB)


# Crear CursoNodo
@app.route('/agregarCursoNodo', methods=['GET','POST'])
@login_required
def agregarCursoNodo():

    if request.method == 'GET':
        # poblar filtros globales
        cursoFiltroDB = session.query(Curso).filter_by(curs_estado = 'Activo').all()                           
        nodoFiltroDB = session.query(Nodo).filter_by(nodo_estado = 'Activo').all()                           
        profesorFiltroDB = session.query(Profesor).filter_by(prof_estado = 'Activo').all()                               

        return render_template('formCursoNodo.htm', actionSelect = "agregar"
                                                    , cursoList = cursoFiltroDB
                                                    , nodoList = nodoFiltroDB
                                                    , profesorList = profesorFiltroDB)
    else:
        if request.method == 'POST':
            cursoNodoDB = session.query(Curso_Nodo).filter_by(cuno_curs_id = request.form['form-curso']
                                                            , cuno_nodo_id = request.form['form-nodo']
                                                            , cuno_anio = request.form['form-anio']
                                                            , cuno_cuatrimestre = request.form['form-cuatrimestre']
                                                   ).first()
            if cursoNodoDB:
                error = "Curso ya existe en ese Nodo para el Anio y Cuatrimestre."
                return render_template('error.htm', error = error)
            else:
                cursoNodoDB = Curso_Nodo (
                    cuno_curs_id = request.form['form-curso'],
                    cuno_nodo_id = request.form['form-nodo'],
                    cuno_prof_id = request.form['form-profesor'],
                    cuno_anio = request.form['form-anio'],
                    cuno_cuatrimestre = request.form['form-cuatrimestre'],
                    cuno_estado = request.form['form-estado']
                    # cuno_fecha_modif = datetime.datetime.now(),
                    # cuno_usuario_modif = login_session['sesion-usuario']
                )
                session.add(cursoNodoDB)
                session.commit()
                msg = 'Operacion realizada con exito.'
                return render_template('success.htm', msg = msg)

#Ver CursoNodo
@app.route('/detalleCursoNodo', methods=['GET'])
@login_required
def detalleCursoNodo():

        id = request.args.get('id')
        cursoNodoDB = session.query(Curso_Nodo).filter_by(cuno_id = id).first()
        # poblar filtros globales
        cursoFiltroDB = session.query(Curso).filter_by(curs_estado = 'Activo').all()                           
        nodoFiltroDB = session.query(Nodo).filter_by(nodo_estado = 'Activo').all()                           
        profesorFiltroDB = session.query(Profesor).filter_by(prof_estado = 'Activo').all()                               

        print ( cursoNodoDB)
        if cursoNodoDB:
             

            return render_template('formCursoNodo.htm', actionSelect="detalle"
                                                      , cursoNodoSelect = cursoNodoDB
                                                      , cursoList = cursoFiltroDB
                                                      , nodoList = nodoFiltroDB
                                                      , profesorList = profesorFiltroDB)
        else:
            return render_template('error.htm', error= 'UPS...No se encontro el CursoNodo')

    

# Ver CursoNodo
@app.route('/editarCursoNodo', methods=['GET','POST'])
@login_required
def editarCursoNodo():

    if request.method == 'GET':
        id = request.args.get('id')
        cursoNodoDB = session.query(Curso_Nodo).filter_by(cuno_id = id).first()
        # poblar filtros globales
        cursoFiltroDB = session.query(Curso).filter_by(curs_estado = 'Activo').all()                           
        nodoFiltroDB = session.query(Nodo).filter_by(nodo_estado = 'Activo').all()                           
        profesorFiltroDB = session.query(Profesor).filter_by(prof_estado = 'Activo').all()                               

        if cursoNodoDB:      
            return render_template('formCursoNodo.htm', actionSelect="editar"
                                                      , cursoNodoSelect = cursoNodoDB
                                                      , cursoList = cursoFiltroDB
                                                      , nodoList = nodoFiltroDB
                                                      , profesorList = profesorFiltroDB )
        else:
            return render_template('error.htm', error= 'UPS...No se encontro el CursoNodo')                                                  
    else:
        if request.method == 'POST':
            cursoNodoDB = session.query(Curso_Nodo).filter_by(cuno_curs_id = request.form['form-curso']
                                                            , cuno_nodo_id = request.form['form-nodo']
                                                            , cuno_anio = request.form['form-anio']
                                                            , cuno_cuatrimestre = request.form['form-cuatrimestre']
                                                   ).first()
            if cursoNodoDB:
                error = "Curso ya existe en ese Nodo para el Anio y Cuatrimestre."
                return render_template('error.htm', error = error)
            else:
                cursoNodoDB = session.query(Curso_Nodo).filter_by(cuno_id= request.form['form-id']).first()
                cursoNodoDB.cuno_nodo_id = request.form['form-nodo']
                cursoNodoDB.cuno_prof_id = request.form['form-profesor']
                cursoNodoDB.cuno_anio = request.form['form-anio']
                cursoNodoDB.cuno_cuatrimestre = request.form['form-cuatrimestre']
                cursoNodoDB.cuno_estado =  request.form['form-estado']
                # cursoNodoDB.curs_fecha_modif = datetime.datetime.now()
                # cursoNodoDB.curs_usuario_modif = login_session['sesion-usuario']
                session.commit()

                msg = 'Operacion realizada con exito.'
                return render_template('success.htm', msg = msg) 

# eliminar CursoNodo
@app.route('/eliminarCursoNodo', methods=['GET'])
@login_required
def eliminarCursoNodo():

    id = request.args.get('id')
    # update
    cursoNodoDB = session.query(Curso_Nodo).filter_by(cuno_id = id).first()
    if cursoNodoDB:
        cursoNodoDB.cuno_estado = 'Inactivo'
        # cursoNodoDB.curs_fecha_modif = datetime.datetime.now()
        # cursoNodoDB.curs_usuario_modif = login_session['sesion-usuario']
        session.commit()
        msg = 'Operacion realizada con exito.'
        return render_template('success.htm', msg = msg)
    else:
        return render_template('error.htm', error='UPS...No se encontro el CursoNodo') 



# Administrador de CursoAlumno
@app.route('/administrarCursoAlumno', methods=['GET','POST'])
@login_required
def administrarCursoAlumno():
    
    # poblar filtros globales
    cursoFiltroDB = session.query(Curso).filter_by(curs_estado = 'Activo').all()                           
    nodoFiltroDB = session.query(Nodo).filter_by(nodo_estado = 'Activo').all()                           
    alumnoFiltroDB = session.query(Alumno).all() #filter_by(alum_estado != 'Rechazado').all()                               

    if request.method == 'GET':
        print("dentro del get administrarCursoAlumno")

        return render_template('administrarCursoAlumno.htm' , cursoList = cursoFiltroDB
                                                          , nodoList = nodoFiltroDB
                                                          , alumnoList = alumnoFiltroDB)
    else:
        if request.method == 'POST':
            print("dentro del post administrarCursoAlumno ")

            if request.form["action"] == "agregar":
                return redirect(url_for('agregarCursoAlumnoNodo'))
            else:    
                filtroCurso = request.form['form-curso']
                filtroNodo = request.form['form-nodo']
                filtroAlumno = request.form['form-alumno']
                filtroEstado = request.form['form-estado']



                sqlStatement = "select * from Curso_Alumno ca, curso_nodo cn, curso c, nodo n, alumno a where ca.cual_cuno_id = cn.cuno_id and cn.cuno_curs_id = c.curs_id and cn.cuno_nodo_id = n.nodo_id and ca.cual_alum_id = a.alum_id"
                print (sqlStatement)
                print ('curso:'+filtroCurso + ' nodo:'+filtroNodo + ' alum:'+filtroAlumno +' estado: '+filtroEstado)
                if filtroCurso != "0" and filtroCurso != "":
                    sqlStatement = sqlStatement + " and cn.cuno_curs_id = " + filtroCurso
                
                if filtroNodo != "0" and filtroNodo != "":
                    sqlStatement = sqlStatement + " and cn.cuno_nodo_id = " + filtroNodo

                if filtroAlumno != "0" and filtroAlumno != "":
                    sqlStatement = sqlStatement + " and ca.cual_alum_id = " + filtroAlumno
                
                if filtroEstado != "Todos":
                    sqlStatement = sqlStatement + " and ca.cual_estado = '" + filtroEstado + "'"
                
                print(sqlStatement)
                listaDB = session.execute(sqlStatement)
    
                return render_template('administrarCursoAlumno.htm', cursoSelect = filtroCurso
                                                                 , alumnoSelect = filtroAlumno
                                                                 , nodoSelect = filtroNodo
                                                                , estadoSelect = filtroEstado
                                                                , cursoList = cursoFiltroDB
                                                                , nodoList = nodoFiltroDB
                                                                , alumnoList = alumnoFiltroDB
                                                                , listaBusqueda = listaDB)


# Crear CursoAlumno
@app.route('/agregarCursoAlumno', methods=['GET','POST'])
@login_required
def agregarCursoAlumno():

    if request.method == 'GET':
        # poblar filtros globales
        cursoNodoFiltroDB = session.query(Curso_Nodo, Curso, Nodo).filter_by(cuno_estado = 'Activo').join(Curso_Nodo.curso, Curso_Nodo.nodo).all()                           
        alumnoFiltroDB = session.query(Alumno).all() #filter_by(alum_estado != 'Rechazado').all()                               
        # profesorFiltroDB = session.query(Profesor).filter_by(prof_estado = 'Activo').all()                               

        return render_template('formCursoAlumno.htm', actionSelect = "agregar"
                                                    , cursoNodoList = cursoNodoFiltroDB
                                                    , alumnoList = alumnoFiltroDB
                                                    # , profesorList = profesorFiltroDB
                                                    )
    else:
        if request.method == 'POST':
            # cursoAlumnoDB = session.query(Curso_Alumno, Curso_Nodo).filter_by(cual_cuno_id = id).join(Curso_Alumno.cursoNodo).first()
            cursoAlumnoDB = session.query(Curso_Alumno).filter_by(cual_cuno_id = request.form['form-cuno']
                                                                , cual_alum_id = request.form['form-alumno']
                                                                # , cual_anio = request.form['form-alumno']
                                                                ).first()
            if cursoAlumnoDB:
                error = "Ya existe el alumno en este Curso."
                return render_template('error.htm', error = error)
            else:
                cursoAlumnoDB = Curso_Alumno (
                    cual_cuno_id = request.form['form-cuno'],
                    cual_alum_id = request.form['form-alumno'],
                    #cual_anio = request.form['form-anio'],
                    #cual_cuatrimestre = request.form['form-cuatrimestre'],
                    cual_estado = request.form['form-estado'],
                    cual_fecha_alta = datetime.datetime.now()
                )
                print ("cuno:"+ request.form['form-cuno'])
                session.add(cursoAlumnoDB)
                session.commit()
                msg = 'Operacion realizada con exito.'
                return render_template('success.htm', msg = msg)

#Ver CursoAlumno
@app.route('/detalleCursoAlumno', methods=['GET'])
@login_required
def detalleCursoAlumno():

        id = request.args.get('id')
        cursoAlumnoDB = session.query(Curso_Alumno, Curso_Nodo).filter_by(cual_id = id).join(Curso_Alumno.cursoNodo).first()
        # poblar filtros globales
        alumnoFiltroDB = session.query(Alumno).all() #filter_by(alum_estado != 'Rechazado').all()
        cursoFiltroDB = session.query(Curso).filter_by(curs_estado = 'Activo').all()                           
        nodoFiltroDB = session.query(Nodo).filter_by(nodo_estado = 'Activo').all()                           
        profesorFiltroDB = session.query(Profesor).filter_by(prof_estado = 'Activo').all()                               

        print ( cursoAlumnoDB)
        if cursoAlumnoDB:
             
            return render_template('formCursoAlumno.htm', actionSelect="detalle"
                                                      , cursoAlumnoSelect = cursoAlumnoDB
                                                      , cursoList = cursoFiltroDB
                                                      , nodoList = nodoFiltroDB
                                                      , alumnoList = alumnoFiltroDB
                                                      , profesorList = profesorFiltroDB
                                                      )
        else:
            return render_template('error.htm', error= 'UPS...No se encontro el CursoAlumno')

    

# Ver CursoAlumno
@app.route('/editarCursoAlumno', methods=['GET','POST'])
@login_required
def editarCursoAlumno():

    if request.method == 'GET':
        id = request.args.get('id')
        cursoAlumnoDB = session.query(Curso_Alumno, Curso_Nodo).filter_by(cual_id = id).join(Curso_Alumno.cursoNodo).first()
        # poblar filtros globales
        cursoFiltroDB = session.query(Curso).filter_by(curs_estado = 'Activo').all()                           
        nodoFiltroDB = session.query(Nodo).filter_by(nodo_estado = 'Activo').all()                           
        alumnoFiltroDB = session.query(Alumno).all() #filter_by(alum_estado != 'Rechazado').all()                               
        profesorFiltroDB = session.query(Profesor).filter_by(prof_estado = 'Activo').all()                               

        if cursoAlumnoDB:      
            return render_template('formCursoAlumno.htm', actionSelect="editar"
                                                      , cursoAlumnoSelect = cursoAlumnoDB
                                                      , cursoList = cursoFiltroDB
                                                      , nodoList = nodoFiltroDB
                                                      , alumnoList = alumnoFiltroDB 
                                                      , profesorList = profesorFiltroDB
                                                      )
        else:
            return render_template('error.htm', error= 'UPS...No se encontro el CursoAlumno')                                                  
    else:
        if request.method == 'POST':
            cursoAlumnoDB = session.query(Curso_Alumno).filter_by(cual_cuno_id = request.form['form-cuno']
                                                                , cual_alum_id = request.form['form-alumno']
                                                                # , cual_anio = request.form['form-alumno']
                                                                ).first()
            if cursoAlumnoDB:
                error = "Ya existe el alumno en este Curso."
                return render_template('error.htm', error = error)
            else:
            
                cursoAlumnoDB = session.query(Curso_Alumno).filter_by(cual_id= request.form['form-id']).first()
                # cursoAlumnoDB.cual_cuno_id = request.form['form-cuno']
                cursoAlumnoDB.cual_alum_id = request.form['form-alumno']
                #cursoAlumnoDB.cual_fecha_alta = request.form['form-fecha-alta']
                cursoAlumnoDB.cual_prof_firma_id = request.form['form-profesor']
                if (request.form['form-fecha-firma']!=''):
                    cursoAlumnoDB.cual_fecha_firma = request.form['form-fecha-firma']
                cursoAlumnoDB.cual_nota_final = request.form['form-nota']
                cursoAlumnoDB.cual_estado =  request.form['form-estado']
                print ("estado:"+ request.form['form-estado'])
                print ("alumno:"+ request.form['form-alumno'])

                # cursoAlumnoDB.curs_fecha_modif = datetime.datetime.now()
                # cursoAlumnoDB.curs_usuario_modif = login_session['sesion-usuario']
                session.commit()

                msg = 'Operacion realizada con exito.'
                return render_template('success.htm', msg = msg) 

# eliminar CursoAlumno
@app.route('/eliminarCursoAlumno', methods=['GET'])
@login_required
def eliminarCursoAlumno():

    id = request.args.get('id')
    # update
    cursoAlumnoDB = session.query(Curso_Alumno).filter_by(cual_id = id).first()
    if cursoAlumnoDB:
        cursoAlumnoDB.cual_estado = 'Inactivo'
        # cursoAlumnoDB.curs_fecha_modif = datetime.datetime.now()
        # cursoAlumnoDB.curs_usuario_modif = login_session['sesion-usuario']
        session.commit()
        msg = 'Operacion realizada con exito.'
        return render_template('success.htm', msg = msg)
    else:
        return render_template('error.htm', error='UPS...No se encontro el CursoAlumno') 





# Administrador de alumnos
@app.route('/administrarAlumnos', methods=['GET','POST'])
@login_required
def administrarAlumnos():
    
    #usuario = login_session["sesion-usuario"]
    

    #poblar filtros globales
    nodoFiltroDB = session.query(Nodo).filter_by(nodo_estado='Activo').all()                           
    nivelFiltroDB = session.query(Nivel).all()
    
    if request.method == 'GET':
        print("dentro del get administracionFiltros")

        return render_template('administrarAlumnos.htm', nodoList = nodoFiltroDB
                                                       , nivelList = nivelFiltroDB)
    else:
        if request.method == 'POST':
            print("dentro del post administrarAlumnos ")

            filtroNodo = request.form['form-nodo']
            filtroDni = request.form['form-dni']
            filtroEducacion = request.form['form-educacion']
            filtroEstado = request.form['form-estado']

            sqlStatement = "select * from Alumno a, Alumno_Estudio e, Nodo n, Nivel v, Ciudad c where a.alum_id = e.ales_alum_id and n.nodo_id = a.alum_nodo_id and e.ales_nivel_educacion_id = v.nive_id and c.ciud_id = a.alum_ciud_residencia_id"
            
            if filtroNodo != "0" and filtroNodo != "":
                #listaDB = session.query(Alumno, Nodo, Ciudad).filter_by(alum_nodo_id = filtroNodo).join(Alumno.nodo, Alumno.ciudad)
                sqlStatement = sqlStatement + " and n.nodo_id = " + filtroNodo

            if filtroDni != "0" and filtroDni != "":
                sqlStatement = sqlStatement + " and a.alum_dni = " + filtroDni
            
            if filtroEducacion != "0" and filtroEducacion != "":
                sqlStatement = sqlStatement + " and v.nive_id = " + filtroEducacion
                    
            if filtroEstado != "Todos" and filtroEstado != "":
                sqlStatement = sqlStatement + " and a.alum_estado = '" + filtroEstado + "'"

            #listaDB = session.query(Alumno, Nodo, Ciudad).filter_by(alum_nodo_id = filtroNodo).filter_by(alum_dni = filtroDni).join(Alumno.nodo, Alumno.ciudad)
            print(sqlStatement)
            listaDB = session.execute(sqlStatement)
 
            return render_template('administrarAlumnos.htm', nodoSelect = filtroNodo
                                                              , dniSelect = filtroDni
                                                              , educacionSelect = filtroEducacion
                                                              , estadoSelect = filtroEstado
                                                              , nodoList = nodoFiltroDB
                                                              , nivelList = nivelFiltroDB
                                                              , listaBusqueda = listaDB)

#detalle del instcripcion del alumno
@app.route('/detalleAlumno', methods=['GET'])
@login_required
def detalleAlumno():



    print ("inside detalleAlumno GET")

    id = request.args.get('id')
    alumnoDB = session.query(Alumno, Alumno_Estudio, Alumno_Experiencia).filter_by(alum_id = id).join(Alumno.estudio, Alumno.experiencia).first()
    if alumnoDB:
        nodoFiltroDB = session.query(Nodo).filter_by(nodo_estado='Activo').all()                           
        paisFiltroDB = session.query(Pais).all()
        ciudadFiltroDB = session.query(Ciudad).all()
        nivelListDB = session.query(Nivel).all() 
        return render_template('formAlumno.htm',  actionSelect = 'detalle'
                                                , alumnoSelect = alumnoDB
                                                , nodoList = nodoFiltroDB
                                                , paisList = paisFiltroDB
                                                , ciudadList = ciudadFiltroDB
                                                , nivelList = nivelListDB  
                                                )
    else:
        return render_template('error.htm', error= 'UPS...No se encontro el Alumno')


#detalle del instcripcion del alumno
@app.route('/editarAlumno', methods=['GET','POST'])
@login_required
def editarAlumno():

    
    if request.method == 'GET':
        print ("inside editarAlumno GET")

        id = request.args.get('id')
        alumnoDB = session.query(Alumno, Alumno_Estudio, Alumno_Experiencia).filter_by(alum_id = id).join(Alumno.estudio, Alumno.experiencia).first()
        if alumnoDB:    
            #poblar filtros globales
            nodoFiltroDB = session.query(Nodo).filter_by(nodo_estado='Activo').all()                           
            paisFiltroDB = session.query(Pais).all()
            ciudadFiltroDB = session.query(Ciudad).all()
            nivelListDB = session.query(Nivel).all()  
            #recuparar datos del alumno a editar          

            return render_template('formAlumno.htm',  actionSelect = 'editar'
                                                    , alumnoSelect = alumnoDB
                                                    , nodoList = nodoFiltroDB
                                                    , paisList = paisFiltroDB
                                                    , ciudadList = ciudadFiltroDB
                                                    , nivelList = nivelListDB       
                                                     )
        else:
            return render_template('error.htm', error= 'UPS...No se encontro el Alumno')

    else:
        # POST
        try:
            # guardar la modificacion en BD
            alumnoDB = session.query(Alumno, Alumno_Estudio, Alumno_Experiencia).filter_by(alum_id = request.form['form-id']).join(Alumno.estudio, Alumno.experiencia).first()
            #Tabla Alumno
            alumnoDB.Alumno.alum_nombre = request.form['form-nombre']
            alumnoDB.Alumno.alum_apellido = request.form['form-apellido']
            alumnoDB.Alumno.alum_email = request.form['form-email']
            alumnoDB.Alumno.alum_fecha_nacimiento = request.form['form-fecha-nac']
            alumnoDB.Alumno.alum_nacionalidad_id = request.form['form-nacionalidad']
            alumnoDB.Alumno.alum_telefono = request.form['form-telefono']
            alumnoDB.Alumno.alum_ciud_residencia_id = request.form['form-residencia']
            alumnoDB.Alumno.alum_nodo_id  = request.form['form-nodo']
            alumnoDB.Alumno.alum_dispositivo = request.form['form-dispositivo']
            alumnoDB.Alumno.alum_usuario_modif = login_session['sesion-usuario']
            alumnoDB.Alumno.alum_fecha_modif = datetime.datetime.now()
            #Tabla Alumno_Experiencia
            alumnoDB.Alumno_Experiencia.alex_trabajo  = request.form['form-trabajo']
            alumnoDB.Alumno_Experiencia.alex_trabajo_lugar = request.form['form-trabajo-lugar']
            alumnoDB.Alumno_Experiencia.alex_sistemas = request.form['form-sistemas']
            alumnoDB.Alumno_Experiencia.alex_sistemas_exp = request.form['form-sistemas-exp']
            alumnoDB.Alumno_Experiencia.alex_sistemas_lugar = request.form['form-sistemas-lugar']
            alumnoDB.Alumno_Experiencia.alex_motivacion = request.form['form-motivacion']
            alumnoDB.Alumno_Experiencia.alex_afectacion = request.form['form-afectacion']
            alumnoDB.Alumno_Experiencia.alex_intervencion = request.form['form-intervencion']
            #Tabla Alumno_Estudio
            # alumnoDB.Alumno_Estudio.ales_alum_dni = request.form['form-dni']
            alumnoDB.Alumno_Estudio.ales_nivel_educacion_id = request.form['form-nivel-educacion']
            alumnoDB.Alumno_Estudio.ales_nahual = request.form['form-nahual']
            alumnoDB.Alumno_Estudio.ales_estudia = request.form['form-estudia']

            
            session.commit()

            msg = 'Operacion realizada con exito.'
            return render_template('success.htm', msg = msg)        

        except SQLAlchemyError as e:
            session.rollback()
            return render_template('error.htm', error = 'Se produjo un error al guardar en la Base de Datos, contacte al Administrador.') 


# eliminar Alumno logico
@app.route('/eliminarAlumno', methods=['GET'])
@login_required
def eliminarAlumno():
        print ("inside eliminarAlumno GET")

        id = request.args.get('id')
        
        alumnoDB = session.query(Alumno).filter_by(alum_id = id).first()
        alumnoDB.alum_estado = 'Rechazado'
        alumnoDB.alum_fecha_modif =  datetime.datetime.now()
        alumnoDB.alum_usuario_modif = login_session['sesion-usuario']

        session.commit()
        
        msg = 'Operacion realizada con exito.'
        return render_template('success.htm', msg = msg)
 

#Inicio de instcripcion al curso
@app.route('/inscripcion', methods=['GET','POST'])
def inscripcion():

    
    if request.method == 'GET':
        print ("inside inscripcion GET")
        login_session.pop("DNI", None)
        session.rollback()
        if request.method == 'GET':
            
            return redirect(url_for('inscripcion1')) 
            #render_template('form1Alumno.htm')
        
    else:
        print ("inside inscripcion Post")
        nombre = request.args.get('form-nombre')
        apellido = request.args.get('form-apellido')
        return "<h1>Bienvenido " + apellido + ", " + nombre + "</h1>"

 
      
@app.route('/inscripcion1', methods=['GET','POST'])
def inscripcion1():

    error = ''
     #poblar filtros globales
    nodoFiltroDB = session.query(Nodo).filter_by(nodo_estado='Activo').all()                           
    paisFiltroDB = session.query(Pais).all()
    ciudadFiltroDB = session.query(Ciudad).all()

    if request.method == 'GET':
        print ("inside inscripcion1 GET")
        
        return render_template('form1Alumno.htm', nodoList = nodoFiltroDB
                                                , paisList = paisFiltroDB
                                                , ciudadList = ciudadFiltroDB)
            
            
    else:

        if request.method == 'POST':
            print ("inside inscripcion1 Post")
            #form_action = request.form['action']
            form_dni = request.form['form-dni']
            form_nombre = request.form['form-nombre']
            form_apellido = request.form['form-apellido']
            form_email = request.form['form-email']
            form_fecha_nac = request.form['form-fecha-nac']
            form_nacionalidad = request.form['form-nacionalidad']
            form_telefono = request.form['form-telefono']
            form_residencia = request.form['form-residencia']
            #form_otro = request.form['form-otro']
            form_nodo = request.form['form-nodo']
            form_trabajo = request.form['form-trabajo']
            form_trabajo_lugar = request.form['form-trabajo-lugar']
            form_dispositivo = request.form['form-dispositivo'] 
            form_sistemas_exp = request.form['form-sistemas-exp']
            form_sistemas_lugar = request.form['form-sistemas-lugar']
            form_sistemas = request.form['form-sistemas']
            form_nivel_educacion =  request.form['form-nivel-educacion']
            form_estudia = request.form['form-estudia']
            form_nahual = request.form['form-nahual']
            form_motivacion = request.form['form-motivacion']
            form_intervencion = request.form['form-intervencion']
            form_afectacion = request.form['form-afectacion']
           
            alumnoDB = session.query(Alumno).filter_by(alum_dni = form_dni).first()
            if alumnoDB:
                error = "Alumno ya registrado con el DNI ingresado."
                return render_template('form1Alumno.htm', error = error
                                                        , nodoList = nodoFiltroDB
                                                        , paisList = paisFiltroDB
                                                        , ciudadList = ciudadFiltroDB)
        
            #return redirect(url_for('inscripcion2'))
            nivelListDB = session.query(Nivel).all()
        
            return render_template('form2Alumno.htm', nivelList = nivelListDB                               
                                                    , post_nombre = form_nombre 
                                                    , post_apellido = form_apellido 
                                                    , post_email = form_email 
                                                    , post_dni = form_dni 
                                                    , post_fecha_nac = form_fecha_nac 
                                                    , post_nacionalidad = form_nacionalidad 
                                                    , post_telefono = form_telefono 
                                                    , post_residencia = form_residencia 
                                                    , post_nodo = form_nodo 
                                                    , post_trabajo = form_trabajo 
                                                    , post_trabajo_lugar = form_trabajo_lugar
                                                    , post_dispositivo = form_dispositivo 
                                                    , post_sistemas_exp =  form_sistemas_exp 
                                                    , post_sistemas = form_sistemas 
                                                    , post_sistemas_lugar = form_sistemas_lugar
                                                    , post_nivel_educacion = form_nivel_educacion 
                                                    , post_estudia = form_estudia 
                                                    , post_nahual = form_nahual
                                                    , post_motivacion = form_motivacion
                                                    , post_intervencion = form_intervencion
                                                    , post_afectacion = form_afectacion)
            

@app.route('/inscripcion2', methods=['GET','POST'])
def inscripcion2():

    nivelListDB = session.query(Nivel).all()
    nodoFiltroDB = session.query(Nodo).all()
    paisFiltroDB = session.query(Pais).all()
    ciudadFiltroDB = session.query(Ciudad).all()

    if request.method == 'GET':
        print ("inside inscripcion2 GET")
        
        return render_template('form2Alumno.htm', nivelList = nivelListDB)             
        
    else:

        if request.method == 'POST':
                print ("inside inscripcion2 POST")

                form_dni = request.form['form-dni']
                form_nombre = request.form['form-nombre']
                form_apellido = request.form['form-apellido']
                form_email = request.form['form-email']
                form_fecha_nac = request.form['form-fecha-nac']
                form_nacionalidad = request.form['form-nacionalidad']
                form_telefono = request.form['form-telefono']
                form_residencia = request.form['form-residencia']
                #form_otro = request.form['form-otro']
                form_nodo = request.form['form-nodo']
                form_trabajo = request.form['form-trabajo']
                form_trabajo_lugar = request.form['form-trabajo-lugar']
                form_dispositivo = request.form['form-dispositivo'] 
                form_sistemas_exp = request.form['form-sistemas-exp']
                form_sistemas_lugar = request.form['form-sistemas-lugar']
                form_sistemas = request.form['form-sistemas']
                form_nivel_educacion =  request.form['form-nivel-educacion']
                form_estudia = request.form['form-estudia']
                form_nahual = request.form['form-nahual']
                form_motivacion = request.form['form-motivacion']
                form_intervencion = request.form['form-intervencion']
                form_afectacion = request.form['form-afectacion']
 
                print(request.form['action'])
                if request.form['action'] == "inscripcion1":
                    #return redirect(url_for('inscripcion1'))
                    return render_template('form1Alumno.htm', nodoList = nodoFiltroDB
                                                            , paisList = paisFiltroDB
                                                            , ciudadList = ciudadFiltroDB
                                                            , post_nombre = form_nombre 
                                                            , post_apellido = form_apellido 
                                                            , post_email = form_email 
                                                            , post_dni = form_dni 
                                                            , post_fecha_nac = form_fecha_nac 
                                                            , post_nacionalidad = form_nacionalidad 
                                                            , post_telefono = form_telefono 
                                                            , post_residencia = form_residencia 
                                                            , post_nodo = form_nodo 
                                                            , post_trabajo = form_trabajo 
                                                            , post_trabajo_lugar = form_trabajo_lugar
                                                            , post_dispositivo = form_dispositivo 
                                                            , post_sistemas_exp = form_sistemas_exp 
                                                            , post_sistemas = form_sistemas 
                                                            , post_sistemas_lugar = form_sistemas_lugar
                                                            , post_nivel_educacion = form_nivel_educacion 
                                                            , post_estudia = form_estudia 
                                                            , post_nahual = form_nahual
                                                            , post_motivacion= form_motivacion
                                                            , post_intervencion = form_intervencion
                                                            , post_afectacion= form_afectacion)
                else:
                    if request.form['action'] == "inscripcion2":
                        return render_template('form2Alumno.htm', nivelList = nivelListDB                               
                                                                , post_nombre = form_nombre 
                                                                , post_apellido = form_apellido 
                                                                , post_email = form_email 
                                                                , post_dni = form_dni 
                                                                , post_fecha_nac = form_fecha_nac
                                                                , post_nacionalidad = form_nacionalidad 
                                                                , post_telefono = form_telefono 
                                                                , post_residencia = form_residencia 
                                                                , post_nodo = form_nodo 
                                                                , post_trabajo = form_trabajo 
                                                                , post_trabajo_lugar = form_trabajo_lugar
                                                                , post_dispositivo = form_dispositivo 
                                                                , post_sistemas_exp = form_sistemas_exp 
                                                                , post_sistemas = form_sistemas 
                                                                , post_sistemas_lugar = form_sistemas_lugar
                                                                , post_nivel_educacion = form_nivel_educacion 
                                                                , post_estudia = form_estudia 
                                                                , post_nahual = form_nahual
                                                                , post_motivacion= form_motivacion
                                                                , post_intervencion = form_intervencion
                                                                , post_afectacion = form_afectacion)
                    else:
                        if request.form['action'] == "inscripcion3":

                            return render_template('form3Alumno.htm', post_nombre = form_nombre
                                                                    , post_apellido = form_apellido
                                                                    , post_email = form_email
                                                                    , post_dni = form_dni
                                                                    , post_fecha_nac = form_fecha_nac
                                                                    , post_nacionalidad = form_nacionalidad
                                                                    , post_telefono = form_telefono
                                                                    , post_residencia = form_residencia
                                                                    , post_nodo = form_nodo
                                                                    , post_trabajo = form_trabajo
                                                                    , post_trabajo_lugar = form_trabajo_lugar
                                                                    , post_dispositivo = form_dispositivo
                                                                    , post_sistemas = form_sistemas
                                                                    , post_sistemas_exp = form_sistemas_exp
                                                                    , post_sistemas_lugar = form_sistemas_lugar
                                                                    , post_nivel_educacion = form_nivel_educacion
                                                                    , post_estudia = form_estudia
                                                                    , post_nahual = form_nahual
                                                                    , post_motivacion = form_motivacion
                                                                    , post_intervencion = form_intervencion
                                                                    , post_afectacion = form_afectacion)


@app.route('/inscripcion3', methods=['GET','POST'])
def inscripcion3():
    
    if request.method == 'GET':
        return render_template('form3Alumno.htm')
    else:
        if request.method == 'POST':

            form_dni = request.form['form-dni']
            form_nombre = request.form['form-nombre']
            form_apellido = request.form['form-apellido']
            form_email = request.form['form-email']
            form_fecha_nac = request.form['form-fecha-nac']
            form_nacionalidad = request.form['form-nacionalidad']
            form_telefono = request.form['form-telefono']
            form_residencia = request.form['form-residencia']
            #form_otro = request.form['form-otro']
            form_nodo = request.form['form-nodo']
            form_trabajo = request.form['form-trabajo']
            form_trabajo_lugar = request.form['form-trabajo-lugar']
            form_dispositivo = request.form['form-dispositivo'] 
            form_sistemas_exp = request.form['form-sistemas-exp']
            form_sistemas_lugar = request.form['form-sistemas-lugar']
            form_sistemas = request.form['form-sistemas']
            form_nivel_educacion =  request.form['form-nivel-educacion']
            form_estudia = request.form['form-estudia']
            form_nahual = request.form['form-nahual']
            form_motivacion = request.form['form-motivacion']
            form_intervencion = request.form['form-intervencion']
            form_afectacion = request.form['form-afectacion']

            if request.form['action'] == "inscripcion2":

                nivelListDB = session.query(Nivel).all()
                return render_template('form2Alumno.htm', nivelList = nivelListDB                               
                                                        , post_nombre = form_nombre 
                                                        , post_apellido = form_apellido 
                                                        , post_email = form_email 
                                                        , post_dni = form_dni 
                                                        , post_fecha_nac = form_fecha_nac 
                                                        , post_nacionalidad = form_nacionalidad 
                                                        , post_telefono = form_telefono 
                                                        , post_residencia = form_residencia 
                                                        , post_nodo = form_nodo 
                                                        , post_trabajo = form_trabajo 
                                                        , post_trabajo_lugar = form_trabajo_lugar
                                                        , post_dispositivo = form_dispositivo 
                                                        , post_sistemas_exp = form_sistemas_exp 
                                                        , post_sistemas = form_sistemas 
                                                        , post_sistemas_lugar = form_sistemas_lugar
                                                        , post_nivel_educacion = form_nivel_educacion 
                                                        , post_estudia = form_estudia 
                                                        , post_nahual = form_nahual
                                                        , post_motivacion= form_motivacion
                                                        , post_intervencion = form_intervencion
                                                        , post_afectacion = form_afectacion)
            else:
                
                nuevoAlumnoDB = Alumno (
                alum_dni = request.form['form-dni'],
                alum_nombre = request.form['form-nombre'],
                alum_apellido = request.form['form-apellido'],
                alum_email = request.form['form-email'],
                alum_fecha_nacimiento = request.form['form-fecha-nac'],
                alum_nacionalidad_id = request.form['form-nacionalidad'],
                alum_telefono = request.form['form-telefono'],
                alum_ciud_residencia_id = request.form['form-residencia'],
                alum_nodo_id  = request.form['form-nodo'],
                alum_dispositivo = bool(int(request.form['form-dispositivo'])),
                alum_estado = 'Pendiente',
                alum_fecha_alta = datetime.datetime.now()
                )
                session.add(nuevoAlumnoDB)

                alumnoDB = session.query(Alumno).filter_by(alum_dni = request.form['form-dni']).first()
                
                nuevoAlumnoExpDB = Alumno_Experiencia (
                alex_alum_id = alumnoDB.alum_id,
                alex_trabajo  = bool(int(request.form['form-trabajo'])),
                alex_trabajo_lugar = request.form['form-trabajo-lugar'],
                alex_sistemas = bool(int(request.form['form-sistemas'])),
                alex_sistemas_exp = bool(int(request.form['form-sistemas-exp'])),
                alex_sistemas_lugar = request.form['form-sistemas-lugar'],
                alex_motivacion = request.form['form-motivacion'],
                alex_afectacion = request.form['form-afectacion'],
                alex_intervencion = request.form['form-intervencion']
                )
                session.add(nuevoAlumnoExpDB)

                nuevoAlumnoEstudioDB = Alumno_Estudio (
                ales_alum_id = alumnoDB.alum_id,
                ales_nivel_educacion_id = request.form['form-nivel-educacion'],
                ales_nahual = request.form['form-nahual'],
                ales_estudia = bool(int(request.form['form-estudia']))
                )
                session.add(nuevoAlumnoEstudioDB)
            
                session.commit()


                return redirect(url_for('finInscripcion'))
            
#fin  de instcripcion al curso
@app.route('/finInscripcion', methods=['GET','POST'])
def finInscripcion():

    print ("inside finInscripcion GET")
    
    if request.method == 'GET':
            
        return render_template('finInscripcion.htm')
    
    else:
        if request.method == 'POST':

            return render_template('index.html', sesion_usuario=login_session ['sesion-usuario'])



if __name__ == '__main__':
    
    app.secret_key = 'secret key'
    app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(minutes=30)
    app.debug = False
    app.run(host = '0.0.0.0', port = 8000, debug=True)
    
    
