from flask import Flask, render_template, request, session
from werkzeug.utils import secure_filename
from pymongo import *
from bson.objectid import ObjectId
import os
import datetime
import tweepy

app = Flask(__name__, template_folder='templates', static_folder='static')

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
		return render_template('inicio.html', user = session, data = newPost(None,session["username"]))
	#El usuario no ha iniciado sesion
	return render_template('index.html', data = newPost("Publico",None))

@app.route('/registro')
@app.route('/registrarse')
def registrarse():
	return render_template('registro.html')

@app.route('/iniciar-sesion')
def iniciarSesion():
	return render_template('index.html', data = newPost("Publico",None))

@app.route('/recuperarC')
def gotoRecupContra():
	return render_template('recuperarContraseña.html')

@app.route('/miPerfil')
def goToPerfil():
	if 'username' in session:
		#El usuario tiene sesion abierta
		userInfo = usuarios.find_one({"userName": session['username']})
		return render_template('miPerfil.html', user = session, data = newPost("perfil",session["username"]), info = userInfo)
	#El usuario no ha iniciado sesion
	return render_template('index.html', data = newPost("Publico",None))

@app.route('/notificaciones')
def goToNotificaciones():
	if 'username' in session:
		#El usuario tiene sesion abierta
		return render_template('Notificaciones.html', user = session)
	#El usuario no ha iniciado sesion
	return render_template('index.html', data = newPost("Publico",None))

@app.route('/salvarPerfil')
@app.route('/editarPerfil')
def goToEditPerfil():
	if 'username' in session:
		#El usuario tiene sesion abierta
		data = usuarios.find_one({ "userName": session["username"] })
		return render_template('EditarPerfil.html', user = session, datos = data)
	#El usuario no ha iniciado sesion
	return render_template('index.html', data = newPost("Publico",None))

@app.route('/cargarFoto')
def goToCargarFoto():
	if 'username' in session:
		#El usuario tiene sesion abierta
		return render_template('cargarFoto.html', user = session)
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
		return render_template('inicio.html', user = session, data = newPost(None,session["username"]))
	#El usuario no ha iniciado sesion
	return render_template('index.html', data = newPost("Publico",None))

@app.route('/seguirUsuario')
@app.route('/buscarUsuario')
def goToBuscarU():
	if 'username' in session:
		#El usuario tiene sesion abierta
		return render_template('BuscarUsuario.html', user = session)
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
		return render_template('inicio.html', user = session, data = newPost(None,user["userName"]))
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
		session['username'] = data['userName']
		session['nombre'] = data["nombre"]+" "+data["apellido"]
		if 'imagenP' in request.files:
			#Validamos que le archivo se haya recibido bien
			file = request.files['imagenP']
			if guardar_Imagen(file,"p") == 1:
				data["fotoP"]="perfil.jpg"
				
		if 'imagenF' in request.files:
			#Validamos que le archivo se haya recibido bien
			file = request.files['imagenF']
			if guardar_Imagen(file,"F") == 1:
				data["fotoF"]="fondo.jpg"
		
		db.usuarios.insert_one(data)
		return render_template('Inicio.html', user = session, data = newPost(None,data["userName"]))
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
		return render_template('BuscarUsuario.html', user = session, flag = x, datos = resuls, tam = resuls.count())
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
			return render_template('cargarFoto.html', user = session, flag = 0)
		
		#Validamos que le archivo se haya recibido bien
		file = request.files['imagen']

		if file.filename == '':
			return render_template('cargarFoto.html', user = session, flag = -1)
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
			data["califc"] = []
			data["fecha"] = datetime.datetime.now()
			db.publicaciones.insert_one(data)
			return render_template('cargarFoto.html', user = session, flag = 1)
		else:
			return render_template('cargarFoto.html', user = session, flag = -2)

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
			return render_template('EditarPerfil.html', user = session, datos = userNew, flag = -1)
		
		aux = usuarios.find_one({ "email": userNew["email"] })
		if userOld["email"] != userNew["email"] and aux != None:
			#Existe el email
			userNew["email"] = ""
			return render_template('EditarPerfil.html', user = session, datos = userNew, flag = -3)
		
		aux = usuarios.find_one({ "userNameF": userNew["userNameF"] })
		if aux != None and userOld["userName"] != aux["userName"]:
			#Ya se asocio la cuenta de FB
			del(userNew["userNameF"])
			return render_template('EditarPerfil.html', user = session, datos = userNew, flag = -4)

		aux = usuarios.find_one({ "userNameT": userNew["userNameT"] })
		if aux != None and userOld["userName"] != aux["userName"]:
			#Ya se asocio la cuenta de Twitter
			del(userNew["userNameT"])
			return render_template('EditarPerfil.html', user = session, datos = userNew, flag = -5)
		if 'imagenP' in request.files:
			#Validamos que le archivo se haya recibido bien
			file = request.files['imagenP']
			if guardar_Imagen(file,"p") == 1:
				userNew["fotoP"]="perfil.jpg"
				
		if 'imagenF' in request.files:
			#Validamos que le archivo se haya recibido bien
			file = request.files['imagenF']
			if guardar_Imagen(file,"F") == 1:
				userNew["fotoF"]="fondo.jpg"

		if 'imagenF' in userNew:
			del(userNew["imagenF"])
		if 'imagenP' in userNew:
			del(userNew["imagenP"])

		if userNew["userNameF"] == "":
			del(userNew["userNameF"])
		if userNew["userNameT"] == "":
			del(userNew["userNameT"])

		del(userNew["pwdOld"])
		db.usuarios.update_one({"userName": session["username"]}, {"$set": userNew})
		
		userNew = usuarios.find_one({ "userName": session["username"] })
		return render_template('EditarPerfil.html', user = session, datos = userNew, flag = 1)
	#El usuario no ha iniciado sesion
	return render_template('index.html', data = newPost("Publico",None))

