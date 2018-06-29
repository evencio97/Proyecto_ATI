from flask import Flask, render_template, request
from pymongo import *
 
app = Flask(__name__, template_folder = 'templates', static_folder = 'static')

# MongoDB Connection with PyMongo
client = MongoClient()

db = client.db_atistagram
usuarios = db.usuarios

# Routes Definition
@app.route('/')
def index():
	return render_template('index.html')

@app.route('/registrarse')
def registrarse():
	return render_template('registro.html')

@app.route('/iniciar-sesion')
def iniciarSesion():
	return render_template('index.html')

#Methos definition
#Inicio de Sesion
@app.route('/login', methods=['POST'])
def login():
	email = request.form['email']
	password  = request.form['password']

	user = usuarios.find_one({ "email": email })
	if user["pwd"] == password:
		return render_template('inicio.html', nombre = user["nombre"])
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

#Inicio del Servidor
if __name__ == '__main__':
	app.debug = True
	app.run()