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
        # Verifica se o usuário está logado
        if not session.get('logged_in') or session.get('gerente_id') is None:
            return redirect(url_for('login_gerente'))  # Redirecionar para a página de login de gerentes

        # Consulta o banco de dados para verificar se o e-mail está na tabela de gerentes
        email = session.get('email')
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM tb_gerente WHERE ger_email = %s", (email,))
        gerente = cursor.fetchone()
        cursor.close()

        # Se o gerente não for encontrado, redireciona
        if not gerente:
            return redirect(url_for('login_gerente'))

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
    
    user_id = session['user_id']

    # Consulta os empréstimos do usuário
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT emp_id, emp_data_ini, emp_dev, emp_status, emp_total 
        FROM tb_emprestimo 
        WHERE emp_cli_id = %s 
        ORDER BY emp_data_ini DESC
    """, (user_id,))
    emprestimos = cursor.fetchall()

    # Consulta os livros associados a cada empréstimo
    emprestimos_com_livros = []
    for emprestimo in emprestimos:
        cursor.execute("""
            SELECT l.liv_titulo, el.eml_quantidade, el.eml_preco 
            FROM tb_emprestimo_livro el
            JOIN tb_livro l ON el.eml_liv_id = l.liv_id
            WHERE el.eml_emp_id = %s
        """, (emprestimo[0],))
        livros = cursor.fetchall()
        emprestimos_com_livros.append({
            'emprestimo': emprestimo,
            'livros': livros
        })

    cursor.close()

    return render_template('cliente_dashboard.html', emprestimos=emprestimos_com_livros)

@app.route('/admin_dashboard')
@admin_required
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
@admin_required
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
@admin_required
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
@admin_required
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
@admin_required
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
@admin_required
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
    if request.method == 'POST':
        
        duracao_dias = int(request.form.get('duracao'))
        livros_ids = request.form.getlist('livros')
        quantidades = request.form.getlist('quantidades')

        if not livros_ids or not quantidades:
            flash('Nenhum livro foi selecionado para empréstimo.', 'danger')
            return redirect('/emprestimo')

        emprestimo_livros = []
        for livro_id, quantidade in zip(livros_ids, quantidades):
            emprestimo_livros.append({
                'livro_id': int(livro_id),
                'quantidade': int(quantidade)
            })

        cursor = mysql.connection.cursor()

        total = 0
        for item in emprestimo_livros:
            cursor.execute("SELECT liv_preco, liv_estoque FROM tb_livro WHERE liv_id = %s", (item['livro_id'],))
            livro = cursor.fetchone()

            if not livro or livro[1] < item['quantidade']:
                flash(f'O livro "{item["livro_id"]}" não está disponível na quantidade solicitada. Estoque atual: {livro[1]}.', 'danger')
                cursor.close()
                return redirect('/emprestimo')

            total += livro[0] * item['quantidade']

        cursor.execute(
            "INSERT INTO tb_emprestimo (emp_cli_id, emp_data_ini, emp_status, emp_total, emp_dev) VALUES (%s, NOW(), %s, %s, DATE_ADD(NOW(), INTERVAL %s DAY))",
            (session['user_id'], 'Ativo', total, duracao_dias)
        )
        emprestimo_id = cursor.lastrowid

        for item in emprestimo_livros:
            cursor.execute("SELECT liv_estoque FROM tb_livro WHERE liv_id = %s", (item['livro_id'],))
            livro = cursor.fetchone()

            cursor.execute(
                "INSERT INTO tb_emprestimo_livro (eml_emp_id, eml_liv_id, eml_quantidade, eml_preco) VALUES (%s, %s, %s, %s)",
                (emprestimo_id, item['livro_id'], item['quantidade'], item['quantidade'] * livro[0])
            )
            cursor.execute(
                "UPDATE tb_livro SET liv_estoque = liv_estoque - %s WHERE liv_id = %s",
                (item['quantidade'], item['livro_id'])
            )

        mysql.connection.commit()
        mysql.connection.close()

        flash('Empréstimo realizado com sucesso!', 'success')
        return redirect('/emprestimo')

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT *, gen_nome, aut_nome FROM tb_livro JOIN tb_genero ON gen_id=liv_gen_id JOIN tb_autor ON aut_id=liv_aut_id")
    livros = cursor.fetchall()
    cursor.close()

    return render_template('emprestimo.html', livros=livros)


# Listagem de usuários com ordenação
@app.route('/listar_clientes', methods=['GET'])
@admin_required
def listar_clientes():
    ordem = request.args.get('ordem', 'asc')  # 'asc' ou 'desc'
    try:
        cursor = mysql.connection.cursor()
        cursor.execute(f"SELECT cli_id, cli_nome, cli_email FROM tb_cliente ORDER BY cli_nome {ordem.upper()}")
        clientes = cursor.fetchall()
        cursor.close()
        return render_template('listar_clientes.html', clientes=clientes, ordem=ordem)
    except Exception as e:
        flash(f'Erro ao listar clientes: {e}', 'danger')
        return redirect(url_for('gerente_dashboard'))

# Listagem de livros com ordenação
@app.route('/listar_livros', methods=['GET'])
@admin_required
def listar_livros():
    ordem = request.args.get('ordem', 'asc')  # 'asc' ou 'desc'
    try:
        cursor = mysql.connection.cursor()
        cursor.execute(f"""
            SELECT liv_id, liv_titulo, liv_aut_id, liv_gen_id, liv_estoque, liv_preco 
            FROM tb_livro 
            ORDER BY liv_titulo {ordem.upper()}
        """)
        livros = cursor.fetchall()
        cursor.close()
        return render_template('listar_livros.html', livros=livros, ordem=ordem)
    except Exception as e:
        flash(f'Erro ao listar livros: {e}', 'danger')
        return redirect(url_for('gerente_dashboard'))


# Listagem de empréstimos com ordenação
@app.route('/listar_emprestimos', methods=['GET'])
@admin_required
def listar_emprestimos():
    ordem = request.args.get('ordem', 'asc')  # 'asc' ou 'desc'
    try:
        cursor = mysql.connection.cursor()
        cursor.execute(f"""
            SELECT emp_id, emp_data_ini, emp_dev, emp_total, cli_nome, liv_titulo 
            FROM tb_emprestimo
            INNER JOIN tb_cliente ON tb_emprestimo.emp_cli_id = tb_cliente.cli_id
            INNER JOIN tb_emprestimo_livro ON tb_emprestimo.emp_id = tb_emprestimo_livro.eml_emp_id
            INNER JOIN tb_livro ON tb_emprestimo_livro.eml_liv_id = tb_livro.liv_id
            ORDER BY emp_data_ini {ordem.upper()}
        """)
        emprestimos = cursor.fetchall()
        cursor.close()
        return render_template('listar_emprestimos.html', emprestimos=emprestimos, ordem=ordem)
    except Exception as e:
        flash(f'Erro ao listar empréstimos: {e}', 'danger')
        return redirect(url_for('gerente_dashboard'))

# Total de empréstimos em reais por usuário
@app.route('/relatorio_emprestimos_cliente', methods=['GET'])
@admin_required
def relatorio_emprestimos_cliente():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT cli.cli_nome, 
                   COUNT(emp.emp_id) AS total_emprestimos,
                   ROUND(SUM(emp.emp_total), 2) AS total_valor
            FROM tb_cliente cli
            LEFT JOIN tb_emprestimo emp ON cli.cli_id = emp.emp_cli_id
            GROUP BY cli.cli_id
            ORDER BY total_emprestimos DESC
        """)
        relatorio = cursor.fetchall()
        cursor.close()
        return render_template('relatorio_emprestimos_cliente.html', relatorio=relatorio)
    except Exception as e:
        flash(f'Erro ao gerar relatório: {e}', 'danger')
        return redirect(url_for('gerente_dashboard'))

