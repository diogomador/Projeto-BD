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

CREATE TABLE tb_logs_emprestimos (
    log_id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    log_emp_id INT NOT NULL,
    log_acao VARCHAR(50) NOT NULL, -- Pode ser 'INSERT', 'UPDATE' ou 'DELETE'
    log_cli_id INT NOT NULL, -- Identificador do cliente que realizou o empréstimo
    log_usuario VARCHAR(100) NOT NULL, -- Nome do usuário que realizou a ação
    log_data_hora DATETIME NOT NULL,
    FOREIGN KEY (log_emp_id) REFERENCES tb_emprestimo(emp_id),
    FOREIGN KEY (log_cli_id) REFERENCES tb_cliente(cli_id)
);

-- Login do Admin Inicial
INSERT INTO tb_gerente (ger_codigo, ger_nome, ger_telefone, ger_email, ger_senha)
VALUES (1, 'Administrador', '40028922', 'admin@biblioteca.com', '$2b$12$QyfS1b2byE1HwzzSLIdH1uW6XogT9Z1WWK5S9iNqkTIgL04IVQ9u2');
-- Inserindo Gerentes
INSERT INTO tb_gerente (ger_codigo, ger_nome, ger_telefone, ger_email, ger_senha)
VALUES 
(1, 'Administrador', '40028922', 'admin@biblioteca.com', '$2b$12$QyfS1b2byE1HwzzSLIdH1uW6XogT9Z1WWK5S9iNqkTIgL04IVQ9u2'),
(2, 'Gerente 1', '40028923', 'gerente1@biblioteca.com', '$2b$12$QyfS1b2byE1HwzzSLIdH1uW6XogT9Z1WWK5S9iNqkTIgL04IVQ9u2');

-- Inserindo Clientes
INSERT INTO tb_cliente (cli_nome, cli_telefone, cli_email, cli_senha)
VALUES 
('Cliente 1', '40028924', 'cliente1@biblioteca.com', '$2b$12$QyfS1b2byE1HwzzSLIdH1uW6XogT9Z1WWK5S9iNqkTIgL04IVQ9u2'),
('Cliente 2', '40028925', 'cliente2@biblioteca.com', '$2b$12$QyfS1b2byE1HwzzSLIdH1uW6XogT9Z1WWK5S9iNqkTIgL04IVQ9u2'),
('Cliente 3', '40028926', 'cliente3@biblioteca.com', '$2b$12$QyfS1b2byE1HwzzSLIdH1uW6XogT9Z1WWK5S9iNqkTIgL04IVQ9u2');

-- Inserindo Endereços
INSERT INTO tb_endereco (end_cli_id, end_estado, end_cidade, end_bairro, end_rua, end_numero)
VALUES 
(1, 'SP', 'São Paulo', 'Bairro 1', 'Rua 1', '100'),
(2, 'RJ', 'Rio de Janeiro', 'Bairro 2', 'Rua 2', '200'),
(3, 'MG', 'Belo Horizonte', 'Bairro 3', 'Rua 3', '300');

-- Inserindo Autores
INSERT INTO tb_autor (aut_nome)
VALUES 
('Autor 1'),
('Autor 2'),
('Autor 3');

-- Inserindo Editoras
INSERT INTO tb_editora (edi_nome)
VALUES 
('Editora 1'),
('Editora 2'),
('Editora 3');

-- Inserindo Gêneros
INSERT INTO tb_genero (gen_nome)
VALUES 
('Ficção'),
('Não-Ficção'),
('Fantasia');

-- Inserindo Livros
INSERT INTO tb_livro (liv_titulo, liv_isbn, liv_ano, liv_aut_id, liv_edi_id, liv_gen_id, liv_pais_origem, liv_estoque, liv_preco, liv_ger_id)
VALUES 
('Livro 1', '1234567890123', 2020, 1, 1, 1, 'Brasil', 10, 29.99, 1),
('Livro 2', '1234567890124', 2021, 2, 2, 2, 'Brasil', 5, 39.99, 1),
('Livro 3', '1234567890125', 2022, 3, 3, 3, 'Brasil', 0, 49.99, 1);

-- Inserindo Empréstimos
INSERT INTO tb_emprestimo (emp_cli_id, emp_data_ini, emp_dev, emp_total, emp_status)
VALUES 
(1, '2023-01-01', '2023-01-15', 59.98, 'Ativo'),
(2, '2023-01-10', '2023-01-20', 29.99, 'Ativo'),
(3, '2023-01-15', NULL, 0, 'Ativo');

-- Inserindo Empréstimos-Livros
INSERT INTO tb_emprestimo_livro (eml_emp_id, eml_liv_id, eml_quantidade, eml_preco)
VALUES 
(1, 1, 2, 59.98),
(2, 2, 1, 29.99),
(3, 3, 1, 49.99);


DELIMITER //

CREATE FUNCTION calcular_multa(id_emprestimo INT) RETURNS DECIMAL(10,2)
BEGIN
    DECLARE multa DECIMAL(10,2);
    DECLARE dias_atraso INT;
    DECLARE taxa_diaria DECIMAL(10,2) DEFAULT 1.00;

    SELECT DATEDIFF(NOW(), emp_dev) INTO dias_atraso
    FROM tb_emprestimo
    WHERE emp_id = id_emprestimo;

    IF dias_atraso > 0 THEN
        SET multa = dias_atraso * taxa_diaria;
    ELSE
        SET multa = 0.00;
    END IF;

    RETURN multa;
