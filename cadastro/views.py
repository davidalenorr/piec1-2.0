from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.urls import reverse
from .forms import ProfessorForm, DisciplinaForm, AlunoForm, QuestaoForm
import json
import os
import re

#Temporario
TEMP_STORAGE_FILE = 'temp_storage/dados_temp.json'

def home(request):
    return render(request, 'cadastro/home.html')
#Carrega as disciplinas do professor logado e exibe na página inicial
def index(request):
    data = load_data()
    cpf_professor = request.session.get('usuario')
    disciplinas = [d for d in data.get('disciplinas', []) if d.get('cpf_professor') == cpf_professor]
    return render(request, 'cadastro/index.html', {'disciplinas': disciplinas})

def load_data():
    if os.path.exists(TEMP_STORAGE_FILE):
        with open(TEMP_STORAGE_FILE, 'r') as file:
            return json.load(file)
    return {'usuarios': [], 'professores': [], 'disciplinas': [], 'alunos': [], 'questoes': []}
#Para salvar
def save_data(data):
    with open(TEMP_STORAGE_FILE, 'w') as file:
        json.dump(data, file)
# FLogin         
def login_view(request):
    error = None
    if request.method == 'POST':
        cpf = request.POST.get('cpf')
        senha = request.POST.get('senha')
        data = load_data()
        usuario = next((u for u in data.get('usuarios', []) if u.get('cpf') == cpf and u.get('senha') == senha), None)
        if usuario:
            request.session['usuario'] = usuario['cpf']
            request.session['nome_completo'] = usuario['nome']
            return redirect('index')
        else:
            error = 'CPF ou senha inválidos!'
    return render(request, 'cadastro/login.html', {'error': error})

def cadastro_usuario(request):
    error = None
    if request.method == 'POST':
        cpf = request.POST.get('cpf')
        nome = request.POST.get('nome')
        rg = request.POST.get('rg')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        data = load_data()
        if len(cpf) != 11 or not cpf.isdigit():
            error = 'CPF deve conter exatamente 11 dígitos numéricos.'
        elif len(rg) != 7 or not rg.isdigit():
            error = 'RG deve conter exatamente 7 dígitos numéricos.'
        elif any(u.get('cpf') == cpf for u in data.get('usuarios', [])):
            error = 'Usuário já cadastrado com esse CPF!'
        else:
            data.setdefault('usuarios', []).append({
                'cpf': cpf,
                'nome': nome,
                'rg': rg,
                'email': email,
                'senha': senha
            })
            save_data(data)
            return redirect('login')
    return render(request, 'cadastro/cadastro_usuario.html', {'error': error})

def cadastrar_professor(request):
    if request.method == 'POST':
        form = ProfessorForm(request.POST)
        if form.is_valid():
            data = load_data()
            data['professores'].append(form.cleaned_data)
            save_data(data)
            return redirect('cadastrar_professor')
    else:
        form = ProfessorForm()
    return render(request, 'cadastro/cadastrar_professor.html', {'form': form})

def cadastrar_disciplina(request):
    sucesso = None
    if request.method == 'POST':
        nome = request.POST.get('nome')
        ano = request.POST.get('ano')
        data = load_data()
        cpf_professor = request.session.get('usuario')
        data.setdefault('disciplinas', []).append({
            'nome': nome,
            'ano': ano,
            'cpf_professor': cpf_professor,
            'alunos': []
        })
        save_data(data)
        sucesso = 'Disciplina cadastrada com sucesso!'
    return render(request, 'cadastro/cadastrar_disciplina.html', {'sucesso': sucesso})

def cadastrar_aluno(request):
    sucesso = None
    if request.method == 'POST':
        matricula = request.POST.get('matricula')
        nome = request.POST.get('nome')
        data = load_data()
        cpf_professor = request.session.get('usuario')
        if len(matricula) != 11 or not matricula.isdigit():
            sucesso = 'A matrícula deve conter exatamente 11 dígitos numéricos.'
        elif any(char.isdigit() for char in nome):
            sucesso = 'O nome não pode conter números.'
        elif any(a['matricula'] == matricula and a.get('cpf_professor') == cpf_professor for a in data.get('alunos', [])):
            sucesso = 'Já existe um aluno com essa matrícula!'
        else:
            data.setdefault('alunos', []).append({
                'matricula': matricula,
                'nome': nome,
                'cpf_professor': cpf_professor
            })
            save_data(data)
            sucesso = 'Aluno cadastrado com sucesso!'
    return render(request, 'cadastro/cadastrar_aluno.html', {'sucesso': sucesso})
