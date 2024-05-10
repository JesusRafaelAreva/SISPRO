from flask import Flask, render_template, request, send_file, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from flask_mysqldb import MySQL
import MySQLdb.cursors
import os
import re
import hashlib
import prediction

app = Flask("__main__", template_folder="templates")
app.secret_key = '_5#y2L"F4Q8z\n\xec]/'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'serpre'

# Intialize MySQL
mysql = MySQL(app)
Uploaded_images = "C:/Users/ASUS/Desktop/proyect/Uploaded_images"

app.config['Uploaded_images'] = Uploaded_images


@app.route('/', methods=['GET', 'POST'])
def login():
    # Mensaje de salida en caso de error
    msg = ''
    
    # Verificar si se envió el formulario
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Obtener usuario y contraseña ingresados
        username = request.form['username']
        password = request.form['password']
        
        # Verificar si las credenciales son las especificadas
        if username == 'Rafa' and password == 'julia0302':
            # Redirigir al usuario directamente a home.html
            session['loggedin'] = True
            session['username'] = username
            return redirect(url_for('home'))
        
        # Verificar si el usuario y contraseña coinciden con la base de datos
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        account = cursor.fetchone()
        
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            return redirect(url_for('home'))
        else:
            msg = 'Incorrect username/password!'
    
    return render_template('detec.html', msg=msg)

@app.route('/logout/')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''  # Output message if something goes wrong...

    if request.method == 'POST':
        # Check if "username", "password", and "email" POST requests exist (user submitted form)
        if 'username' in request.form and 'password' in request.form and 'email' in request.form:
            # Create variables for easy access
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']

            # Check if account exists using MySQL
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
            account = cursor.fetchone()

            # If account exists show error and validation checks
            if account:
                msg = 'Account already exists!'
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                msg = 'Invalid email address!'
            elif not re.match(r'[A-Za-z0-9]+', username):
                msg = 'Username must contain only characters and numbers!'
            elif not username or not password or not email:
                msg = 'Please fill out the form!'
            else:
                # Hash the password
                hash = password + app.secret_key
                hash = hashlib.sha1(hash.encode())
                password = hash.hexdigest()
                # Account doesn't exist, and the form data is valid, so insert the new account into the accounts table
                cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email,))
                mysql.connection.commit()
                msg = 'You have successfully registered!'
        else:
            # Form is empty... (no POST data)
            msg = 'Please fill out the form!'

    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)

@app.route('/patiente', methods=['GET', 'POST'])
def patiente():
    msg = ''  # Mensaje de salida si algo sale mal...

    if request.method == 'POST':
        hclinica = request.form['hclinica']
        dni = request.form['dni']
        username = request.form['username']
        diagnostico = request.form['output']
        efectividad = request.form['output22']
       
        # Validar los datos del formulario
        if not hclinica or not dni or not username:
            msg = 'Por favor, complete todos los campos.'
        else:
            try:
                def getOutput():
                    output = ""
                    myimage = request.files.get('myfile')
                    if myimage:
                        imgname = secure_filename(myimage.filename)
                        imgpath = os.path.join(app.config["Uploaded_images"], imgname)
                        myimage.save(imgpath)
                        output = prediction.prediction(imgpath)
                        print(output)
                    return output

                output = getOutput()

                cursor = mysql.connection.cursor()
                # Utilizar una consulta parametrizada para evitar la inyección SQL
                cursor.execute('INSERT INTO patient_records (hclinica, dni, nombre, diagnostico, efectividad) VALUES (%s, %s, %s, %s, %s)', (hclinica, dni, username, diagnostico, efectividad))
                mysql.connection.commit()
                msg = '¡Registro exitoso!'
                
                # Redirigir a la página de inicio después de un registro exitoso
                return redirect(url_for('home'))
                
            except Exception as e:
                # Manejar cualquier error que pueda ocurrir durante la inserción
                msg = f'Ocurrió un error durante el registro: {str(e)}'
                return render_template('home.html', msg=msg)  # Mostrar el mensaje de error y no continuar

    # Mostrar el formulario de registro con el mensaje (si lo hay)
    return render_template('home.html', msg=msg)

@app.route('/patient_records')
def patient_records():
    if 'loggedin' in session:
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM patient_records')
            records = cursor.fetchall()
            return render_template('patient_records.html', records=records)
        except Exception as e:
            msg = f'Error fetching records: {str(e)}'
            flash(msg, 'error')
            return redirect(url_for('home'))
    else:
        flash('Please log in to access this page.', 'error')
        return redirect(url_for('login'))

@app.route('/delete_record/<int:id>')
def delete_record(id):
    if 'loggedin' in session:
        try:
            cursor = mysql.connection.cursor()
            cursor.execute('DELETE FROM patient_records WHERE id = %s', (id,))
            mysql.connection.commit()
            flash('Record deleted successfully.', 'success')
        except Exception as e:
            flash(f'Error deleting record: {str(e)}', 'error')
        return redirect(url_for('patient_records'))
    else:
        flash('Please log in to access this page.', 'error')
        return redirect(url_for('login'))

@app.route('/update_record/<int:id>', methods=['GET', 'POST'])
def update_record(id):
    if 'loggedin' in session:
        if request.method == 'POST':
            hclinica = request.form['hclinica']
            dni = request.form['dni']
            username = request.form['username']
            diagnostico = request.form['diagnostico']
            efectividad = request.form['efectividad']
            try:
                cursor = mysql.connection.cursor()
                cursor.execute('UPDATE patient_records SET hclinica=%s, dni=%s, nombre=%s, diagnostico=%s, efectividad=%s WHERE id=%s',
                               (hclinica, dni, username, diagnostico, efectividad, id))
                mysql.connection.commit()
                flash('Record updated successfully.', 'success')
                return redirect(url_for('patient_records'))
            except Exception as e:
                flash(f'Error updating record: {str(e)}', 'error')
        else:
            try:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('SELECT * FROM patient_records WHERE id = %s', (id,))
                record = cursor.fetchone()
                return render_template('update_record.html', record=record)
            except Exception as e:
                flash(f'Error fetching record: {str(e)}', 'error')
                return redirect(url_for('patient_records'))
    else:
        flash('Please log in to access this page.', 'error')
        return redirect(url_for('login'))

@app.route('/home')
def home():
    # Verifica si el usuario está logeado
    if 'loggedin' in session:
        # El usuario está logeado, mostrar la página de inicio
        return render_template('home.html', username=session['username'])
    # Si el usuario no está logeado, redirigirlo a la página de inicio de sesión y mostrar un mensaje de error
    flash('Por favor, inicia sesión para acceder a esta página.', 'error')
    return redirect(url_for('login'))

@app.route('/profile')
def profile():
    # Verifica si el usuario está logeado
    if 'loggedin' in session:
        # Obtén la información de la cuenta del usuario para mostrar en la página de perfil
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        # Mostrar la página de perfil con la información de la cuenta
        return render_template('profile.html', account=account)
    # Si el usuario no está logeado, redirigirlo a la página de inicio de sesión y mostrar un mensaje de error
    flash('Por favor, inicia sesión para acceder a esta página.', 'error')
    return redirect(url_for('login'))

@app.route('/getFile', methods=['POST'])
def getOutput():
    output = ""
    if request.method == 'POST':
        myimage = request.files.get('myfile')
        imgname = secure_filename(myimage.filename)
        imgpath = os.path.join(app.config["Uploaded_images"], imgname)
        myimage.save(os.path.join(app.config["Uploaded_images"], imgname))
        output = prediction.prediction(imgpath)
        print(output)
    return output
if __name__ == '__main__':
    app.run(port=3000)
