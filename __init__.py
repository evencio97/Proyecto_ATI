from flask import Flask, render_template, request, session, redirect, url_for, escape
from werkzeug.utils import secure_filename
from pymongo import *
import os
 
app = Flask(__name__, template_folder = 'templates', static_folder = 'static')

#Clave secreta para la cifrar las sesiones
app.secret_key = os.urandom(16)
# MongoDB Connection with PyMongo
client = MongoClient()

db = client.db_atistagram
usuarios = db.usuarios
sigue = db.sigue
publicaciones = db.publicaciones

#extenciones aceptadas
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

# Routes Definition
@app.route('/')
def index():
	if 'username' in session:
		#El usuario tiene sesion abierta
		return render_template('inicio.html', user = session['username'])
	#El usuario no ha iniciado sesion
	return render_template('index.html')

@app.route('/registro')
@app.route('/registrarse')
def registrarse():
	return render_template('registro.html')

@app.route('/iniciar-sesion')
def iniciarSesion():
	return render_template('index.html')

@app.route('/miPerfil')
def goToPerfil():
	if 'username' in session:
		#El usuario tiene sesion abierta
		return render_template('miPerfil.html')
	#El usuario no ha iniciado sesion
	return render_template('index.html')

@app.route('/notificaciones')
def goToNotificaciones():
	if 'username' in session:
		#El usuario tiene sesion abierta
		return render_template('Notificaciones.html')
	#El usuario no ha iniciado sesion
	return render_template('index.html')

@app.route('/editarPerfil')
def goToEditPerfil():
	if 'username' in session:
		#El usuario tiene sesion abierta
		return render_template('EditarPerfil.html')
	#El usuario no ha iniciado sesion
	return render_template('index.html')

@app.route('/cargarFoto')
def goToCargarFoto():
	if 'username' in session:
		#El usuario tiene sesion abierta
		return render_template('cargarFoto.html', user = session["username"])
	#El usuario no ha iniciado sesion
	return render_template('index.html')

@app.route('/registro')

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return render_template('index.html')

@app.route('/login')
def gotoHome():	
	if 'username' in session:
		#El usuario tiene sesion abierta
		return render_template('inicio.html', user = session["username"])
	#El usuario no ha iniciado sesion
	return render_template('index.html')

@app.route('/seguirUsuario')
@app.route('/buscarUsuario')
def goToBuscarU():
	if 'username' in session:
		#El usuario tiene sesion abierta
		return render_template('BuscarUsuario.html', user = session['username'])
	#El usuario no ha iniciado sesion
	return render_template('index.html')



#Methos definition
#Inicio de Sesion
@app.route('/login', methods=['POST'])
def login():
	email = request.form['email']
	password  = request.form['password']

	user = usuarios.find_one({ "email": email })
	if user["pwd"] == password:
		session['username'] = user['userName']
		return render_template('inicio.html', user = user["userName"])
	return render_template('index.html', error = 1)

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
		return render_template('registro.html', exito = 1)
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
		return render_template('BuscarUsuario.html', user = session['username'], flag = x, datos = resuls, tam = resuls.count())
	#El usuario no ha iniciado sesion
	return render_template('index.html')

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
			return render_template('cargarFoto.html', user = session["username"], flag = 0)
		
		#Validamos que le archivo se haya recibido bien
		file = request.files['imagen']

		if file.filename == '':
			return render_template('cargarFoto.html', user = session["username"], flag = -1)
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
			data["imagen"] = os.path.join(ruta, nombreImg)
			db.publicaciones.insert_one(data)
			return render_template('cargarFoto.html', user = session["username"], flag = 1)
		else:
			return render_template('cargarFoto.html', user = session["username"], flag = -2)

	#El usuario no ha iniciado sesion
	return render_template('index.html')



#Inicio del Servidor
if __name__ == '__main__':
	app.debug = True
	app.run()