# Detalhe da disciplina
def detalhe_disciplina(request, disciplina_id):
    data = load_data()
    cpf_professor = request.session.get('usuario')
    disciplinas = [d for d in data.get('disciplinas', []) if d.get('cpf_professor') == cpf_professor]
    if 0 <= disciplina_id < len(disciplinas):
        disciplina = disciplinas[disciplina_id]
        alunos = [a for a in data.get('alunos', []) if a.get('cpf_professor') == cpf_professor]
        sucesso = None

        if 'alunos' not in disciplina:
            disciplina['alunos'] = []
        if request.method == 'POST':
            matricula = request.POST.get('aluno_matricula')
            if matricula and matricula not in [a['matricula'] for a in disciplina['alunos']]:
                aluno = next((a for a in alunos if a['matricula'] == matricula), None)
                if aluno:
                    disciplina['alunos'].append({
                        'matricula': aluno['matricula'],
                        'nome': aluno['nome'],
                        'nota_1va': None,
                        'nota_2va': None,
                        'nota_3va': None,
                        'nota_final': None
                    })
                    save_data(data)
                    sucesso = 'Aluno adicionado com sucesso!'
        matriculas_na_disciplina = [a['matricula'] for a in disciplina['alunos']]
        alunos_disponiveis = [a for a in alunos if a['matricula'] not in matriculas_na_disciplina]
        alunos_disciplina = []
        for a in disciplina['alunos']:
            notas = [a.get('nota_1va'), a.get('nota_2va'), a.get('nota_3va'), a.get('nota_final')]
            notas_validas = [n for n in notas[:2] if n is not None]
            media_geral = None
            situacao = None
            if len(notas_validas) == 2:
                media = sum(notas_validas) / 2
                if media >= 7:
                    media_geral = media
                    situacao = "APV"
                elif a.get('nota_3va') is not None:
                    notas_3 = notas_validas + [a.get('nota_3va')]
                    media_3 = sum(n for n in notas_3 if n is not None) / 3
                    if media_3 >= 7:
                        media_geral = media_3
                        situacao = "APV"
                    elif a.get('nota_final') is not None:
                        notas_final = notas_3 + [a.get('nota_final')]
                        media_final = sum(n for n in notas_final if n is not None) / 4
                        media_geral = media_final
                        situacao = "APV" if media_final >= 7 else "RPV"
                    else:
                        situacao = None
                elif a.get('nota_final') is not None:
                    notas_final = notas_validas + [a.get('nota_final')]
                    media_final = sum(n for n in notas_final if n is not None) / 3
                    media_geral = media_final
                    situacao = "APV" if media_final >= 7 else "RPV"
                else:
                    situacao = None
            alunos_disciplina.append({
                **a,
                'media_geral': media_geral,
                'situacao': situacao
            })
        return render(request, 'cadastro/detalhe_disciplina.html', {
            'disciplina': disciplina,
            'alunos_disponiveis': alunos_disponiveis,
            'alunos_disciplina': alunos_disciplina,
            'sucesso': sucesso
        })
    else:
        return render(request, 'cadastro/detalhe_disciplina.html', {'disciplina': None})
# Lista de alunos do professor logado
def lista_alunos(request):
    data = load_data()
    cpf_professor = request.session.get('usuario')
    alunos = sorted(
        [a for a in data.get('alunos', []) if a.get('cpf_professor') == cpf_professor],
        key=lambda x: x['nome'].lower()
    )
    return render(request, 'cadastro/lista_alunos.html', {'alunos': alunos})

def logout_view(request):
    request.session.flush()
    return redirect('home')

