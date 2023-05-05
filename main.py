from flask import Flask, request, make_response, redirect, render_template, session, url_for, flash
from flask_mysqldb import MySQL
from flask_bootstrap import  Bootstrap4
import mysql.connector
from datetime import datetime
from dotenv import load_dotenv
import os

#Declaracion de variables de entorno
load_dotenv()

MYSQL_HOST = os.getenv('MYSQL_HOST')
MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_DB= os.getenv('MYSQL_DB')
PORT= os.getenv('PORT')


app = Flask(__name__)
app.config.update(
    DEBUG=False
)
app.secret_key = 'Im_the_key' #llave de incriptacion de sessions

#Configuracion de la base de datos
app.config['MYSQL_HOST'] = MYSQL_HOST
app.config['MYSQL_USER'] = MYSQL_USER
app.config['MYSQL_PASSWORD'] = MYSQL_PASSWORD
app.config['MYSQL_DB'] = MYSQL_DB



mysql = MySQL(app)

bootstrap = Bootstrap4(app)

#Manejo de erroes
@app.errorhandler(404) #ERROR CLIENTE
def not_found(error):
    return render_template('/Public/404.html', error=error)

@app.errorhandler(500) #ERROR DE SERVIDOR
def internal_server_error(error):
    return render_template('/Public/500.html', error=error)

@app.route('/')#pagina principal
def index ():
    return render_template('/Public/index.html')

@app.route('/logs')#Consulta Para ver el resgistro de logs
def logs():
    if session['Admin'] == 1:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM logs ")
        data = cursor.fetchall()
        cursor.close()
        return render_template('/Public/logs.html', data=data)
    else:
        return render_template('/Public/acces_deined.html')

@app.route('/login', methods=['GET', 'POST']) #Verficiacion de credenciales
def login():
    if request.method == 'POST':
        #Se Obtiene informacion del intento de login
        username = request.form['username']
        password = request.form['password']

        # Buscar en la tabla "login" para verificar que el nombre de usuario y la contraseña sean válidos
        cursor = mysql.connection.cursor()
        consulta = "SELECT * FROM users WHERE username = %s AND password = %s"
        valores = (username, password)
        cursor.execute(consulta, valores)
        resultado = cursor.fetchone()

        if resultado is not None:
            # Si las credenciales son válidas, establecer la sesión de usuario y redirigir al usuario a la página de perfil
            session['user_id'] = resultado[0]
            session['Admin'] = resultado[8]
            if session['Admin'] == 1:
                flash(f'Bienvenido {resultado[1]}, User: Root','success')
            else:
                flash(f'Bienvenido {resultado[1]}','success')
                
            return redirect(url_for('index'))
        else:
        # Si el usuario no ha iniciado sesión o ha ingresado credenciales incorrectas, mostrar el formulario de inicio de sesión
         flash('Informacion de usuario incorrecta.','danger')
        return render_template('/Public/login.html')
    return render_template('/Public/login.html')
        

@app.route('/logout')#Cierre de sesion
def logout():
    session.clear()
    flash('Adios, esperamos verte pronto','info')
    return redirect('/')

@app.route('/perfil') #Vista individual del perfil del usuario
def perfil():
    cursor = mysql.connection.cursor()
    user_id = session['user_id']
    cursor.execute("SELECT * FROM users WHERE DNI = %s", (user_id,))
    data = cursor.fetchone()
    cursor.close()
    return render_template('/Public/perfil.html', data=data)

@app.route('/UserTasks') # Consulta indiviual de las tareas de casa usuario
def UserTasks():
    if 'user_id' in session:


        cursor = mysql.connection.cursor()
        user_id = session['user_id']
        cursor.execute("SELECT * FROM tasks WHERE user_id = %s", (user_id,))
        data = cursor.fetchall()
        cursor.close()     
        return render_template('/Public/tasks.html', data = data)
        
    else:
        flash('Primero debes iniciar sesion','info')
        return redirect(url_for('index'))
    