# Usuários com empréstimos acima de R$100,00
@app.route('/clientes_acima_cem', methods=['GET'])
@admin_required
def clientes_acima_cem():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT cli.cli_nome, SUM(emp.emp_total) AS total
            FROM tb_cliente cli
            INNER JOIN tb_emprestimo emp ON cli.cli_id = emp.emp_cli_id
            GROUP BY cli.cli_id
            HAVING total > 100
        """)
        clientes = cursor.fetchall()
        cursor.close()
        return render_template('clientes_acima_cem.html', clientes=clientes)
    except Exception as e:
        flash(f'Erro ao gerar relatório: {e}', 'danger')
        return redirect(url_for('gerente_dashboard'))

# Top 10 livros mais pedidos
@app.route('/top_livros', methods=['GET'])
@admin_required
def top_livros():
    dias = request.args.get('dias', 30)
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT liv_titulo, COUNT(eml_id) AS pedidos
            FROM tb_emprestimo_livro
            INNER JOIN tb_livro ON tb_emprestimo_livro.eml_liv_id = tb_livro.liv_id
            INNER JOIN tb_emprestimo ON tb_emprestimo_livro.eml_emp_id = tb_emprestimo.emp_id
            WHERE emp_data_ini >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
            GROUP BY tb_emprestimo_livro.eml_liv_id
            ORDER BY pedidos DESC
            LIMIT 10
        """, (dias,))
        livros = cursor.fetchall()
        cursor.close()
        return render_template('top_livros.html', livros=livros)
    except Exception as e:
        flash(f'Erro ao gerar relatório: {e}', 'danger')
        return redirect(url_for('gerente_dashboard'))

