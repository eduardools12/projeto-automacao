# 🛒 Projeto de Automação Web com Python

Automação desenvolvida em Python para realizar coleta automatizada de preços de produtos em e-commerces utilizando Selenium.

O projeto realiza buscas em sites como Amazon e Magazine Luiza, extrai informações relevantes (nome e preço) e gera uma planilha Excel com os dados coletados.

---

## 🚀 Objetivo

Demonstrar conhecimentos em:

- Automação Web
- Web Scraping
- Manipulação de dados
- Geração de arquivos Excel
- Uso de bibliotecas externas em Python

---

## 🛠 Tecnologias Utilizadas

- Python 3.x
- Selenium
- Openpyxl
- Regex (re)
- ChromeDriver

---

## ⚙️ Como Funciona

O script executa as seguintes etapas:

1. Inicializa o navegador automaticamente.
2. Acessa os sites definidos.
3. Realiza a busca de um produto específico.
4. Extrai o nome e o preço do produto.
5. Armazena os dados em uma planilha `.xlsx`.

---

## 📦 Instalação

### 1️⃣ Clone o repositório

git clone https://github.com/eduardools12/projeto-automacao.git
cd projeto-automacao
2️⃣ (Opcional) Criar ambiente virtual
python -m venv venv
Ativar no Windows:

venv\Scripts\activate
Ativar no Linux/Mac:

source venv/bin/activate

3️⃣ Instalar dependências
pip install -r requirements.txt

## 🖥 Pré-requisitos
Antes de executar o projeto, é necessário:

Python 3 instalado

Google Chrome instalado

ChromeDriver compatível com sua versão do Chrome

Para verificar a versão do Chrome:

chrome://settings/help
Download do ChromeDriver:
https://chromedriver.chromium.org/downloads

## ▶️ Execução
Para rodar o projeto:

python auto.py
Após a execução, será gerado um arquivo Excel com os dados coletados.

## 📂 Estrutura do Projeto
projeto-automacao/
│
├── auto.py
├── requirements.txt
└── README.md
## 📈 Possíveis Melhorias Futuras
Modularização do código

Implementação de tratamento de exceções

Uso de logging

Interface de linha de comando (argparse)

Dockerização do projeto

Integração com banco de dados

Criação de dashboard para visualização dos dados

## 📄 Licença
Este projeto está sob a licença MIT.

## 👨‍💻 Autor
Eduardo Gonçalves
GitHub: https://github.com/eduardools12