@app.route('/AgregarTask', methods=['GET', 'POST']) #Agregacion de nuevaas tareas
def AgregarTask():
    if request.method == 'POST':
        user_id = session['user_id']
        task_name = request.form['task_name']
        description = request.form['description']
        #Restricciones
        if not task_name or not description: 
            flash('Debe llenar los campos indicados','warning')
            return redirect(url_for('AgregarTask'))
        
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO tasks (user_id, task_name, description) VALUES (%s, %s ,%s)", (user_id, task_name, description))
        mysql.connection.commit()
        cursor.close()
        flash('Tarea guardada con exito.','success')

        #Resgistro en log
        user_id = session['user_id']
        accion = "Creo nueva tarea"
        tabla = "tasks"
        log = mysql.connection.cursor()
        log.execute('INSERT INTO logs (user_id, accion, tabla) VALUES (%s,%s,%s) ', (user_id, accion, tabla))
        mysql.connection.commit()
        log.close()

        return redirect(url_for('UserTasks'))
    return render_template('/Public/AgregarTask.html')
    
@app.route('/AgregarUser', methods=['GET', 'POST']) #Agregacion de nuevos usuarios
def AgregarUser():
    if request.method == 'POST':
        #Recuperando datos del formulario
        DNI = request.form['DNI']
        primer_nombre = request.form['primer_nombre']
        segundo_nombre = request.form['segundo_nombre']
        primer_apellido = request.form['primer_apellido']
        segundo_apellido = request.form['segundo_apellido']
        telefono = request.form['telefono']
        fecha_nacimiento = request.form['fecha_nacimiento']
        direccion = request.form['direccion']
        username = request.form['username']
        password = request.form['password']

        #Validando Datos
        # Comprobando si ya existe la cuenta de Usuario con respecto al id registrado
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE DNI = %s', (DNI,))
        DNI_Repetido = cursor.fetchone()
        cursor.close() #cerrrando conexion SQL

        if DNI_Repetido:
            flash("El DNI ya se encuentra registrado",'warning')
            return render_template('/Public/AgregarUser.html')
        elif not DNI or not primer_apellido or not primer_nombre or not telefono or not fecha_nacimiento or not direccion:
            flash('Ingrese correctamente los campos obligatorios','warning')
            return render_template('/Public/AgregarUser.html')
        elif int(DNI) < 0:
            flash('El DNI no puede ser un numero negativo','danger')
            return render_template('/Public/AgregarUser.html')
        elif int(telefono) < 0:
            flash('El numero de telefono no puede ser negativo', 'danger')
            return render_template('/Public/AgregarUser.html')
        #Insertando datos en la base de datos
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (DNI ,primer_nombre, segundo_nombre, primer_apellido, segundo_apellido, telefono, fecha_nacimiento, direccion, username, password) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (DNI,primer_nombre,segundo_nombre,primer_apellido,segundo_apellido,telefono,fecha_nacimiento,direccion,username,password))
        mysql.connection.commit()
        cur.close()
        flash('Informacio ingresada con exito','success')

        #Resgistro en log
        user_id = request.form['DNI']
        accion = "Nuevo User: {}".format(request.form['primer_nombre'])
        tabla = "users"
        log = mysql.connection.cursor()
        log.execute('INSERT INTO logs (user_id, accion, tabla) VALUES (%s,%s,%s) ', (user_id, accion, tabla))
        mysql.connection.commit()
        log.close()

        return render_template('/Public/login.html') 
    return render_template('/Public/AgregarUser.html')

#----------------------------------------------------------------------------
@app.route('/users')#CONSULTA/REPORTE DE LA TABLA DE USUARIOS
def users():
    if session['Admin'] == 1:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users")
        data = cur.fetchall()
        cur.close()
        return render_template('/Public/users.html', data=data)
    else:
        return render_template('/Public/acces_deined.html')
