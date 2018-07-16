from selenium import webdriver
from selenium.webdriver.common.keys import Keys

def imprimir(nombre):
	# Obtenemos el id del cuadro de busqueda y lo limpiamos
	search_field = driver.find_element_by_id("userAB") #EN CASO DE NO SER ESE EL ID, EL ID ES buscarU
	search_field.clear()
	# Realizamos una busqueda
	search_field.send_keys(nombre)
	search_field.submit()

	# Obtenemos la lista de elementos cuya clase posee este nombre (enlaces)
	lists = driver.find_elements_by_class_name("nombre-usuario")

	if len(lists)>0:
		# Imprimimos el numero de elementos encontrados
		print ("Encontrados " + str(len(lists)) + " usuarios:")

		# Iteramos sobre cada elemento e imprimimos su valor
		i = 0
		for listitem in lists:
			print (listitem.text)
			i = i+1
			if(i>10):
				break
	else:
		print ("No se encontraron resultados")
	print ()


# Creamos una nueva sesion en Chrome
driver = webdriver.Chrome()
driver.implicitly_wait(20)
driver.maximize_window()

# Navegamos a la pagina principal de ATIstagram
driver.get("http://localhost:5000")

# Obtenemos el id del cuadro de usuario y lo limpiamos
user = driver.find_element_by_id("email")
user.clear()

# Obtenemos el id del cuadro de contraseña y lo limpiamos
password = driver.find_element_by_id("password")
password.clear()

# Iniciamos Sesion
user.send_keys("dannyelportu2013@gmail.com")
password.send_keys("123")
password.submit()


imprimir("Evencio")
#driver.implicitly_wait(2000)
imprimir("Danny Caldeira")
#driver.implicitly_wait(2000)
imprimir("Ninguno")

# close the browser window
driver.quit()
