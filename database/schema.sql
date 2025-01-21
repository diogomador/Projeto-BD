CREATE DATABASE db_biblioteca;
USE db_biblioteca;

CREATE TABLE tb_gerente(
    ger_id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    ger_codigo INT,
    ger_nome VARCHAR(255),
    ger_telefone VARCHAR(15),
    ger_email VARCHAR(100),
    ger_senha VARCHAR(100)
);

CREATE TABLE tb_cliente(
cli_id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
cli_nome VARCHAR(40),
cli_telefone VARCHAR(15),
cli_email VARCHAR(100) UNIQUE,
cli_senha VARCHAR(100),
cli_endereco VARCHAR(255)
);

CREATE TABLE tb_livros(
liv_id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
liv_titulo VARCHAR(100),
liv_isbn VARCHAR(30),
liv_ano INT,
liv_aut_id VARCHAR(100),
liv_edi_id VARCHAR(100),
liv_gen_id VARCHAR(100),
liv_pais_origem VARCHAR(100),
liv_estoque INT,
liv_preco FLOAT,
FOREIGN KEY (liv_aut_id) REFERENCES tb_autor(aut_id),
FOREIGN KEY (liv_edi_id) REFERENCES tb_editora(edi_id),
FOREIGN KEY (liv_gen_id) REFERENCES tb_genero(gen_id)
);

CREATE TABLE tb_editora(
    edi_id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    edi_nome VARCHAR(40)
);

CREATE TABLE tb_autor(
    aut_id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    aut_nome VARCHAR(40)
);

CREATE TABLE tb_genero(
    gen_id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    gen_nome VARCHAR(40)
);

CREATE TABLE tb_emprestimo(
    emp_id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    emp_nome VARCHAR(40),
    emp_cli_id INT,
    emp_data_ini DATE,
    emp_data_dev DATE,
    emp_total INT,
    emp_status VARCHAR(15),
    FOREIGN KEY (emp_cli_id) REFERENCES tb_cliente(cli_id)
);

CREATE TABLE tb_emprestimo_livro(
    epl_id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    epl_emp_id INT,
    epl_liv_id INT,
    epl_quantidade INT,
    epl_preco FLOAT,
    FOREIGN KEY (epl_emp_id) REFERENCES tb_emprestimo(emp_id),
    FOREIGN KEY (epl_liv_id) REFERENCES tb_livros(liv_id)
);

