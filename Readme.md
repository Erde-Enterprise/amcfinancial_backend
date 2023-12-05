# 📈 AMC Financial

Bem-vindo ao Backend do AMC Financial da Avegena Medical Center, projeto pela Erde EnterPrise.
Para Detalhes mais específicos a respeito da lógica e estrutura do backend, consulte a [documentação ](https://www.notion.so/AMC-Financial-893a044b008747a89fb810caee500d4d?pvs=4)

# Versões
- Python 3.11
- SQL Server 2019


## Configurando o Ambiente de Desenvolvimento

### 1. Clonar o Repositório

```bash
git clone https://github.com/seu-usuario/api.git
```


### 2. Entrar na Pasta "api"

```bash
cd api
```


### 3. Configurando a Máquina Virtual e Instalando Dependências

Criar e Ativar a Máquina Virtual

```bash
python -m venv env
```
- No Windows (cmd):

```bash
env\Scripts\activate
```
- No macOS/Linux:

```bash
source env/bin/activate
```

Instalar Dependências
```bash
pip install -r requirements.txt
```

### 4. Configurando Banco de dados
Para isso, crie um documento na raiz do projeto "api" igual ao **databaseconf_example.py** mas deixe com o nome de **databaseconf.py**, copie os dados no example e substitua pelas suas configurações do banco de dados do seu SQL Server.

### 4. Executando o Projeto

Prepare as migrações
```bash
python manage.py makemigrations 
```

Efetue as migrações
```bash
python manage.py migrate 
```
Rode o programa
```bash
python manage.py runserver
```