# Livros não emprestados
@app.route('/livros_nao_emprestados', methods=['GET'])
@admin_required
def livros_nao_emprestados():
    dias = request.args.get('dias', 30)
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT liv_titulo
            FROM tb_livro
            WHERE liv_id NOT IN (
                SELECT DISTINCT eml_liv_id 
                FROM tb_emprestimo_livro
                INNER JOIN tb_emprestimo ON tb_emprestimo_livro.eml_emp_id = tb_emprestimo.emp_id
                WHERE emp_data_ini >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
            )
        """, (dias,))
        livros = cursor.fetchall()
        cursor.close()
        return render_template('livros_nao_emprestados.html', livros=livros)
    except Exception as e:
        flash(f'Erro ao gerar relatório: {e}', 'danger')
        return redirect(url_for('gerente_dashboard'))


@app.route("/devolver/<int:emp_id>", methods=["POST"])
def devolver(emp_id):
    cursor = mysql.connection.cursor()

    # Verificação do status do empréstimo
    cursor.execute("""
        SELECT emp_status 
        FROM tb_emprestimo 
        WHERE emp_id = %s AND emp_cli_id = %s
    """, (emp_id, session['user_id']))
    resultado = cursor.fetchone()
    
    if not resultado or resultado[0] == 'Finalizado':
        # Interrompe o processo, caso o empréstimo já tenha sido finalizado
        return redirect(url_for("cliente_dashboard"))

    # Busca os livros e atualiza o estoque
    cursor.execute("""
        SELECT eml_liv_id, eml_quantidade 
        FROM tb_emprestimo_livro 
        WHERE eml_emp_id = %s
    """, (emp_id,))
    livros = cursor.fetchall()

    for livro_id, quantidade in livros:
        cursor.execute("""
            UPDATE tb_livro 
            SET liv_estoque = liv_estoque + %s 
            WHERE liv_id = %s
        """, (quantidade, livro_id))

    # Atualiza status
    cursor.execute("""
        UPDATE tb_emprestimo 
        SET emp_status = 'Finalizado' 
        WHERE emp_id = %s AND emp_cli_id = %s
    """, (emp_id, session['user_id']))
    
    mysql.connection.commit()
    cursor.close()

    return redirect(url_for("cliente_dashboard"))