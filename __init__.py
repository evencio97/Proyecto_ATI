from flask import Flask, render_template, request, session, redirect, url_for, escape
from werkzeug.utils import secure_filename
from pymongo import *
import os
import datetime
import facebook
import tweepy
from itertools import chain

app = Flask(__name__, template_folder = 'templates', static_folder = 'static')

#-----------Twitter-----------------------
CONSUMER_KEY = 'F5jfpDLAJYcOlXXbqdx8lb9Rl'
CONSUMER_SECRET = 'gh3NfO2caBPVlfNtJLZ7dPGgzQmDZoKKhmjEHx4ZfRnvw20HB9'
ACCESS_TOKEN = '260342983-BCMoR7AY2R7mdsvkDIpSV2vY9APmxRVV70WaSLEm'
ACCESS_TOKEN_SECRET = 'wTdjF5NaSn5mPLAlwrjvdY6YZQ7jstZNpdnzIakEMHbjY'
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

api = None

#Clave secreta para la cifrar las sesiones
app.secret_key = os.urandom(16)
# MongoDB Connection with PyMongo
client = MongoClient()

db = client.db_atistagram
usuarios = db.usuarios
sigue = db.sigue
publicaciones = db.publicaciones
calificaciones = db.calificaciones

#extenciones aceptadas
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

# Routes Definition
@app.route('/')
def index():
	if 'username' in session:
		#El usuario tiene sesion abierta
		return render_template('inicio.html', user = session['nombre'], data = newPost(None,session["username"]))
	#El usuario no ha iniciado sesion
	return render_template('index.html', data = newPost("Publico",None))

@app.route('/registro')
@app.route('/registrarse')
def registrarse():
	return render_template('registro.html')

@app.route('/iniciar-sesion')
def iniciarSesion():
	return render_template('index.html', data = newPost("Publico",None))

@app.route('/miPerfil')
def goToPerfil():
	if 'username' in session:
		#El usuario tiene sesion abierta
		return render_template('miPerfil.html', user = session['nombre'])
	#El usuario no ha iniciado sesion
	return render_template('index.html', data = newPost("Publico",None))

@app.route('/notificaciones')
def goToNotificaciones():
	if 'username' in session:
		#El usuario tiene sesion abierta
		return render_template('Notificaciones.html', user = session['nombre'])
	#El usuario no ha iniciado sesion
	return render_template('index.html', data = newPost("Publico",None))

@app.route('/salvarPerfil')
@app.route('/editarPerfil')
def goToEditPerfil():
	if 'username' in session:
		#El usuario tiene sesion abierta
		data = usuarios.find_one({ "userName": session["username"] })
		return render_template('EditarPerfil.html', user = session['nombre'], datos = data)
	#El usuario no ha iniciado sesion
	return render_template('index.html', data = newPost("Publico",None))

@app.route('/cargarFoto')
def goToCargarFoto():
	if 'username' in session:
		#El usuario tiene sesion abierta
		return render_template('cargarFoto.html', user = session['nombre'])
	#El usuario no ha iniciado sesion
	return render_template('index.html', data = newPost("Publico",None))

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return render_template('index.html', data = newPost("Publico",None))

@app.route('/t_login')
@app.route('/f_login')
@app.route('/login')
def gotoHome():	
	if 'username' in session:
		#El usuario tiene sesion abierta
		return render_template('inicio.html', user = session['nombre'], data = newPost(None,session["username"]))
	#El usuario no ha iniciado sesion
	return render_template('index.html', data = newPost("Publico",None))

@app.route('/seguirUsuario')
@app.route('/buscarUsuario')
def goToBuscarU():
	if 'username' in session:
		#El usuario tiene sesion abierta
		return render_template('BuscarUsuario.html', user = session['nombre'])
	#El usuario no ha iniciado sesion
	return render_template('index.html', data = newPost("Publico",None))



#Methos definition
#Inicio de Sesion
@app.route('/login', methods=['POST'])
def login():
	email = request.form['email']
	password  = request.form['password']

	user = usuarios.find_one({ "email": email })
	if user is None:
		return render_template('index.html', error = 2, data = newPost("Publico",None))
	elif user["pwd"] == password:
		session['username'] = user['userName']
		session['nombre'] = user["nombre"]+" "+user["apellido"]
		return render_template('inicio.html', user = session['nombre'], data = newPost(None,user["userName"]))
	return render_template('index.html', error = 1, data = newPost("Publico",None))