def cadastrar_questao(request):
    sucesso = None
    error = None
    data = load_data()
    cpf_professor = request.session.get('usuario')
    
    # Buscar disciplinas do professor logado
    disciplinas_professor = [d['nome'] for d in data.get('disciplinas', []) if d.get('cpf_professor') == cpf_professor]
    
    # Verificar se veio uma disciplina específica via GET
    disciplina_selecionada = request.GET.get('disciplina', '')
    
    if request.method == 'POST':
        enunciado = request.POST.get('enunciado')
        alternativa_a = request.POST.get('alternativa_a')
        alternativa_b = request.POST.get('alternativa_b')
        alternativa_c = request.POST.get('alternativa_c')
        alternativa_d = request.POST.get('alternativa_d')
        alternativa_e = request.POST.get('alternativa_e')
        resposta_correta = request.POST.get('resposta_correta')
        disciplina = request.POST.get('disciplina')
        
        # Validações
        if not all([enunciado, alternativa_a, alternativa_b, alternativa_c, alternativa_d, alternativa_e, resposta_correta, disciplina]):
            error = 'Todos os campos são obrigatórios!'
        elif disciplina not in disciplinas_professor:
            error = 'Disciplina inválida!'
        else:
            # Gerar ID único baseado no timestamp
            import time
            questao_id = int(time.time() * 1000)  # Timestamp em milissegundos
            
            # Salvar questão
            questao = {
                'id': questao_id,
                'enunciado': enunciado,
                'alternativa_a': alternativa_a,
                'alternativa_b': alternativa_b,
                'alternativa_c': alternativa_c,
                'alternativa_d': alternativa_d,
                'alternativa_e': alternativa_e,
                'resposta_correta': resposta_correta,
                'cpf_professor': cpf_professor,
                'disciplina_nome': disciplina
            }
            
            data.setdefault('questoes', []).append(questao)
            save_data(data)
            sucesso = 'Questão cadastrada com sucesso!'
    
    return render(request, 'cadastro/cadastrar_questao.html', {
        'sucesso': sucesso,
        'error': error,
        'disciplinas': disciplinas_professor,
        'disciplina_selecionada': disciplina_selecionada
    })

def lista_questoes(request):
    data = load_data()
    cpf_professor = request.session.get('usuario')
    questoes = [q for q in data.get('questoes', []) if q.get('cpf_professor') == cpf_professor]
    
    # Migrar questões sem ID (para compatibilidade com questões antigas)
    import time
    questoes_modificadas = False
    for questao in questoes:
        if 'id' not in questao:
            questao['id'] = int(time.time() * 1000) + hash(questao['enunciado']) % 10000
            questoes_modificadas = True
    
    if questoes_modificadas:
        save_data(data)
    
    # Verificar se veio uma disciplina específica via GET
    disciplina_filtro = request.GET.get('disciplina', '')
    if disciplina_filtro:
        questoes = [q for q in questoes if q['disciplina_nome'] == disciplina_filtro]
    
    total_questoes = len(questoes)
    
    return render(request, 'cadastro/lista_questoes.html', {
        'questoes': questoes,
        'total_questoes': total_questoes,
        'disciplina_filtro': disciplina_filtro
    })