#------------------------------------------------------------------------------------------------------
@app.route('/AllTasks') #Consulta exclusiva para user admin, TODAS las tareas de los usuarios
def AllTasks():
    if session['Admin'] == 1:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM tasks")
        data = cur.fetchall()
        cur.close()
        return render_template('/Public/AllTasks.html', data=data)
    else:
        return render_template('/Public/acces_deined.html')

#------------------------------------------------------------------------------------------------------  
@app.route('/SuperUser')#Mensaje de Usuario no eminable (Administrador principal)
def SuperUser():
    flash('Este Usuario no se puede eliminar, es el Administrador Principal','info')
    return redirect(url_for('users'))
#----------------------------------------------------------------------------------------------------
@app.route('/editar/<int:id>', methods=['GET', 'POST'])#EDITAR USUARIOS DE LA DB A PARTIR DE LA ID
def editar(id):
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM users WHERE DNI = %s', (id,))
    data = cursor.fetchone()
    cursor.close()
    return render_template('/Public/editar.html', data=data)
#---------------------------------------------------------------------------------------
@app.route('/editar_task/<int:id>', methods=['GET','POST'])#Editar tareas a partir de la id
def editar_task(id):
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM tasks WHERE task_id = %s', (id,))
    data = cursor.fetchone()
    cursor.close()
    return render_template('/Public/editarTask.html', data=data)
#.---------------------------------------------------------------------------------------------------------------------------
@app.route('/eiliminar_task/<int:id>', methods=['GET','POST']) #Borrado logico de una tarea a partir de la id
def eliminar_task(id):
    #Parte logica:
    cursor = mysql.connection.cursor()
    cursor.execute('UPDATE tasks SET ShowTask=%s WHERE task_id = %s;', (0,id))
    mysql.connection.commit()
    cursor.close()
    flash('Tarea eliminada','danger')

    #Regsitro en log:
    user_id = session['user_id']
    accion = "Eliminado logico Tarea con id: {}".format(id)
    tabla = "Tasks"
    log = mysql.connection.cursor()
    log.execute('INSERT INTO logs (user_id, accion, tabla) VALUES (%s,%s,%s) ', (user_id, accion, tabla))
    mysql.connection.commit()
    log.close()
    
    return redirect(url_for('UserTasks'))
#----------------------------------------------------------------------------------------------------------------------
@app.route('/eiliminar_task_perma/<int:id>', methods=['GET','POST']) #Borrado permamente de una tarea a partir de la id
def eliminar_task_perma(id):
    cursor = mysql.connection.cursor()
    cursor.execute('DELETE FROM tasks WHERE task_id = %s;', (id,))
    mysql.connection.commit()
    cursor.close()
    flash('Tarea eliminada de forma permamente', 'danger')

    #Regsitro en log:
    user_id = session['user_id']
    accion = "Eliminado perma Tarea con id: {}".format(id)
    tabla = "Tasks"
    log = mysql.connection.cursor()
    log.execute('INSERT INTO logs (user_id, accion, tabla) VALUES (%s,%s,%s) ', (user_id, accion, tabla))
    mysql.connection.commit()
    log.close()

    return redirect(url_for('AllTasks'))
#---------------------------------------------------------------------------------------------
@app.route('/Terminar_task/<int:id>', methods=['GET','POST']) #Finalizacion de tarea
def Terminar_task(id):
    #Parte logica:
    finish = datetime.now()
    cursor = mysql.connection.cursor()
    cursor.execute('UPDATE tasks SET status=%s, finish=%s  WHERE task_id = %s;', (0,finish,id))
    mysql.connection.commit()
    cursor.close()
    flash('¡Tarea finalizada!','success')

    #Registro en el log:
    user_id = session['user_id']
    accion = "Finalizacion Tarea con id: {}".format(id)
    tabla = "Tasks"
    log = mysql.connection.cursor()
    log.execute('INSERT INTO logs (user_id, accion, tabla) VALUES (%s,%s,%s) ', (user_id, accion, tabla))
    mysql.connection.commit()
    log.close()

    return redirect(url_for('UserTasks'))
