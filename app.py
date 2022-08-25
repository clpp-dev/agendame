from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL, MySQLdb
from datetime import date
from datetime import datetime

# initializations
app = Flask(__name__)


# variable global con la fecha actual
today = date.today()


# Mysql Connection LOCALHOST
# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = 'password'
# app.config['MYSQL_DB'] = 'agendame'

# Mysql Connection CLERVER CLOUD
app.config['MYSQL_HOST'] = 'b5kxtdi020cffj7b0oks-mysql.services.clever-cloud.com'
app.config['MYSQL_USER'] = 'ucycgzgbsgxlcyvj'
app.config['MYSQL_PASSWORD'] = 'qdntrRCC2Euw2hqhmriw'
app.config['MYSQL_DB'] = 'b5kxtdi020cffj7b0oks'
mysql = MySQL(app)


# settings
app.secret_key = "mysecretkey"


# routes
@app.route('/')
def Index():

    if 'id' in session:
        flash('Ya tienes una sesión activa')
        return redirect(url_for('inicio'))
    else:
        return render_template('index.html')


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if 'id' in session:
        flash('Ya tienes una sesión activa')
        return redirect(url_for('inicio'))

    else:
        return render_template('registro.html')


@app.route('/registrousuario', methods=['GET', 'POST'])
def registrousuario():
    if 'id' in session:
        flash('Ya tienes una sesión activa')
        return redirect(url_for('inicio'))

    else:
        if request.method == 'POST':
            nombre = request.form["nombre"]
            apellido = request.form["apellido"]
            edad = request.form["edad"]
            ocupacion = request.form["ocupacion"]
            email = request.form["email"]
            password = request.form["password"]

            cursor = mysql.connection.cursor()
            cursor.execute(
                'SELECT * FROM usuario WHERE email=%s', (email,))
            datosUser = cursor.fetchall()
            cursor.close()

            if (len(datosUser) > 0):
                if email == datosUser[0][5]:
                    flash('El email ya esta registrado')
                    return redirect(url_for('registro'))

            else:
                cursor = mysql.connection.cursor()
                cursor.execute('INSERT INTO usuario (nombre,apellido,edad,ocupacion,email,password) VALUES(%s, %s, %s, %s,%s, %s)',
                               (nombre, apellido, edad, ocupacion, email, password))

                mysql.connection.commit()

                flash('Registro exitoso!')
                return redirect(url_for('registro'))


@app.route('/login',  methods=['GET', 'POST'])
def login():

    if 'id' in session:
        flash('Ya tienes una sesión activa')
        return redirect(url_for('inicio'))

    elif request.method == 'POST':
        email = request.form["email"]
        password = request.form["password"]

        cursor = mysql.connection.cursor()
        cursor.execute(
            'SELECT * FROM usuario WHERE email=%s', (email,))
        datosUser = cursor.fetchall()
        cursor.close()

        if (len(datosUser) > 0):
            if (password == datosUser[0][6]):
                session['nombre'] = datosUser[0][1]
                session['id'] = datosUser[0][0]

                flash('Bienvenido(a),')
                id = session['id']
                nombre = session['nombre']

                cur = mysql.connection.cursor()
                cur.execute(
                    'SELECT * FROM eventos eventos WHERE usuario=%s ORDER BY fecha ASC', (id,)
                    )
                datos = cur.fetchall()
                cur.close()
                return render_template('inicio.html', evento=datos, nombre=nombre, today=today)

            else:
                flash('Password incorrecto')
                return redirect(url_for('login'))
        else:
            flash("Error Usuario No encontrado")
            return redirect(url_for('login'))
    else:
        return render_template('login.html')


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if 'id' in session:
        session.clear()
        flash('Sesion Cerrada')
        return render_template('index.html')
    else:
        flash('No ha iniciado sesión')
        return render_template('index.html')


@app.route('/inicio', methods=['GET', 'POST'])
def inicio():
    print(today)
    valor = str(today)
    valor = valor.replace("-", "")
    print(valor)

    if 'id' in session:
        id = session['id']
        print(id)
        nombre = session['nombre']
        cursor = mysql.connection.cursor()
        cursor.execute(
                    'SELECT * FROM eventos eventos WHERE usuario=%s ORDER BY fecha ASC', (id,)
                )
        datos = cursor.fetchall()
        # print(f"DATOS FECHAALL INICIO: {datos}")
        cursor.close()
        return render_template('inicio.html', evento=datos, nombre=nombre)

    else:
        flash('No ha iniciado sesión')
        return render_template('login.html')


