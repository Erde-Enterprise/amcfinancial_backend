USE amcFinancial;

-- Inserindo dados na tabela User_Root (apenas uma instância)
INSERT INTO User_Root (id, email_Root, password)
VALUES (1, 'user_root@example.com', 'password123');

-- Inserindo dados na tabela Costumer (clientes)
INSERT INTO Costumer (id, email, password, type, root_Id)
VALUES (1, 'customer1@example.com', 'password123', 1, 1),
       (2, 'customer2@example.com', 'password456', 2, 1);

-- Inserindo dados na tabela Medical_Clinic (clínicas médicas)
INSERT INTO Medical_Clinic (id, name, color)
VALUES (1, 'Clinic A', 'Blue'),
       (2, 'Clinic B', 'Green');

-- Inserindo dados na tabela Invoice (faturas)
INSERT INTO Invoice (id, invoice_number, description, amount, title, issue_date, due_date, attachment, reminder, status, type, clinic_Id, user_Id)
VALUES (1, '12345', 'Description 1', 100, 'Invoice 1', '2023-01-01', '2023-01-10', NULL, 0, 'Pending', 'Type A', 1, 1),
       (2, '67890', 'Description 2', 150, 'Invoice 2', '2023-02-01', '2023-02-15', NULL, 0, 'Pending', 'Type B', 2, 1);

-- Inserindo dados na tabela Access_History (histórico de acesso)
INSERT INTO Access_History (id, user_Id, login_date, location)
VALUES (1, 1, '2023-01-05 10:00:00', 'Location A'),
       (2, 2, '2023-02-10 15:30:00', 'Location B');
