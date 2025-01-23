CREATE DATABASE db_biblioteca;
USE db_biblioteca;

-- Tabela de Gerentes
CREATE TABLE tb_gerente (
    ger_id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    ger_codigo INT,
    ger_nome VARCHAR(255),
    ger_telefone VARCHAR(15),
    ger_email VARCHAR(100),
    ger_senha VARCHAR(100)
);

-- Tabela de Clientes
CREATE TABLE tb_cliente (
    cli_id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    cli_nome VARCHAR(40),
    cli_telefone VARCHAR(15),
    cli_email VARCHAR(100) UNIQUE,
    cli_senha VARCHAR(100)
);

-- Tabela de Endereços (relacionada a Clientes)
CREATE TABLE tb_endereco (
    end_id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    end_cli_id INT NOT NULL,
    end_estado VARCHAR(2),
    end_cidade VARCHAR(100),
    end_bairro VARCHAR(100),
    end_rua VARCHAR(100),
    end_numero VARCHAR(10),
    FOREIGN KEY (end_cli_id) REFERENCES tb_cliente(cli_id)
);

-- Tabela de Autores
CREATE TABLE tb_autor (
    aut_id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    aut_nome VARCHAR(40)
);

-- Tabela de Editoras
CREATE TABLE tb_editora (
    edi_id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    edi_nome VARCHAR(40)
);

-- Tabela de Gêneros
CREATE TABLE tb_genero (
    gen_id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    gen_nome VARCHAR(40)
);

-- Tabela de Livros
CREATE TABLE tb_livro (
    liv_id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    liv_titulo VARCHAR(100),
    liv_isbn VARCHAR(30),
    liv_ano INT,
    liv_aut_id INT,
    liv_edi_id INT,
    liv_gen_id INT,
    liv_pais_origem VARCHAR(100),
    liv_estoque INT,
    liv_preco FLOAT,
    liv_ger_id INT NOT NULL,
    FOREIGN KEY (liv_aut_id) REFERENCES tb_autor(aut_id),
    FOREIGN KEY (liv_edi_id) REFERENCES tb_editora(edi_id),
    FOREIGN KEY (liv_gen_id) REFERENCES tb_genero(gen_id),
    FOREIGN KEY (liv_ger_id) REFERENCES tb_gerente(ger_id)
);

-- Tabela de Empréstimos
CREATE TABLE tb_emprestimo (
    emp_id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    emp_cli_id INT NOT NULL,
    emp_data_ini DATE,
    emp_dev DATE,
    emp_total FLOAT,
    emp_status VARCHAR(15),
    FOREIGN KEY (emp_cli_id) REFERENCES tb_cliente(cli_id)
);

-- Tabela de Empréstimos-Livros (relaciona empréstimos e livros)
CREATE TABLE tb_emprestimo_livro (
    eml_id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    eml_emp_id INT NOT NULL,
    eml_liv_id INT NOT NULL,
    eml_quantidade INT,
    eml_preco FLOAT,
    FOREIGN KEY (eml_emp_id) REFERENCES tb_emprestimo(emp_id),
    FOREIGN KEY (eml_liv_id) REFERENCES tb_livro(liv_id)
);

-- Login do Admin Inicial
INSERT INTO tb_gerente (ger_codigo, ger_nome, ger_telefone, ger_email, ger_senha)
VALUES (1, 'Administrador', '40028922', 'admin@biblioteca.com', '$2b$12$QyfS1b2byE1HwzzSLIdH1uW6XogT9Z1WWK5S9iNqkTIgL04IVQ9u2');
