CREATE TABLE User_Root (
    id INT PRIMARY KEY,
    email_Root VARCHAR(255),
    password VARCHAR(255)
);

CREATE TABLE User (
    id INT PRIMARY KEY,
    email VARCHAR(255),
    password VARCHAR(255),
    type INT,
    root_Id INT,
    FOREIGN KEY (root_Id) REFERENCES User_Root(id)
);

CREATE TABLE Medical_Clinic (
    id INT PRIMARY KEY,
    name VARCHAR(255),
    color VARCHAR(255)
);

CREATE TABLE Invoice (
    id INT PRIMARY KEY,
    invoice_number VARCHAR(255),
    description TEXT,
    amount INT,
    title VARCHAR(255),
    issue_date DATE,
    due_date DATE,
    attachment VARBINARY(MAX),
    reminder INT,
    status VARCHAR(255),
    type VARCHAR(255),
    clinic_Id INT,
    FOREIGN KEY (clinic_Id) REFERENCES Medical_Clinic(id)
);

CREATE TABLE Access_History (
    id INT PRIMARY KEY,
    user_Id INT,
    login_date DATETIME,
    location VARCHAR(255),
    FOREIGN KEY (user_Id) REFERENCES User_Root(id)
);