END //

DELIMITER ;

DELIMITER //

CREATE PROCEDURE validar_emprestimo(
    IN id_usuario INT, 
    IN id_livro INT, 
    IN data_devolucao DATE,
    IN quantidade INT
)
BEGIN
    DECLARE estoque INT;
    DECLARE emprestimos_ativos INT;
    DECLARE preco DECIMAL(10,2);
    DECLARE total DECIMAL(10,2);
    DECLARE emp_id INT;

    -- Verificar estoque
    SELECT liv_estoque INTO estoque
    FROM tb_livro
    WHERE liv_id = id_livro;

    -- Verificar empréstimos ativos do usuário
    SELECT COUNT(*) INTO emprestimos_ativos
    FROM tb_emprestimo
    WHERE emp_cli_id = id_usuario AND emp_dev < NOW();

    -- Se o estoque for suficiente e o usuário não tiver empréstimos pendentes
    IF estoque >= quantidade AND emprestimos_ativos = 0 THEN
        -- Criar o empréstimo na tabela tb_emprestimo
        INSERT INTO tb_emprestimo (emp_cli_id, emp_data_ini, emp_dev, emp_total, emp_status)
        VALUES (id_usuario, NOW(), data_devolucao, 0, 'Ativo');

        -- Recuperar o emp_id do empréstimo recém-criado
        SET emp_id = LAST_INSERT_ID();

        -- Recuperar o preço do livro
        SELECT liv_preco INTO preco
        FROM tb_livro
        WHERE liv_id = id_livro;

        -- Calcular o total
        SET total = preco * quantidade;

        -- Inserir os livros na tabela tb_emprestimo_livro
        INSERT INTO tb_emprestimo_livro (eml_emp_id, eml_liv_id, eml_quantidade, eml_preco)
        VALUES (emp_id, id_livro, quantidade, total);

        -- Atualizar o estoque do livro
        UPDATE tb_livro 
        SET liv_estoque = liv_estoque - quantidade 
        WHERE liv_id = id_livro;

        -- Atualizar o total do empréstimo
        UPDATE tb_emprestimo
        SET emp_total = emp_total + total
        WHERE emp_id = emp_id;

        -- Retornar mensagem de sucesso
        SELECT 'Empréstimo válido e realizado com sucesso.' AS mensagem;
    ELSE
        -- Caso o estoque seja insuficiente ou haja empréstimos pendentes
        SELECT 'Empréstimo inválido. Verifique o estoque ou se há multas pendentes.' AS mensagem;
    END IF;
END //

DELIMITER ;

DELIMITER //

CREATE TRIGGER bloquear_usuario BEFORE INSERT ON tb_emprestimo
FOR EACH ROW
BEGIN
    DECLARE multa_pendente DECIMAL(10,2);

    SELECT calcular_multa(NEW.emp_id) INTO multa_pendente;

    IF multa_pendente > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Usuário com multa pendente. Empréstimo bloqueado.';
    END IF;
END //

DELIMITER ;

DELIMITER //

CREATE TRIGGER log_emprestimos AFTER INSERT ON tb_emprestimo
FOR EACH ROW
BEGIN
    DECLARE nome_usuario VARCHAR(100);

    -- Obter o nome do cliente que realizou o empréstimo
    SELECT cli_nome INTO nome_usuario
    FROM tb_cliente
    WHERE cli_id = NEW.emp_cli_id;

    -- Inserir o log na tabela tb_logs_emprestimos
    INSERT INTO tb_logs_emprestimos (log_emp_id, log_acao, log_cli_id, log_usuario, log_data_hora)
    VALUES (NEW.emp_id, 'INSERT', NEW.emp_cli_id, nome_usuario, NOW());
END //

DELIMITER ;

DELIMITER //

CREATE TRIGGER log_emprestimos_delete AFTER DELETE ON tb_emprestimo
FOR EACH ROW
BEGIN
    DECLARE nome_usuario VARCHAR(100);

    -- Obter o nome do cliente que realizou o empréstimo
    SELECT cli_nome INTO nome_usuario
    FROM tb_cliente
    WHERE cli_id = OLD.emp_cli_id;

    -- Inserir o log na tabela tb_logs_emprestimos
    INSERT INTO tb_logs_emprestimos (log_emp_id, log_acao, log_cli_id, log_usuario, log_data_hora)
    VALUES (OLD.emp_id, 'DELETE', OLD.emp_cli_id, nome_usuario, NOW());
END //

DELIMITER ;

DELIMITER //

CREATE TRIGGER log_emprestimos_update AFTER UPDATE ON tb_emprestimo
FOR EACH ROW
BEGIN
    DECLARE nome_usuario VARCHAR(100);

    -- Obter o nome do cliente que realizou o empréstimo
    SELECT cli_nome INTO nome_usuario
    FROM tb_cliente
    WHERE cli_id = NEW.emp_cli_id;

    -- Inserir o log na tabela tb_logs_emprestimos
    INSERT INTO tb_logs_emprestimos (log_emp_id, log_acao, log_cli_id, log_usuario, log_data_hora)
    VALUES (NEW.emp_id, 'UPDATE', NEW.emp_cli_id, nome_usuario, NOW());
END //

DELIMITER ;