from flask import Flask, render_template, request, send_file, redirect, url_for, session
from werkzeug.utils import secure_filename
import prediction
from flask_mysqldb import MySQL
import MySQLdb.cursors
import MySQLdb.cursors, re, hashlib
import os
from flask import flash

app = Flask("__main__", template_folder="templates")
app.secret_key = '_5#y2L"F4Q8z\n\xec]/'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'sispre'

# Intialize MySQL
mysql = MySQL(app)
Uploaded_images = "C:/Users/ASUS/Desktop/proyect/Uploaded_images"

app.config['Uploaded_images'] = Uploaded_images


@app.route('/', methods=['GET', 'POST'])
def login():
    # Output a message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
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
