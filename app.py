from flask import Flask, render_template, redirect, request, url_for, flash, session
from flask_mysqldb import MySQL
from MySQLdb._exceptions import IntegrityError
from flask_bcrypt import Bcrypt
from functools import wraps
from datetime import datetime, timedelta

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
            return redirect(url_for('login_cliente'))

        except IntegrityError:
            mysql.connection.rollback()
            flash('Erro ao cadastrar cliente. Tente novamente.', 'danger')
        finally:
            cursor.close()

    return render_template('cadastro.html')

@app.route('/login_cliente', methods=['GET', 'POST'])
def login_cliente():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')

        try:
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * FROM tb_cliente WHERE cli_email = %s", (email,))
            cliente = cursor.fetchone()
            cursor.close()

            if not cliente:
                flash('E-mail não encontrado.', 'danger')
                return redirect(url_for('login_cliente'))

            if bcrypt.check_password_hash(cliente[4], senha):  # Índice 4 corresponde à senha
                session['logged_in'] = True
                session['user_id'] = cliente[0]
                session['nome'] = cliente[1]
                return redirect(url_for('cliente_dashboard'))
            else:
                flash('Senha incorreta.', 'danger')

        except Exception as e:
            print(f"Erro no login do cliente: {e}")
            flash('Erro interno no servidor.', 'danger')

    return render_template('login_cliente.html')


@app.route('/login_gerente', methods=['GET', 'POST'])
def login_gerente():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')

        try:
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * FROM tb_gerente WHERE ger_email = %s", (email,))
            gerente = cursor.fetchone()
            cursor.close()

            if gerente and bcrypt.check_password_hash(gerente[5], senha):  # Índice 5 corresponde à senha
                session['logged_in'] = True
                session['gerente_id'] = gerente[0]  # Índice 0 corresponde ao ID do gerente
                session['nome'] = gerente[2]  # Índice 2 corresponde ao nome do gerente
                session['email'] = gerente[4]  # Índice 4 corresponde ao e-mail do gerente

                # Redirecionar para o dashboard apropriado
                if gerente[4] == 'admin@biblioteca.com':
                    return redirect(url_for('admin_dashboard'))
                else:
                    return redirect(url_for('gerente_dashboard'))

        except Exception as e:
            print(f"Erro no login do gerente: {e}")  # Apenas para debug; remova em produção.

        flash('Credenciais inválidas para gerente.', 'danger')

    return render_template('login_gerente.html')


