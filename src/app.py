#!/usr/bin/env python3

#Importamos las librerías que vamos a usar en nuestro código.
import os
from pexpect import pxssh
from flask import Flask, render_template

#Variable que almacena un objeto heredado de Flask

app=Flask(__name__)	


#Variables que obtienen el valor de una variable de entorno del sistema
sshpass=os.getenv('SSH_PASS')
sshuser=os.getenv('SSH_USER')
sship=os.getenv('SSH_IP')


#Variable para la conexión por ssh y todos los comandos que éste implica
s = pxssh.pxssh()

#Condicional que se intenta conectar con los parámetros introducidos anteriormente.
#En el caso de que no se establezca conexión el programa dará un mensaje de error
# por lo contrario el programa continuará.

if not s.login ( sship , sshuser , sshpass ):
    print ("SSH session failed on login.")
    print (str(s))
else:
    #print ("SSH session login successful")
    s.sendline ('ansible all --list-host')
    s.prompt()
    s.sendline ('ansible all -m copy -a "src=/html/ dest=/var/www/html"')
    print (s.before.decode('UTF-8'))
    # s.logout()

#Página principal redireccionando a un html que ya tenemos.
@app.route('/')
def inicio():
    return render_template("inicio.html")

#Página de actualizaciones
@app.route('/iapache/')
def update():
    s.sendline ('ansible-playbook /etc/ansible/apache.yaml')
    s.prompt()         # match the prompt
    print (s.before.decode('UTF-8'))
    return render_template("instalarapache.html")

#Página de lista
@app.route('/papache/')
def lists():
    s.sendline ('ansible-playbook /etc/ansible/desinstalarapache.yaml')
    s.prompt()
    print (s.before.decode('UTF-8'))
    return render_template("desinstalarapache.html")

#Pagina de testeo
@app.route('/rapache/')
def ping():
    s.sendline ('ansible all -a "systemctl restart apache2"')
    s.prompt()
    print (s.before.decode('UTF-8'))
    return render_template("reiniciarapache.html")

#Pagina de apagado
@app.route('/poweroff/')
def poweroff():
    s.sendline ('ansible all -a "poweroff"')
    s.prompt()
    print (s.before.decode('UTF-8'))
    return render_template("poweroff.html")

#Permitimos que se pueda acceder a través de la red por el puerto 5000
app.run("0.0.0.0",5000)
