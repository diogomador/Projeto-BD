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
liv_autor VARCHAR(100),
liv_editora VARCHAR(100),
liv_genero VARCHAR(100),
liv_pais_origem VARCHAR(100),
liv_estoque INT,
liv_preco FLOAT
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
    emp_data_ini DATE,
    emp_data_dev DATE,
    emp_total INT,
    emp_status VARCHAR(15)
);

CREATE TABLE tb_emprestimo_livro(
    epl_id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    epl_quantidade INT,
    epl_preco FLOAT
);

