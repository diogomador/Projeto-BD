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

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in') or session.get('gerente_id') is None or session.get('email') != 'admin@biblioteca.com':
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def login_user(email, senha, user_type):
    table = 'tb_gerente' if user_type == 'gerente' else 'tb_cliente'
    cursor = mysql.connection.cursor()
    cursor.execute(f"SELECT * FROM {table} WHERE {table[:-1]}_email = %s", (email,))
    user = cursor.fetchone()
    cursor.close()
    if user and bcrypt.check_password_hash(user[3 if user_type == 'cliente' else 5], senha):
        return user
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
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
            cliente_id = cursor.lastrowid

            # Inserir endereço na tabela tb_endereco
            cursor.execute(
                'INSERT INTO tb_endereco (end_cli_id, end_estado, end_cidade, end_bairro, end_rua, end_numero) '
                'VALUES (%s, %s, %s, %s, %s, %s)',
                (cliente_id, estado, cidade, bairro, rua, numero)
            )

            mysql.connection.commit()
            flash('Cadastro realizado com sucesso! Você pode fazer login agora.', 'success')
            return redirect(url_for('login'))

        except IntegrityError:
            mysql.connection.rollback()
            flash('Erro ao cadastrar cliente. Tente novamente.', 'danger')
        finally:
            cursor.close()

    return render_template('cadastro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')

        gerente = login_user(email, senha, 'gerente')
        if gerente:
            session['logged_in'] = True
            session['user_id'] = gerente[0]
            session['email'] = gerente[4]
            session['nome'] = gerente[2]
            if gerente[4] == 'admin@biblioteca.com':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('gerente_dashboard'))

        cliente = login_user(email, senha, 'cliente')
        if cliente:
            session['logged_in'] = True
            session['user_id'] = cliente[0]
            session['nome'] = cliente[1]
            return redirect(url_for('cliente_dashboard'))

        flash('Credenciais inválidas.', 'danger')
    return render_template('login.html')

@app.route('/cliente_dashboard')
def cliente_dashboard():
    if not session.get('logged_in') or not session.get('user_id'):
        return redirect(url_for('login'))
    return render_template('cliente_dashboard.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if not session.get('logged_in') or not session.get('gerente_id'):
        return redirect(url_for('login'))
    if session.get('email') != 'admin@biblioteca.com':
        return redirect(url_for('gerente_dashboard'))
    return render_template('admin_dashboard.html')

@app.route('/gerente_dashboard')
def gerente_dashboard():
    if not session.get('logged_in') or not session.get('gerente_id'):
        return redirect(url_for('login'))
    return render_template('gerente_dashboard.html')

@app.route('/editar', methods=['GET', 'POST'])
def editar():
    if 'logged_in' not in session or not session['logged_in']:
        flash('Você precisa estar logado para acessar esta página.', 'danger')
        return redirect(url_for('login'))

    user_id = session['user_id']
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        telefone = request.form.get('telefone')
        estado = request.form.get('estado')
        cidade = request.form.get('cidade')
        bairro = request.form.get('bairro')
        rua = request.form.get('rua')
        numero = request.form.get('numero')

        try:
            cursor = mysql.connection.cursor()

            # Atualizar tabela de clientes
            cursor.execute("""
                UPDATE tb_cliente 
                SET cli_nome = %s, cli_email = %s, cli_telefone = %s 
                WHERE cli_id = %s
            """, (nome, email, telefone, user_id))

            # Atualizar tabela de endereços
            cursor.execute("""
                UPDATE tb_endereco 
                SET end_estado = %s, end_cidade = %s, end_bairro = %s, end_rua = %s, end_numero = %s 
                WHERE end_cli_id = %s
            """, (estado, cidade, bairro, rua, numero, user_id))

            mysql.connection.commit()
            flash('Dados atualizados com sucesso!', 'success')
        except Exception as e:
            mysql.connection.rollback()
            flash('Erro ao atualizar os dados: ' + str(e), 'danger')
        finally:
            cursor.close()

        return redirect(url_for('editar'))

    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT c.cli_nome, c.cli_email, c.cli_telefone, e.end_estado, e.end_cidade, e.end_bairro, e.end_rua, e.end_numero
        FROM tb_cliente c
        JOIN tb_endereco e ON c.cli_id = e.end_cli_id
        WHERE c.cli_id = %s
    """, (user_id,))
    user_data = cursor.fetchone()
    cursor.close()

    return render_template('editar.html', user_data=user_data)

@app.route('/excluir', methods=['POST'])
def excluir():
    if 'logged_in' not in session or not session['logged_in']:
        flash('Você precisa estar logado para acessar esta página.', 'danger')
        return redirect(url_for('login'))

    user_id = session['user_id']
    try:
        cursor = mysql.connection.cursor()
        
        # Excluir endereço associado
        cursor.execute("DELETE FROM tb_endereco WHERE end_cli_id = %s", (user_id,))

        # Excluir cliente
        cursor.execute("DELETE FROM tb_cliente WHERE cli_id = %s", (user_id,))

        mysql.connection.commit()
        session.clear()
        flash('Conta excluída com sucesso.', 'info')
    except Exception as e:
        mysql.connection.rollback()
        flash('Erro ao excluir a conta: ' + str(e), 'danger')
    finally:
        cursor.close()

    return redirect(url_for('index'))

@app.route('/cadastro_livro')
def cadastro_livro():
    return render_template('cadastro_livro.html')