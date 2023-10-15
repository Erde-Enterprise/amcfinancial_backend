USE amcFinancial;

-- Inserindo dados na tabela User_Root (apenas uma instância)
INSERT INTO User_Root ( email_Root, password)
VALUES ( 'user_root@example.com', 'password123');

-- Inserindo dados na tabela Costumer (clientes)
INSERT INTO Customer ( email, password, type, root_Id)
VALUES ( 'customer1@example.com', 'password123', 1, 1),
       ( 'customer2@example.com', 'password456', 2, 1);

-- Inserindo dados na tabela Medical_Clinic (clínicas médicas)
INSERT INTO Medical_Clinic ( name, color)
VALUES ( 'Clinic A', 'Blue'),
       ( 'Clinic B', 'Green');

-- Inserindo dados na tabela Invoice (faturas)
INSERT INTO Invoice ( invoice_number, description, amount, title, issue_date, due_date, attachment, reminder, status, type, clinic_Id, user_Id)
VALUES ( '12345', 'Description 1', 100, 'Invoice 1', '2023-01-01', '2023-01-10', NULL, 0, 'Pending', 'Type A', 1, 1),
       ( '67890', 'Description 2', 150, 'Invoice 2', '2023-02-01', '2023-02-15', NULL, 0, 'Pending', 'Type B', 2, 1);

-- Inserindo dados na tabela Access_History (histórico de acesso)
INSERT INTO Access_History ( user_Id, login_date, location)
VALUES ( 1, '2023-01-05 10:00:00', 'Location A'),
       ( 2, '2023-02-10 15:30:00', 'Location B');
