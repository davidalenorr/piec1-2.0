# Sistema de Cadastro e Avaliação com OMR

Este projeto é um sistema completo de gestão educacional desenvolvido em Django, onde professores podem cadastrar disciplinas, alunos e questões, gerar provas personalizadas e corrigir automaticamente utilizando tecnologia OMR (Optical Mark Recognition).

# Características Principais

- **Sistema Completo de Gestão**: Cadastro de professores, disciplinas, alunos e questões
- **Gerador de Provas Inteligente**: Criação automática de provas com questões cadastradas
- **Tecnologia OMR Profissional**: Correção automática de gabaritos com leitura óptica
- **Gabaritos Padronizados**: Folhas de resposta otimizadas para diferentes quantidades de questões
- **Layout Responsivo**: Interface moderna e intuitiva
- **Exportação PDF**: Geração de provas e gabaritos em formato profissional

# Programas Necessários
- Python 3.10 (ou superior)
- Django 4.0+
- Navegador web moderno

# Passo a passo para usar

1. **Clone ou baixe o projeto**
   ```bash
   git clone <https://github.com/davidalenorr/piec1-2.0.git>
   cd piec1-master
   ```

2. **Abra o terminal na pasta do projeto**

3. **Crie e ative um ambiente virtual**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Instale as dependências**
   ```bash
   pip install django
   pip install Pillow 
   ```

5. **Configure o banco de dados**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Execute o servidor de desenvolvimento**
   ```bash
   python manage.py runserver
   ```

7. **Acesse o sistema**
   - Abra seu navegador e vá para: `http://127.0.0.1:8000/`
   - Para acessar o painel administrativo: `http://127.0.0.1:8000/admin/`

# Funcionalidades

# Gestão de Usuários
- Cadastro e autenticação de professores
- Sistema de login seguro
- Perfis de usuário personalizados

# Gestão Acadêmica
- Cadastro de disciplinas com detalhes completos
- Cadastro de alunos por disciplina
- Organização hierárquica de conteúdo

# Banco de Questões
- Cadastro de questões com múltiplas alternativas
- Categorização por disciplina
- Sistema de tags e filtros
- Reutilização de questões em diferentes provas

# Geração de Provas
- Criação automática de provas personalizadas
- Seleção inteligente de questões
- Formatação profissional para impressão
- Exportação em PDF de alta qualidade

# Sistema OMR (Optical Mark Recognition)
- **Gabaritos Padronizados**: Folhas de resposta otimizadas para leitura óptica
- **Múltiplos Formatos**: Suporte para 5, 10, 15 e 20 questões
- **Layout Simétrico**: Distribuição equilibrada das questões para melhor precisão
- **Círculos Padronizados**: Tamanho uniforme (18px) para máxima compatibilidade
- **Marcadores de Alinhamento**: Sistema profissional de referência para scanners
- **Correção Automática**: Processamento rápido e preciso de respostas

# Características Técnicas OMR
- **Especificações dos Círculos**:
  - Diâmetro: 18px (padrão internacional)
  - Borda: 2px sólida preta
  - Fundo: Branco para máximo contraste
  - Formato: Círculo perfeito (border-radius: 50%)

- **Compatibilidade**: Otimizado para impressão A4 e scanners OMR profissionais

# Armazenamento
- Banco de dados SQLite integrado
- Armazenamento temporário em JSON
- Backup automático de dados críticos

# Tecnologias Utilizadas

- **Backend**: Django 5.2.4
- **Frontend**: HTML5, CSS3, JavaScript
- **Banco de Dados**: SQLite
- **Exportação**: Tecnologia PDF nativa
- **OMR**: Sistema proprietário de leitura óptica

## 📁 Estrutura do Projeto

```
piec1-master/
├── cadastro/                 # App principal
│   ├── templates/            # Templates HTML
│   ├── static/              # Arquivos estáticos (CSS, JS)
│   ├── models.py            # Modelos de dados
│   ├── views.py             # Lógica de negócio
│   └── forms.py             # Formulários
├── sistema_cadastro/         # Configurações Django
├── gabarito_*.html          # Templates OMR especializados
├── temp_storage/            # Armazenamento temporário
└── manage.py               # Gerenciador Django
```

## 🎨 Interface

O sistema possui uma interface moderna e intuitiva com:
- Design responsivo para diferentes dispositivos
- Navegação clara e organizada
- Formulários validados em tempo real
- Feedback visual para ações do usuário
- Tema profissional adequado para ambiente educacional

## 📈 Vantagens do Sistema OMR

1. **Precisão**: Correção automática elimina erros humanos
2. **Velocidade**: Processamento instantâneo de centenas de provas
3. **Padronização**: Gabaritos uniformes garantem consistência
4. **Profissionalismo**: Layout adequado para instituições de ensino
5. **Economia**: Redução significativa no tempo de correção manual

