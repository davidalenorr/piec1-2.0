# Sistema de Cadastro de Usuários

Este projeto é um sistema de cadastro de usuários desenvolvido em Django, onde um professor pode cadastrar disciplinas e alunos, corrigir provas de gabarito utilizando OMR.

#Programas Necessários
- Python 3.10 (ou superior)

#Passo a passo para usar

1. Baixe o projeto

2. Abra o terminal do projeto

3. Crie um ambiente virtual
   - python -m venv venv
  
   - venv\Scripts\activate

4. Instalar as dependências
   - pip install -r requirements.txt

   - pip install django
     
5. Migrações do BD
   
   - python manage.py migrate
  
   - python manage.py createsuperuser
     
6. Rode o servidor
   
   - python manage.py runserver
     
7. Acesse o sistema através `http://127.0.0.1:8000/`.

# Funcionalidades

- Cadastro de professores
- Cadastro de disciplinas
- Cadastro de alunos
- Cadastro de questões
- Gerador de provas com questões cadastradas
- Armazenamento temporário de dados em JSON
- Correção de gabarito(OMR)