def guardar_Imagen(file,tipo):

	if file.filename == '':
		return 0
	if file and allowed_file(file.filename):
		#Definimos la ruta y nombre del archivo
		if tipo == "p":
			nombreImg = "perfil.jpg"
		else:
			nombreImg = "fondo.jpg"	
		aux = app.root_path+"\static\perfiles"
		ruta = os.path.join(aux, session['username'])
		#Si no exite la ruta la creamos
		if not os.path.exists(ruta):
			#Creamos el directorio
			os.makedirs(ruta)
		#Guardamos el archivo
		file.save(os.path.join(ruta, nombreImg))
		return 1
	else:
		return -1

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
		return render_template('inicio.html', user = session, data = newPost(None,user["userName"]))


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
		return render_template('inicio.html', user = session, data = newPost(None,user["userName"]))

#Recuperar contraseña
@app.route('/recuperarC', methods=['POST'])
def recuperarC():
	data = request.form.to_dict()
	if "pwd" in data:
		#Cambiamos la contraseña
		aux = db.usuarios.update_one({"userName": data["userN"]}, {"$set": {"pwd": data["pwd"]}})
		#Informamos el exito
		return render_template('recuperarContraseña.html',flag = 1)
	else:
		#Buscamos si existe un usuario con el email o el userName
		aux = usuarios.find_one({ "email": data['email'] })
		aux2 = usuarios.find_one({ "userName": data['userName'] })
		
		if aux is None and aux2 is None:
			#No hay usuario con ese email o nombre de usuario
			return render_template('recuperarContraseña.html',flag = -1)
		elif aux is None:
			#No existe el email
			return render_template('recuperarContraseña.html',flag = -2)
		elif aux2 is None:
			#No existe el userName
			return render_template('recuperarContraseña.html',flag = -3)
		elif aux["userName"] == aux2["userName"]:
			#Datos correctos, cambiamos la contraseña
			return render_template('recuperarContraseña.html',userName = data["userName"])
		else:
			#Datos incorrectos
			return render_template('recuperarContraseña.html',flag = -4)

#Calificar un post
@app.route('/calificar', methods=['POST'])
def calificar():
	if 'username' in session:
	#El usuario tiene sesion abierta
		data = request.form.to_dict()
		aux = publicaciones.find_one({ "_id": ObjectId(data["id"]) })
		#Validamos que el usuario no haya califiado ya la foto
		if aux is None:
			return "error"
		#Creamos la calificacion
		dictAux = dict(valor= data["valor"], nombre= session['nombre'], userName= session['username'], fecha= datetime.datetime.now())
		array = []
		array.append(dictAux)
		#Validamos si el usuario ya califico la foto
		for x in range(len(aux["califc"])):
			#Si no es del mismo usuario la encolamos en el arreglo
			if session['username'] != aux["califc"][x]["userName"]:
				array.append(aux["califc"][x])

		publicaciones.update_one({"_id": aux["_id"]}, {"$set": {"califc": array}})
		return "exito"
	#El usuario no ha iniciado sesion
	return "salir"

#Devuelve las publicaciones mas nuevas segun el tipo o usuario
def newPost(tipo,userN):
	if userN is None:
		#buscamos segun el tipo
		data = db.publicaciones.find({"seguridad": "Publico"}).sort("fecha", -1).limit(20)
		return data
	elif tipo=="perfil":
		data = db.publicaciones.find({"userName": session["username"]}).sort("fecha", -1).limit(20)
		return data	
	else:
		seguidos = list(db.sigue.find({"userName_1": userN},{ "_id": 0,"userName_2": 1 }))
		aux = []
		for x in seguidos:
			aux.append(x["userName_2"])
		#Buscamos segun el usuario
		data = db.publicaciones.find({"$or":[{"userName": userN},{"userName": { "$in": aux}}]}).sort("fecha", -1).limit(20)

		return data

#Inicio del Servidor
if __name__ == '__main__':
	app.debug = True
	app.run()