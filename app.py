from flask import Flask, render_template, redirect, request, url_for, flash, session
from flask_mysqldb import MySQL
from MySQLdb._exceptions import IntegrityError
from flask_bcrypt import Bcrypt
from functools import wraps

app = Flask(__name__)
mysql = MySQL(app)
bcrypt = Bcrypt(app)
app.config.from_object('models.config.Config')

def is_email_taken(email):
    """
    Verifica se o e-mail já está cadastrado na tabela tb_cliente
    """
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM tb_cliente WHERE cli_email = %s", (email,))
    result = cursor.fetchone()
    cursor.close()
    return result is not None

@app.route('/')
def index():
    """
    Página inicial do site.
    """
    return render_template('index.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    """
    Página para cadastro de novos clientes e seus endereços.
    """
    if request.method == 'POST':
        # Dados do cliente
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        telefone = request.form.get('telefone')

        # Dados do endereço
        estado = request.form.get('estado')
        cidade = request.form.get('cidade')
        bairro = request.form.get('bairro')
        rua = request.form.get('rua')
        numero = request.form.get('numero')

        # Verificar se o e-mail já está em uso
        if is_email_taken(email):
            flash('Esse e-mail já está em uso. Escolha outro.', 'warning')
            return redirect(url_for('cadastro'))

        # Hash da senha
        hashed_senha = bcrypt.generate_password_hash(senha).decode('utf-8')

        try:
            cursor = mysql.connection.cursor()

            # Inserir cliente na tabela tb_cliente
            cursor.execute(
                'INSERT INTO tb_cliente (cli_nome, cli_email, cli_senha, cli_telefone) VALUES (%s, %s, %s, %s)',
                (nome, email, hashed_senha, telefone)
            )
            cliente_id = cursor.lastrowid  # ID do cliente recém-cadastrado

            # Inserir endereço na tabela tb_endereco
            cursor.execute(
                'INSERT INTO tb_endereco (end_cli_id, end_estado, end_cidade, end_bairro, end_rua, end_numero) '
                'VALUES (%s, %s, %s, %s, %s, %s)',
                (cliente_id, estado, cidade, bairro, rua, numero)
            )

            # Confirmar as alterações
            mysql.connection.commit()

            flash('Cadastro realizado com sucesso! Você pode fazer login agora.', 'success')
            return redirect(url_for('login'))

        except IntegrityError:
            mysql.connection.rollback()
            flash('Erro ao cadastrar cliente. Tente novamente.', 'danger')
            return redirect(url_for('cadastro'))
        finally:
            cursor.close()

    return render_template('cadastro.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Página de login para usuários registrados.
    """
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        # Validar os dados enviados
        if not email or not senha:
            flash('Por favor, preencha todos os campos.', 'danger')
            return redirect(url_for('login'))

        # Buscar o usuário no banco de dados
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT cli_id, cli_nome, cli_senha FROM tb_cliente WHERE cli_email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()

        if user and bcrypt.check_password_hash(user[2], senha):  # user[2] é a senha criptografada
            # Criar a sessão do usuário
            session['logged_in'] = True
            session['user_id'] = user[0]  # ID do cliente
            session['username'] = user[1]  # Nome do cliente
            flash('Login efetuado com sucesso!', 'success')
            return redirect(url_for('dashboard'))  # Redireciona para o dashboard
        else:
            flash('Credenciais inválidas. Tente novamente.', 'danger')

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    """
    Página do painel do usuário após o login.
    """
    if not session.get('logged_in'):
        flash('Por favor, faça login para acessar essa página.', 'warning')
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session.get('username'))
