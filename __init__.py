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

@app.route('/login', methods=['POST'])
def login():
	email = request.form['email']
	password  = request.form['password']

	user = usuarios.find_one({ "email": email })
	if user["pwd"] == password:
		return render_template('inicio.html', nombre = user["usuario"])
	return render_template('index.html', error = 1)

if __name__ == '__main__':
	app.debug = True
	app.run()