@app.route('/cliente_dashboard')
def cliente_dashboard():
    if not session.get('logged_in') or not session.get('user_id'):
        return redirect(url_for('login_cliente'))
    return render_template('cliente_dashboard.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if not session.get('logged_in') or not session.get('gerente_id'):
        return redirect(url_for('login'))
    if session.get('email') != 'admin@biblioteca.com':
        return redirect(url_for('gerente_dashboard'))
    return render_template('admin_dashboard.html')

@app.route('/adicionar_gerente', methods=['GET', 'POST'])
@admin_required
def adicionar_gerente():
    if request.method == 'POST':
        codigo = request.form.get('codigo')
        nome = request.form.get('nome')
        telefone = request.form.get('telefone')
        email = request.form.get('email')
        senha = request.form.get('senha')

        # Verificar se o e-mail já está em uso
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM tb_gerente WHERE ger_email = %s", (email,))
        gerente_existente = cursor.fetchone()

        if gerente_existente:
            flash('E-mail já cadastrado para outro gerente.', 'danger')
            return redirect(url_for('adicionar_gerente'))

        # Gerar o hash da senha
        hashed_senha = bcrypt.generate_password_hash(senha).decode('utf-8')

        # Inserir o gerente na tabela
        try:
            cursor.execute(
                'INSERT INTO tb_gerente (ger_codigo, ger_nome, ger_telefone, ger_email, ger_senha) '
                'VALUES (%s, %s, %s, %s, %s)',
                (codigo, nome, telefone, email, hashed_senha)
            )
            mysql.connection.commit()
            flash('Gerente adicionado com sucesso!', 'success')
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Erro ao adicionar gerente: {e}', 'danger')
        finally:
            cursor.close()

        return redirect(url_for('adicionar_gerente'))

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

@app.route('/cadastrar_autor', methods=['GET', 'POST'])
def cadastrar_autor():
    if not session.get('logged_in') or not session.get('gerente_id'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        autor_nome = request.form.get('autor_nome')

        try:
            cursor = mysql.connection.cursor()

            # Inserir autor na tabela
            cursor.execute("INSERT INTO tb_autor (aut_nome) VALUES (%s)", (autor_nome,))
            mysql.connection.commit()
            flash('Autor cadastrado com sucesso!', 'success')

        except Exception as e:
            mysql.connection.rollback()
            flash(f'Erro ao cadastrar o autor: {e}', 'danger')
        finally:
            cursor.close()

        return redirect(url_for('cadastrar_autor'))

    return render_template('cadastrar_autor.html')


@app.route('/cadastrar_editora', methods=['GET', 'POST'])
def cadastrar_editora():
    if not session.get('logged_in') or not session.get('gerente_id'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        editora_nome = request.form.get('editora_nome')

        try:
            cursor = mysql.connection.cursor()

            # Inserir editora na tabela
            cursor.execute("INSERT INTO tb_editora (edi_nome) VALUES (%s)", (editora_nome,))
            mysql.connection.commit()
            flash('Editora cadastrada com sucesso!', 'success')

        except Exception as e:
            mysql.connection.rollback()
            flash(f'Erro ao cadastrar a editora: {e}', 'danger')
        finally:
            cursor.close()

        return redirect(url_for('cadastrar_editora'))

    return render_template('cadastrar_editora.html')


@app.route('/cadastrar_genero', methods=['GET', 'POST'])
def cadastrar_genero():
    if not session.get('logged_in') or not session.get('gerente_id'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        genero_nome = request.form.get('genero_nome')

        try:
            cursor = mysql.connection.cursor()

            # Inserir gênero na tabela
            cursor.execute("INSERT INTO tb_genero (gen_nome) VALUES (%s)", (genero_nome,))
            mysql.connection.commit()
            flash('Gênero cadastrado com sucesso!', 'success')

        except Exception as e:
            mysql.connection.rollback()
            flash(f'Erro ao cadastrar o gênero: {e}', 'danger')
        finally:
            cursor.close()

        return redirect(url_for('cadastrar_genero'))

    return render_template('cadastrar_genero.html')

@app.route('/cadastrar_livro', methods=['GET', 'POST'])
def cadastrar_livro():
    if not session.get('logged_in') or not session.get('gerente_id'):
        return redirect(url_for('login_gerente'))

    if request.method == 'POST':
        titulo = request.form.get('titulo')
        isbn = request.form.get('isbn')
        ano = request.form.get('ano')
        autor_id = request.form.get('autor')
        editora_id = request.form.get('editora')
        genero_id = request.form.get('genero')
        pais_origem = request.form.get('pais_origem')
        estoque = request.form.get('estoque')
        preco = request.form.get('preco')
        gerente_id = session['gerente_id']  # ID do gerente logado

        try:
            cursor = mysql.connection.cursor()

            # Inserir o livro na tabela
            cursor.execute("""
                INSERT INTO tb_livro (
                    liv_titulo, liv_isbn, liv_ano, liv_aut_id, liv_edi_id, liv_gen_id,
                    liv_pais_origem, liv_estoque, liv_preco, liv_ger_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (titulo, isbn, ano, autor_id, editora_id, genero_id, pais_origem, estoque, preco, gerente_id))

            mysql.connection.commit()
            flash('Livro cadastrado com sucesso!', 'success')

        except Exception as e:
            mysql.connection.rollback()
            flash(f'Erro ao cadastrar o livro: {e}', 'danger')
        finally:
            cursor.close()

        return redirect(url_for('cadastrar_livro'))

    # Buscar autores, editoras e gêneros para exibir no formulário
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT aut_id, aut_nome FROM tb_autor")
    autores = cursor.fetchall()

    cursor.execute("SELECT edi_id, edi_nome FROM tb_editora")
    editoras = cursor.fetchall()

    cursor.execute("SELECT gen_id, gen_nome FROM tb_genero")
    generos = cursor.fetchall()
    cursor.close()

    return render_template('cadastro_livro.html', autores=autores, editoras=editoras, generos=generos)


@app.route('/emprestimo', methods=['GET', 'POST'])
def emprestimo():

    if 'user_id' not in session:
        flash('Você precisa estar logado para realizar um empréstimo.', 'danger')
        return redirect(url_for('login_cliente'))
    
    if request.method == 'POST':
        # Processa o formulário enviado
        livros_ids = request.form.getlist('livros[]')  # Use livros[] para capturar como lista
        quantidades = request.form.getlist('quantidades[]')  # Use quantidades[] para capturar como lista

        if not livros_ids or not quantidades:
            flash('Nenhum livro foi selecionado para empréstimo.', 'danger')
            return redirect('/emprestimo')

        emprestimo_livros = []
        for livro_id, quantidade in zip(livros_ids, quantidades):
            emprestimo_livros.append({
                'livro_id': int(livro_id),
                'quantidade': int(quantidade)
            })

        # Manipulação de tempo
        data_inicio = datetime.now()
        data_devolucao = data_inicio + timedelta(weeks=2)

        # Formatar as datas formato 'YYYY-MM-DD HH:MM:SS'
        data_inicio_str = data_inicio.strftime('%Y-%m-%d %H:%M:%S')
        data_devolucao_str = data_devolucao.strftime('%Y-%m-%d %H:%M:%S')

        # Lógica de criação do empréstimo
        cursor = mysql.connection.cursor()

        # Calcula o total do empréstimo
        total = 0
        for item in emprestimo_livros:
            cursor.execute("SELECT liv_preco, liv_estoque FROM tb_livro WHERE liv_id = %s", (item['livro_id'],))
            livro = cursor.fetchone()
            if not livro or livro[1] < item['quantidade']:
                flash(f'O livro com ID {item["livro_id"]} não está disponível na quantidade solicitada.', 'danger')
                cursor.close()
                return redirect('/emprestimo')
            total += livro[0] * item['quantidade']

        # Insere o registro de empréstimo
        cursor.execute(
            "INSERT INTO tb_emprestimo (emp_cli_id, emp_data_ini, emp_dev, emp_status, emp_total) VALUES (%s, %s, %s, %s, %s)",
            (session['user_id'], data_inicio_str, data_devolucao_str, 'Ativo', total)
        )
        emprestimo_id = cursor.lastrowid

        # Insere os livros no empréstimo
        for item in emprestimo_livros:
            cursor.execute(
                "INSERT INTO tb_emprestimo_livro (eml_emp_id, eml_liv_id, eml_quantidade, eml_preco) VALUES (%s, %s, %s, %s)",
                (emprestimo_id, item['livro_id'], item['quantidade'], item['quantidade'] * livro[0])
            )
            # Atualiza o estoque
            cursor.execute(
                "UPDATE tb_livro SET liv_estoque = liv_estoque - %s WHERE liv_id = %s",
                (item['quantidade'], item['livro_id'])
            )

        mysql.connection.commit()
        cursor.close()

        flash('Empréstimo realizado com sucesso!', 'success')
        return redirect('/emprestimo')

    # Método GET: Exibe os livros disponíveis
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT *, gen_nome, aut_nome FROM tb_livro JOIN tb_genero ON gen_id=liv_gen_id JOIN tb_autor ON aut_id=liv_aut_id")
    livros = cursor.fetchall()
    cursor.close()

    return render_template('emprestimo.html', livros=livros)