#-------------------------------------------------------------------------------------------------
@app.route('/eiliminar/<int:id>', methods=['GET','POST']) #ELIMINAR USUARIOS DE LA DB A PARTIR DE LA ID
def eliminar(id):
    #PARTE LOGICA
    cursor = mysql.connection.cursor()
    cursor.execute('DELETE FROM users WHERE DNI = %s;', (id,))
    mysql.connection.commit()
    cursor.close()
    flash(f'El Usuario {id} y todos sus registros han sido eliminados', 'danger')
    #REGISTRO EN LOG
    user_id = session['user_id']
    accion = "Eliminacion user: {}".format(id)
    tabla = "users"
    log = mysql.connection.cursor()
    log.execute('INSERT INTO logs (user_id, accion, tabla) VALUES (%s,%s,%s) ', (user_id, accion, tabla))
    mysql.connection.commit()
    log.close()

    return redirect(url_for('users'))
#------------------------------------------------------------------------------------------------------------------
@app.route('/guardar_cambios_task/<int:id>', methods=['POST']) #Guardado de cambios en una tarea
def guardar_cambios_task(id):
    #Parte Logica:
    task_name = request.form['task_name']
    description = request.form['description']
    ShowTask = request.form['ShowTask']
    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE tasks SET task_name=%s, description=%s, ShowTask=%s WHERE task_id=%s", (task_name, description,ShowTask, id) )
    mysql.connection.commit()
    cursor.close()
    flash('Cambios guardados con exito', 'success')
    #Registro en el log:
    user_id = session['user_id']
    accion = "Edicion de Tarea con id: {}".format(id)
    tabla = "Tasks"
    log = mysql.connection.cursor()
    log.execute('INSERT INTO logs (user_id, accion, tabla) VALUES (%s,%s,%s) ', (user_id, accion, tabla))
    mysql.connection.commit()
    log.close()

    if session['Admin'] == 1:
        return redirect('/AllTasks')
    else:
        return redirect('/UserTasks')

#------------------------------------------------------------------------------------------------------
@app.route('/guardar_cambios/<int:id>', methods=['POST']) #Guardado de cambios en la edicion de un perfil
def guardar_cambios(id):
    #Funcionamiento logico
    primer_nombre = request.form['primer_nombre']
    segundo_nombre = request.form['segundo_nombre']
    primer_apellido = request.form['primer_apellido']
    segundo_apellido = request.form['segundo_apellido']
    telefono = request.form['telefono']
    fecha_nacimiento = request.form['fecha_nacimiento']
    direccion = request.form['direccion']
    admin = request.form['admin']
    username = request.form['username']
    password = request.form['password']
    cursor = mysql.connection.cursor()
    cursor.execute('UPDATE users SET primer_nombre=%s, segundo_nombre=%s, primer_apellido=%s, segundo_apellido=%s, telefono=%s, fecha_nacimiento=%s, direccion=%s, admin=%s, username=%s, password=%s WHERE DNI=%s', (primer_nombre, segundo_nombre,primer_apellido,segundo_apellido,telefono,fecha_nacimiento,direccion,admin,username,password, id))
    mysql.connection.commit()
    cursor.close()
    #Registro en el log:
    user_id = id
    accion = "Edicion del perfil."
    tabla = "users"
    log = mysql.connection.cursor()
    log.execute('INSERT INTO logs (user_id, accion, tabla) VALUES (%s,%s,%s) ', (user_id, accion, tabla))
    mysql.connection.commit()
    log.close()



    #Alertas:
    if session['Admin'] == 1:
        flash('Cambios guardados con exito', 'success')
        return redirect('/users')
    else:
        flash('Cambios guardados con exito', 'success')
        return redirect('/perfil')



if __name__ == "__main__":
    app.run(port=PORT)