#Registro de Usuario
@app.route('/registro', methods=['POST'])
def registro():
	email = request.form['email']
	userName  = request.form['userName']

	user = usuarios.find_one({ "email": email })
	user2 = usuarios.find_one({ "userName": userName })
	if request.form['pwd'] != request.form['pwd2']:
		#Las contraseñas no son iguales
		return render_template('registro.html', error = 4)
	elif user is None and user2 is None:
		#No hay otro usuario con ese email o nombre de usuario, registramos al usuario
		data = request.form.to_dict()
		del(data["pwd2"])
		db.usuarios.insert_one(data)
		return render_template('Inicio.html', user = session['nombre'], data = newPost(None,data["userName"]))
	elif user != None and user2 != None:
		#Existe el email y el userName
		return render_template('registro.html', error = 1)
	elif user != None:
		#Existe el email
		return render_template('registro.html', error = 2)
	elif user2 != None:
		#Existe el nombre de usuario
		return render_template('registro.html', error = 3)

#Buscar Usuario
@app.route('/buscarUsuario', methods=['POST'])
def buscarU():
	if 'username' in session:
		#El usuario tiene sesion abierta
		data = request.form['userB'].split(" ")
		tam = len(data)
		x = 1
		if (tam == 1):
			resuls = db.usuarios.find({"nombre": data[0]},{ "_id": 0,"userName": 1, "nombre": 1, "apellido": 1 })
		elif (tam == 2):
			resuls = db.usuarios.find({"nombre": data[0],"apellido": data[1]},{ "_id": 0,"userName": 1,"nombre": 1, "apellido": 1 })
		else:
			x = 0
		return render_template('BuscarUsuario.html', user = session['nombre'], flag = x, datos = resuls, tam = resuls.count())
	#El usuario no ha iniciado sesion
	return render_template('index.html', data = newPost("Publico",None))

@app.route('/seguirUsuario', methods=['POST'])
def seguirU():
	if 'username' in session:
		#El usuario tiene sesion abierta
		data = request.form['userN']
		
		if (session['username']==data):
			return "mismo"
		elif (sigue.find_one({ "userName_1": session['username'],"userName_2": data} ) is None):
			#Como no existe creamos la relacion de seguimiento
			db.sigue.insert_one({ "userName_1": session['username'],"userName_2": data })
			return "listo"
		#Ya el usuario sigue al otro
		return "existe"

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/cargarFoto', methods=['POST'])
def cargarF():
	if 'username' in session:
		#El usuario tiene sesion abierta
		if 'imagen' not in request.files:
			return render_template('cargarFoto.html', user = session['nombre'], flag = 0)
		
		#Validamos que le archivo se haya recibido bien
		file = request.files['imagen']

		if file.filename == '':
			return render_template('cargarFoto.html', user = session['nombre'], flag = -1)
		if file and allowed_file(file.filename):
			#Definimos la ruta y nombre del archivo
			nombreImg = secure_filename(file.filename)
			aux = app.root_path+"\static\publicaciones"
			ruta = os.path.join(aux, session['username'])
			#Si no exite la ruta la creamos
			if not os.path.exists(ruta):
				#Creamos el directorio
				os.makedirs(ruta)
        	#Guardamos el archivo
			file.save(os.path.join(ruta, nombreImg))
			#Guardamos la publicacion en la BD
			data = request.form.to_dict()
			data["userName"] = session['username']
			data["nombre"] = session['nombre']
			data["imagen"] = "../static/publicaciones/"+session['username']+"/"+nombreImg
			data["seguridad"] = usuarios.find_one({ "userName": session['username'] })["seguridad"]
			data["fecha"] = datetime.datetime.now()
			db.publicaciones.insert_one(data)
			return render_template('cargarFoto.html', user = session['nombre'], flag = 1)
		else:
			return render_template('cargarFoto.html', user = session['nombre'], flag = -2)

	#El usuario no ha iniciado sesion
	return render_template('index.html', data = newPost("Publico",None))

