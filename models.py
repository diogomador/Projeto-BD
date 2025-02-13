from app import db

class Gerente(db.Model):
    __tablename__ = 'tb_gerente'

    ger_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ger_codigo = db.Column(db.Integer)
    ger_nome = db.Column(db.String(255))
    ger_telefone = db.Column(db.String(15))
    ger_email = db.Column(db.String(100), unique=True)
    ger_senha = db.Column(db.String(100))

    def __repr__(self):
        return f'<Gerente {self.ger_nome}>'

class Cliente(db.Model):
    __tablename__ = 'tb_cliente'

    cli_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cli_nome = db.Column(db.String(40))
    cli_telefone = db.Column(db.String(15))
    cli_email = db.Column(db.String(100), unique=True)
    cli_senha = db.Column(db.String(100))

    enderecos = db.relationship('Endereco', backref='cliente', lazy=True)

    def __repr__(self):
        return f'<Cliente {self.cli_nome}>'

class Endereco(db.Model):
    __tablename__ = 'tb_endereco'

    end_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    end_cli_id = db.Column(db.Integer, db.ForeignKey('tb_cliente.cli_id'), nullable=False)
    end_estado = db.Column(db.String(2))
    end_cidade = db.Column(db.String(100))
    end_bairro = db.Column(db.String(100))
    end_rua = db.Column(db.String(100))
    end_numero = db.Column(db.String(10))

    def __repr__(self):
        return f'<Endereco {self.end_id}>'

class Autor(db.Model):
    __tablename__ = 'tb_autor'

    aut_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    aut_nome = db.Column(db.String(40))

    def __repr__(self):
        return f'<Autor {self.aut_nome}>'

class Editora(db.Model):
    __tablename__ = 'tb_editora'

    edi_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    edi_nome = db.Column(db.String(40))

    def __repr__(self):
        return f'<Editora {self.edi_nome}>'

class Genero(db.Model):
    __tablename__ = 'tb_genero'

    gen_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    gen_nome = db.Column(db.String(40))

    def __repr__(self):
        return f'<Genero {self.gen_nome}>'

class Livro(db.Model):
    __tablename__ = 'tb_livro'

    liv_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    liv_titulo = db.Column(db.String(100))
    liv_isbn = db.Column(db.String(30))
    liv_ano = db.Column(db.Integer)
    liv_aut_id = db.Column(db.Integer, db.ForeignKey('tb_autor.aut_id'))
    liv_edi_id = db.Column(db.Integer, db.ForeignKey('tb_editora.edi_id'))
    liv_gen_id = db.Column(db.Integer, db.ForeignKey('tb_genero.gen_id'))
    liv_pais_origem = db.Column(db.String(100))
    liv_estoque = db.Column(db.Integer)
    liv_preco = db.Column(db.Float)
    liv_ger_id = db.Column(db.Integer, db.ForeignKey('tb_gerente.ger_id'), nullable=False)

    def __repr__(self):
        return f'<Livro {self.liv_titulo}>'

class Emprestimo(db.Model):
    __tablename__ = 'tb_emprestimo'

    emp_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    emp_cli_id = db.Column(db.Integer, db.ForeignKey('tb_cliente.cli_id'))
    emp_data_ini = db.Column(db.Date)
    emp_dev = db.Column(db.Date)
    emp_total = db.Column(db.Float)
    emp_status = db.Column(db.String(15))

    def __repr__(self):
        return f'<Emprestimo {self.emp_id}>'

class EmprestimoLivro(db.Model):
    __tablename__ = 'tb_emprestimo_livro'

    eml_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    eml_emp_id = db.Column(db.Integer, db.ForeignKey('tb_emprestimo.emp_id'))
    eml_liv_id = db.Column(db.Integer, db.ForeignKey('tb_livro.liv_id'))
    eml_quantidade = db.Column(db.Integer)
    eml_preco = db.Column(db.Float)

    def __repr__(self):
        return f'<EmprestimoLivro {self.eml_id}>'