@app.route('/newevento', methods=['GET', 'POST'])
def newevento():
    if 'id' in session:
        return render_template('newevento.html', today=today)
    else:
        flash('No ha iniciado sesión')
        return render_template('login.html')


@app.route('/registroevento', methods=['GET', 'POST'])
def registroevento():
    if 'id' in session:
        if request.method == 'POST':
            descripcion = request.form["descripcion"]
            hora = request.form["hora"]
            fecha = request.form["fecha"]
            lugar = request.form["lugar"]
            idusuario = session['id']
            cursor = mysql.connection.cursor()
            cursor.execute('INSERT INTO eventos (descripcion,hora,fecha,lugar,usuario) VALUES(%s, %s, %s, %s,%s)',
                           (descripcion, hora, fecha, lugar, idusuario))

            mysql.connection.commit()

            flash('Registro de evento exitoso!')
            return redirect(url_for('newevento'))
        else:
            return render_template('newevento.html')
    else:
        flash('No ha iniciado sesión')
        return render_template('index.html')


@app.route('/editar/<id>', methods=['POST', 'GET'])
def editar(id):
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM eventos WHERE ideventos = %s', (id,))
    datos = cursor.fetchall()
    cursor.close()
    return render_template('editarevento.html', evento=datos[0])


@app.route('/update/<id>', methods=['POST'])
def update(id):
    if request.method == 'POST':
        descripcion = request.form['descripcion']
        hora = request.form['hora']
        fecha = request.form['fecha']
        lugar = request.form['lugar']
        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE eventos SET descripcion = %s, hora = %s, fecha = %s, lugar = %s WHERE ideventos = %s",
                       (descripcion, hora, fecha, lugar, id))
        flash('El evento fué actualizado correctamente')
        mysql.connection.commit()
        return redirect(url_for('inicio'))


@app.route('/eliminar/<string:id>', methods=['POST', 'GET'])
def delete_evento(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM eventos WHERE ideventos = {0}'.format(id))
    mysql.connection.commit()
    flash('Evento eliminado correctamente')
    return redirect(url_for('inicio'))


@app.route('/filtroDescripcion', methods=['POST'])
def filtrarDescripcion():
    if request.method == 'POST':

        filtroDescripcion = "%" + request.form['descripcion'] + "%"
        id = session['id']
        nombre = session['nombre']
        cur = mysql.connection.cursor()
        cur.execute(
            'SELECT * FROM eventos WHERE usuario=%s and descripcion like %s ', (id, filtroDescripcion,))

        flash('Filtro aplicado correctamente')
        datos = cur.fetchall()
        cur.close()

        return render_template('inicio.html', evento=datos, nombre=nombre)

    else:
        return redirect(url_for('inicio'))


@app.route('/filtroHora', methods=['POST'])
def filtrarHora():
    if request.method == 'POST':

        filtroHora = "%" + request.form['hora'] + "%"
        id = session['id']
        nombre = session['nombre']
        cur = mysql.connection.cursor()
        hora = []
        hora = filtroHora.split(":")
        hora[0] = hora[0]+"%"
        print(hora[0])

        cur.execute(
            'SELECT * FROM eventos WHERE usuario=%s and hora like %s ', (id, hora[0],))

        flash('Filtro aplicado correctamente')
        datos = cur.fetchall()
        print(datos)
        cur.close()

        return render_template('inicio.html', evento=datos, nombre=nombre)

    else:

        return redirect(url_for('inicio'))


@app.route('/filtroFecha', methods=['POST'])
def filtrarFecha():
    if request.method == 'POST':
        filtroFecha = request.form['fecha']
        id = session['id']
        nombre = session['nombre']
        cur = mysql.connection.cursor()
        cur.execute(
            'SELECT * FROM eventos WHERE usuario=%s and fecha =%s ', (id, filtroFecha,))

        flash('Filtro aplicado correctamente')
        datos = cur.fetchall()
        cur.close()

        return render_template('inicio.html', evento=datos, nombre=nombre, today=today)

    else:
        return redirect(url_for('inicio'))


@app.route('/filtroLugar', methods=['POST'])
def filtrarLugar():
    if request.method == 'POST':
        filtroLugar = "%" + request.form['lugar'] + "%"
        id = session['id']
        nombre = session['nombre']
        cur = mysql.connection.cursor()
        cur.execute(
            'SELECT * FROM eventos WHERE usuario=%s and lugar like %s ', (id, filtroLugar,))

        flash('Filtro aplicado correctamente')
        datos = cur.fetchall()
        cur.close()

        return render_template('inicio.html', evento=datos, nombre=nombre)

    else:
        return redirect(url_for('inicio'))


# Inicializar la app
if __name__ == "__main__":
    app.run(port=3000, debug=True)