@app.route('/twitter',methods=['POST'])
def twitter_login():
	global api
	api = tweepy.API(auth)
	user = api.me()
	return user.screen_name

@app.route('/salvarPerfil',methods=['POST'])
def salvarPerfil():
	if 'username' in session:
		#El usuario tiene sesion abierta
		userNew = request.form.to_dict()

		userOld = usuarios.find_one({ "userName": session['username'] })
		if request.form['pwdOld'] != userOld["pwd"]:
			#Las contraseñas no son iguales
			return render_template('EditarPerfil.html', user = session['nombre'], datos = userNew, flag = -1)
		
		aux = usuarios.find_one({ "userName": userNew["userName"] })
		if userOld["userName"] != userNew["userName"] and aux != None:
			#Existe el userName escoguido
			userNew["userName"] = ""
			return render_template('EditarPerfil.html', user = session['nombre'], datos = userNew, flag = -2)
		
		aux = usuarios.find_one({ "email": userNew["email"] })
		if userOld["email"] != userNew["email"] and aux != None:
			#Existe el email
			userNew["email"] = ""
			return render_template('EditarPerfil.html', user = session['nombre'], datos = userNew, flag = -3)
		
		aux = usuarios.find_one({ "userNameF": userNew["userNameF"] })
		if aux != None and userOld["userName"] != aux["userName"]:
			#Ya se asocio la cuenta de FB
			del(userNew["userNameF"])
			return render_template('EditarPerfil.html', user = session['nombre'], datos = userNew, flag = -4)

		aux = usuarios.find_one({ "userNameT": userNew["userNameT"] })
		if aux != None and userOld["userName"] != aux["userName"]:
			#Ya se asocio la cuenta de Twitter
			del(userNew["userNameT"])
			return render_template('EditarPerfil.html', user = session['nombre'], datos = userNew, flag = -5)
		
		db.usuarios.delete_one({'userName': userOld["userName"]})
		session["username"] = userNew["userName"]
		session["nombre"] = userNew["nombre"]+" "+userNew["apellido"]
		del(userNew["pwdOld"])
		db.usuarios.insert_one(userNew)
		return render_template('EditarPerfil.html', user = session['nombre'], datos = userNew, flag = 1)
	#El usuario no ha iniciado sesion
	return render_template('index.html', data = newPost("Publico",None))

#Inicio de Sesion con las Redes
@app.route('/f_login', methods=['POST'])
def f_login():
	userFB = request.form['userNameF']

	#Iniciamos con FB
	user = usuarios.find_one({ "userNameF": userFB })

	if user is None:
		return render_template('index.html', error = 4, data = newPost("Publico",None))
	else:
		session['username'] = user['userName']
		session['nombre'] = user["nombre"]+" "+user["apellido"]
		return render_template('inicio.html', user = session['nombre'], data = newPost(None,user["userName"]))


@app.route('/t_login', methods=['POST'])
def t_login():
	userT  = request.form['userNameT']

	#Iniciamos con Twitter
	user = usuarios.find_one({ "userNameT": userT })

	if user is None:
		return render_template('index.html', error = 5, data = newPost("Publico",None))
	else:
		session['username'] = user['userName']
		session['nombre'] = user["nombre"]+" "+user["apellido"]
		return render_template('inicio.html', user = session['nombre'], data = newPost(None,user["userName"]))

#Devuelve las publicaciones mas nuevas segun el tipo o usuario
def newPost(tipo,userN):
	if userN is None:
		#buscamos segun el tipo
		data = db.publicaciones.find({"seguridad": "Publico"}).sort("fecha", -1).limit(20)
		return data
	else:
		seguidos = list(db.sigue.find({"userName_1": userN},{ "_id": 0,"userName_2": 1 }))
		aux = []
		for x in seguidos:
			aux.append(x["userName_2"])
		#Buscamos segun el usuario
		data = db.publicaciones.find({"$or":[{"userName": userN},{"userName": { "$in": aux}}]}).sort("fecha", -1)
		return data

#Inicio del Servidor
if __name__ == '__main__':
	app.debug = True
	app.run()