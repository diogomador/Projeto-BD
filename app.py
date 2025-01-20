from flask import Flask, render_template, url_for, redirect, request
from flask_mysqldb import MySQL

app = Flask(__name__)
mysql = MySQL(app)
app.config.from_object('models.config.Config')

def is_email_taken(email):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM tb_users WHERE use_email = %s", (email,))
    result = cursor.fetchone()
    cursor.close()
    return result is not None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        telefone = request.form['telefone']
        endereco =request.form['endereco']


    return render_template('cadastro.html')