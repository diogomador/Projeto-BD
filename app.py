from flask import Flask, render_template, redirect, request, url_for, flash, session
from flask_mysqldb import MySQL
from MySQLdb import IntegrityError
from flask_bcrypt import Bcrypt
from functools import wraps

app = Flask(__name__)
mysql = MySQL(app)
bcrypt = Bcrypt()
app.config.from_object('models.config.Config')

def is_email_taken(email):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM tb_cliente WHERE cli_email = %s", (email,))
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
        senha = request.form['senha']
        telefone = request.form['telefone']
        estado = request.form['estado']
        cidade = request.form['cidade']
        bairro = request.form['bairro']
        rua = request.form['rua']
        numero = request.form['numero']

        # Verifique se o e-mail já está em uso
        if is_email_taken(email):
            flash('Esse e-mail já está em uso. Escolha outro')
            return redirect(url_for('register'))

        # Hash da senha
        hashed_senha = bcrypt.generate_password_hash(senha).decode('utf-8')

        # Tente inserir o novo usuário
        try:
            cursor = mysql.connection.cursor()
            cursor.execute('INSERT INTO tb_cliente (nome, email, senha, telefone) VALUES (%s, %s, %s, %s)', (nome, email, hashed_senha, telefone))
            mysql.connection.commit()

            cursor = mysql.connection.cursor()
            cursor.execute('INSERT INTO tb_endereco (estado, cidade, bairro, rua, numero) VALUES (%s, %s, %s, %s, %s)', (estado, cidade, bairro, rua, numero))
            mysql.connection.commit()

            flash('Cadastro realizado com sucesso! Você pode fazer login agora.','info')
            return redirect(url_for('login'))
        except IntegrityError:
            mysql.connection.rollback()
            flash('Erro ao cadastrar cliente.')
            return redirect(url_for('cadastro'))
        finally:
            cursor.close()

    return render_template('cadastro.html')

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         email = request.form['email']
#         senha = request.form['senha']
        
#         # Buscar o usuário no banco de dados
#         cur = mysql.connection.cursor()
#         cur.execute("SELECT * FROM users WHERE email = %s", [email])
#         user = cur.fetchone()
#         cur.close()

#         if user and bcrypt.check_senha_hash(user[3], senha):  # O campo 3 é a senha
#             session['logged_in'] = True
#             session['users_id'] = user[0]  # Armazenar o ID do usuário na sessão
#             session['username'] = user[1]
#             flash('Login efetuado com sucesso!', 'success')
#             return redirect(url_for('dashboard'))
#         else:
#             flash('Falha no login. Verifique suas credenciais', 'danger')
#     return render_template('login.html')