def gerar_prova(request):
    data = load_data()
    cpf_professor = request.session.get('usuario')
    questoes = [q for q in data.get('questoes', []) if q.get('cpf_professor') == cpf_professor]
    
    # Migrar questões sem ID (para compatibilidade com questões antigas)
    import time
    questoes_modificadas = False
    for questao in questoes:
        if 'id' not in questao:
            questao['id'] = int(time.time() * 1000) + hash(questao['enunciado']) % 10000
            questoes_modificadas = True
    
    if questoes_modificadas:
        save_data(data)
    
    # Verificar se veio uma disciplina específica via GET
    disciplina_selecionada = request.GET.get('disciplina', '')
    
    # Se veio de uma disciplina específica, filtrar questões apenas dessa disciplina
    if disciplina_selecionada:
        questoes_disponiveis = [q for q in questoes if q['disciplina_nome'] == disciplina_selecionada]
        disciplinas_professor = [disciplina_selecionada]
    else:
        questoes_disponiveis = questoes
        # Buscar todas as disciplinas do professor logado para filtro
        disciplinas_professor = list(set([q['disciplina_nome'] for q in questoes]))
    
    if request.method == 'POST':
        # Verificar se é seleção manual ou automática
        modo_selecao = request.POST.get('modo_selecao', 'automatico')
        print(f"DEBUG: Modo de seleção recebido: {modo_selecao}")  # Debug
        print(f"DEBUG: Dados POST: {request.POST}")  # Debug
        
        if modo_selecao == 'manual':
            # Seleção manual - redirecionar para página de seleção
            disciplina_filtro = request.POST.get('disciplina_filtro', '')
            print(f"DEBUG: Redirecionando para seleção manual com disciplina: {disciplina_filtro}")  # Debug
            if disciplina_filtro and disciplina_filtro != 'todas':
                return redirect(f"{reverse('selecionar_questoes')}?disciplina={disciplina_filtro}")
            else:
                return redirect(reverse('selecionar_questoes'))
        
        # Seleção automática (modo original)
        quantidade = int(request.POST.get('quantidade', 0))
        disciplina_filtro = request.POST.get('disciplina_filtro', '')
        
        # Filtrar por disciplina se selecionada
        questoes_filtradas = questoes_disponiveis
        if disciplina_filtro and disciplina_filtro != 'todas':
            questoes_filtradas = [q for q in questoes_disponiveis if q['disciplina_nome'] == disciplina_filtro]
        
        # Validar quantidade
        if quantidade <= 0 or quantidade > len(questoes_filtradas):
            error = f'Quantidade inválida! Deve ser entre 1 e {len(questoes_filtradas)} questões.'
            return render(request, 'cadastro/gerar_prova.html', {
                'error': error,
                'total_questoes': len(questoes_disponiveis),
                'disciplinas': disciplinas_professor,
                'disciplina_selecionada': disciplina_selecionada
            })
        
        # Selecionar questões aleatoriamente
        import random
        questoes_selecionadas = random.sample(questoes_filtradas, quantidade)
        
        return render(request, 'cadastro/visualizar_prova.html', {
            'questoes': questoes_selecionadas,
            'quantidade': quantidade,
            'disciplina': disciplina_filtro if disciplina_filtro != 'todas' else disciplina_selecionada or 'Múltiplas disciplinas'
        })
    
    return render(request, 'cadastro/gerar_prova.html', {
        'total_questoes': len(questoes_disponiveis),
        'disciplinas': disciplinas_professor,
        'disciplina_selecionada': disciplina_selecionada
    })

def selecionar_questoes(request):
    data = load_data()
    cpf_professor = request.session.get('usuario')
    questoes = [q for q in data.get('questoes', []) if q.get('cpf_professor') == cpf_professor]
    
    # Migrar questões sem ID (para compatibilidade com questões antigas)
    import time
    questoes_modificadas = False
    for questao in questoes:
        if 'id' not in questao:
            questao['id'] = int(time.time() * 1000) + hash(questao['enunciado']) % 10000
            questoes_modificadas = True
    
    if questoes_modificadas:
        save_data(data)
    
    # Filtrar por disciplina se especificada
    disciplina_filtro = request.GET.get('disciplina', '')
    if disciplina_filtro and disciplina_filtro != 'todas':
        questoes = [q for q in questoes if q['disciplina_nome'] == disciplina_filtro]
    
    if request.method == 'POST':
        # Obter questões selecionadas
        questoes_selecionadas_ids = request.POST.getlist('questoes_selecionadas')
        
        if not questoes_selecionadas_ids:
            error = 'Você deve selecionar pelo menos uma questão!'
            return render(request, 'cadastro/selecionar_questoes.html', {
                'questoes': questoes,
                'error': error,
                'disciplina_filtro': disciplina_filtro
            })
        
        # Buscar as questões selecionadas
        questoes_selecionadas = []
        for questao in questoes:
            if str(questao.get('id', '')) in questoes_selecionadas_ids:
                questoes_selecionadas.append(questao)
        
        return render(request, 'cadastro/visualizar_prova.html', {
            'questoes': questoes_selecionadas,
            'quantidade': len(questoes_selecionadas),
            'disciplina': disciplina_filtro if disciplina_filtro != 'todas' else 'Múltiplas disciplinas',
            'selecao_manual': True
        })
    
    return render(request, 'cadastro/selecionar_questoes.html', {
        'questoes': questoes,
        'disciplina_filtro': disciplina_filtro,
        'total_questoes': len(questoes)
    })