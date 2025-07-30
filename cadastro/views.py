from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.urls import reverse
from .forms import ProfessorForm, DisciplinaForm, AlunoForm, QuestaoForm
from .models import Professor, Disciplina, Aluno, Questao, Prova, GabaritoProva, ResultadoAluno
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

def salvar_prova_e_gabarito(questoes_selecionadas, disciplina, cpf_professor, selecao_manual=False):
    """
    Salva a prova e seu gabarito no banco de dados
    """
    try:
        from .models import Questao
        
        # Buscar o professor
        professor = Professor.objects.filter(email__contains=cpf_professor).first()
        if not professor:
            # Se não encontrar por email, criar um professor temporário ou buscar de outra forma
            # Por enquanto, vamos criar um professor temporário
            data = load_data()
            usuario = next((u for u in data.get('usuarios', []) if u.get('cpf') == cpf_professor), None)
            if usuario:
                professor, created = Professor.objects.get_or_create(
                    email=f"{cpf_professor}@temp.com",
                    defaults={'nome': usuario.get('nome', 'Professor')}
                )
            else:
                return None
        
        # Criar a prova
        modo = "Manual" if selecao_manual else "Automática"
        titulo = f"Prova {disciplina} - {modo}"
        
        prova = Prova.objects.create(
            titulo=titulo,
            disciplina=disciplina,
            professor=professor,
            quantidade_questoes=len(questoes_selecionadas)
        )
        
        # Preparar IDs das questões e gabarito
        questoes_ids = []
        respostas_corretas = {}
        
        for questao in questoes_selecionadas:
            questao_id = questao.get('id')
            
            # Salvar questão no Django se não existir
            questao_django, created = Questao.objects.get_or_create(
                id=questao_id,
                defaults={
                    'enunciado': questao.get('enunciado', ''),
                    'alternativa_a': questao.get('alternativa_a', ''),
                    'alternativa_b': questao.get('alternativa_b', ''),
                    'alternativa_c': questao.get('alternativa_c', ''),
                    'alternativa_d': questao.get('alternativa_d', ''),
                    'alternativa_e': questao.get('alternativa_e', ''),
                    'resposta_correta': questao.get('resposta_correta', 'A'),
                    'cpf_professor': cpf_professor,
                    'disciplina_nome': questao.get('disciplina_nome', disciplina)
                }
            )
            
            questoes_ids.append(questao_id)
            respostas_corretas[str(questao_id)] = questao.get('resposta_correta')
        
        # Salvar IDs das questões na prova
        prova.set_questoes_ids_list(questoes_ids)
        prova.save()
        
        # Criar o gabarito
        gabarito = GabaritoProva.objects.create(prova=prova)
        gabarito.set_respostas_dict(respostas_corretas)
        gabarito.save()
        
        return prova
        
    except Exception as e:
        print(f"Erro ao salvar prova e gabarito: {e}")
        import traceback
        traceback.print_exc()
        return None
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

def detalhe_disciplina_por_nome(request, nome_disciplina):
    """View para acessar disciplina pelo nome em vez do índice"""
    data = load_data()
    cpf_professor = request.session.get('usuario')
    disciplinas = [d for d in data.get('disciplinas', []) if d.get('cpf_professor') == cpf_professor]
    
    # Buscar a disciplina pelo nome
    disciplina = None
    disciplina_id = None
    for i, d in enumerate(disciplinas):
        if d.get('nome') == nome_disciplina:
            disciplina = d
            disciplina_id = i
            break
    
    if disciplina:
        # Redirecionar para a view original com o ID correto
        return redirect('detalhe_disciplina', disciplina_id=disciplina_id)
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
        
        # Salvar a prova e gabarito no banco de dados
        prova_salva = salvar_prova_e_gabarito(
            questoes_selecionadas, 
            disciplina_filtro if disciplina_filtro != 'todas' else disciplina_selecionada or 'Múltiplas disciplinas',
            cpf_professor,
            selecao_manual=False
        )
        
        return render(request, 'cadastro/visualizar_prova.html', {
            'questoes': questoes_selecionadas,
            'quantidade': quantidade,
            'disciplina': disciplina_filtro if disciplina_filtro != 'todas' else disciplina_selecionada or 'Múltiplas disciplinas',
            'prova_id': prova_salva.id if prova_salva else None,
            'gabarito_salvo': prova_salva is not None
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
        
        # Salvar a prova e gabarito no banco de dados
        prova_salva = salvar_prova_e_gabarito(
            questoes_selecionadas,
            disciplina_filtro if disciplina_filtro != 'todas' else 'Múltiplas disciplinas',
            request.session.get('usuario'),
            selecao_manual=True
        )
        
        return render(request, 'cadastro/visualizar_prova.html', {
            'questoes': questoes_selecionadas,
            'quantidade': len(questoes_selecionadas),
            'disciplina': disciplina_filtro if disciplina_filtro != 'todas' else 'Múltiplas disciplinas',
            'selecao_manual': True,
            'prova_id': prova_salva.id if prova_salva else None,
            'gabarito_salvo': prova_salva is not None
        })
    
    return render(request, 'cadastro/selecionar_questoes.html', {
        'questoes': questoes,
        'disciplina_filtro': disciplina_filtro,
        'total_questoes': len(questoes)
    })

def listar_provas(request, disciplina=None):
    """Lista todas as provas criadas pelo professor logado, opcionalmente filtradas por disciplina"""
    cpf_professor = request.session.get('usuario')
    if not cpf_professor:
        return redirect('login')
    
    try:
        # Buscar professor
        professor = Professor.objects.filter(email__contains=cpf_professor).first()
        if professor:
            provas = Prova.objects.filter(professor=professor)
            
            # Filtrar por disciplina se especificada
            if disciplina:
                provas = provas.filter(disciplina=disciplina)
                
            provas = provas.order_by('-data_criacao')
        else:
            provas = []
        
        return render(request, 'cadastro/listar_provas.html', {
            'provas': provas,
            'disciplina_filtro': disciplina
        })
    except Exception as e:
        return render(request, 'cadastro/listar_provas.html', {
            'provas': [],
            'disciplina_filtro': disciplina,
            'error': f'Erro ao carregar provas: {str(e)}'
        })

def visualizar_gabarito(request, prova_id):
    """Visualiza o gabarito de uma prova específica"""
    cpf_professor = request.session.get('usuario')
    if not cpf_professor:
        return redirect('login')
    
    try:
        prova = Prova.objects.get(id=prova_id)
        gabarito = prova.gabarito
        
        # Verificar se o professor tem acesso a esta prova
        if prova.professor.email != f"{cpf_professor}@temp.com":
            return render(request, 'cadastro/erro.html', {
                'mensagem': 'Você não tem permissão para visualizar este gabarito.'
            })
        
        # Buscar as questões do gabarito
        questoes_ids = prova.get_questoes_ids_list()
        questoes = []
        
        # Buscar questões dos dados temporários (JSON)
        data = load_data()
        
        for questao_id in questoes_ids:
            for questao_data in data.get('questoes', []):
                # Converter ambos para o mesmo tipo para comparação
                if int(questao_data.get('id', 0)) == int(questao_id):
                    questoes.append(questao_data)
                    break
        
        respostas_corretas = gabarito.get_respostas_dict()
        
        return render(request, 'cadastro/visualizar_gabarito.html', {
            'prova': prova,
            'questoes': questoes,
            'respostas_corretas': respostas_corretas,
            'gabarito': gabarito,
            'debug_info': {
                'questoes_ids': questoes_ids,
                'questoes_encontradas': len(questoes),
                'total_questoes_sistema': len(data.get('questoes', []))
            }
        })
        
    except Prova.DoesNotExist:
        return render(request, 'cadastro/erro.html', {
            'mensagem': 'Prova não encontrada.'
        })
    except Exception as e:
        return render(request, 'cadastro/erro.html', {
            'mensagem': f'Erro ao carregar gabarito: {str(e)}'
        })

def processar_omr(request):
    """
    Função para processar respostas OMR e calcular notas
    Simula o processamento OMR até a implementação real
    """
    if request.method == 'POST':
        prova_id = request.POST.get('prova_id')
        aluno_matricula = request.POST.get('aluno_matricula')
        avaliacao = request.POST.get('avaliacao')
        foto_gabarito = request.FILES.get('foto_gabarito')
        
        try:
            prova = Prova.objects.get(id=prova_id)
            gabarito = prova.gabarito
            
            # SIMULAÇÃO DE OMR - Substituir pela implementação real
            # Por enquanto, vamos simular respostas detectadas
            import random
            respostas_corretas = gabarito.get_respostas_dict()
            questoes_ids = list(respostas_corretas.keys())
            
            # Simular detecção com 70-90% de acerto
            respostas_detectadas = []
            for questao_id in questoes_ids:
                resposta_correta = respostas_corretas[questao_id]
                # 80% de chance de acertar
                if random.random() < 0.8:
                    respostas_detectadas.append(resposta_correta)
                else:
                    # Escolher uma alternativa aleatória diferente
                    opcoes = ['A', 'B', 'C', 'D', 'E']
                    opcoes.remove(resposta_correta)
                    respostas_detectadas.append(random.choice(opcoes))
            
            # Calcular nota baseada na simulação
            acertos = 0
            for i, questao_id in enumerate(questoes_ids):
                if respostas_detectadas[i] == respostas_corretas[questao_id]:
                    acertos += 1
            
            total = len(questoes_ids)
            nota_final = round((acertos / total) * 10, 1)
            
            return JsonResponse({
                'success': True,
                'respostas_detectadas': respostas_detectadas,
                'acertos': acertos,
                'total': total,
                'nota': nota_final
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Método não permitido'})

def api_provas_disciplina(request, disciplina):
    """API para buscar provas de uma disciplina específica"""
    cpf_professor = request.session.get('usuario')
    if not cpf_professor:
        return JsonResponse({'error': 'Não autorizado'}, status=401)
    
    try:
        professor = Professor.objects.filter(email__contains=cpf_professor).first()
        if professor:
            provas = Prova.objects.filter(
                professor=professor, 
                disciplina=disciplina
            ).order_by('-data_criacao')
            
            provas_data = []
            for prova in provas:
                provas_data.append({
                    'id': prova.id,
                    'titulo': prova.titulo,
                    'disciplina': prova.disciplina,
                    'quantidade_questoes': prova.quantidade_questoes,
                    'data_criacao': prova.data_criacao.strftime('%d/%m/%Y %H:%M')
                })
            
            return JsonResponse(provas_data, safe=False)
        else:
            return JsonResponse({'error': 'Professor não encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def aplicar_nota_omr(request):
    """Aplica a nota calculada pelo OMR ao aluno"""
    if request.method == 'POST':
        try:
            import json
            data_request = json.loads(request.body)
            
            matricula = data_request.get('matricula')
            avaliacao = data_request.get('avaliacao')
            nota = float(data_request.get('nota', 0))
            
            # Carregar dados temporários
            data = load_data()
            cpf_professor = request.session.get('usuario')
            
            # Encontrar e atualizar a nota do aluno
            for disciplina in data.get('disciplinas', []):
                if disciplina.get('cpf_professor') == cpf_professor:
                    for aluno in disciplina.get('alunos', []):
                        if aluno.get('matricula') == matricula:
                            # Mapear nome da avaliação para o campo correspondente
                            campo_nota = {
                                '1VA': 'nota_1va',
                                '2VA': 'nota_2va', 
                                '3VA': 'nota_3va',
                                'Final': 'nota_final'
                            }.get(avaliacao)
                            
                            if campo_nota:
                                aluno[campo_nota] = nota
                                save_data(data)
                                return JsonResponse({'success': True})
            
            return JsonResponse({'success': False, 'error': 'Aluno não encontrado'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método não permitido'})


def editar_questao(request, questao_id):
    """Edita uma questão existente"""
    cpf_professor = request.session.get('usuario')
    if not cpf_professor:
        return redirect('login')
    
    data = load_data()
    questao = None
    
    # Verificar se veio uma disciplina específica via GET
    disciplina_filtro = request.GET.get('disciplina', '')
    
    # Encontrar a questão
    for q in data['questoes']:
        if q['id'] == questao_id:
            questao = q
            break
    
    if not questao:
        return redirect('lista_questoes')
    
    if request.method == 'POST':
        # Atualizar os dados da questão
        questao['enunciado'] = request.POST.get('enunciado')
        questao['alternativa_a'] = request.POST.get('alternativa_a')
        questao['alternativa_b'] = request.POST.get('alternativa_b')
        questao['alternativa_c'] = request.POST.get('alternativa_c')
        questao['alternativa_d'] = request.POST.get('alternativa_d')
        questao['alternativa_e'] = request.POST.get('alternativa_e')
        questao['resposta_correta'] = request.POST.get('resposta_correta')
        
        save_data(data)
        
        # Redirecionar baseado na disciplina
        if disciplina_filtro:
            return redirect(f'/cadastro/lista_questoes/?disciplina={disciplina_filtro}')
        else:
            return redirect('lista_questoes')
    
    # Preparar dados para o template
    disciplinas = data['disciplinas']
    return render(request, 'cadastro/editar_questao.html', {
        'questao': questao,
        'disciplinas': disciplinas,
        'disciplina_filtro': disciplina_filtro
    })


def excluir_questao(request, questao_id):
    """Exclui uma questão"""
    cpf_professor = request.session.get('usuario')
    if not cpf_professor:
        return JsonResponse({'success': False, 'error': 'Não autorizado'})
    
    if request.method == 'DELETE':
        try:
            data = load_data()
            
            # Encontrar e remover a questão
            questoes_originais = len(data['questoes'])
            data['questoes'] = [q for q in data['questoes'] if q['id'] != questao_id]
            
            if len(data['questoes']) < questoes_originais:
                save_data(data)
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'Questão não encontrada'})
                
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método não permitido'})


from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def excluir_prova(request, prova_id):
    """Exclui uma prova e todos os dados relacionados"""
    print(f"\n=== EXCLUIR PROVA CHAMADA ===")
    print(f"Método: {request.method}")
    print(f"Prova ID: {prova_id}")
    print(f"URL Path: {request.path}")
    
    cpf_professor = request.session.get('usuario')
    print(f"Usuario da sessão: {cpf_professor}")
    
    if not cpf_professor:
        print("ERRO: Usuário não autenticado")
        return JsonResponse({'success': False, 'error': 'Não autorizado'})
    
    if request.method in ['DELETE', 'POST']:
        try:
            from .models import Prova, GabaritoProva, ResultadoAluno, Professor
            
            # Buscar professor usando a mesma lógica da view listar_provas
            professor = Professor.objects.filter(email__contains=cpf_professor).first()
            print(f"Professor encontrado: {professor}")
            
            if not professor:
                print("ERRO: Professor não encontrado")
                return JsonResponse({'success': False, 'error': 'Professor não encontrado'})
            
            # Buscar a prova
            try:
                prova = Prova.objects.get(id=prova_id, professor=professor)
                print(f"PROVA ENCONTRADA: {prova}")
            except Prova.DoesNotExist:
                print(f"ERRO: Prova {prova_id} não encontrada para professor {professor}")
                return JsonResponse({'success': False, 'error': 'Prova não encontrada'})
            
            # Excluir tudo relacionado
            print("Excluindo resultados...")
            resultados_count = ResultadoAluno.objects.filter(prova=prova).count()
            ResultadoAluno.objects.filter(prova=prova).delete()
            print(f"Resultados excluídos: {resultados_count}")
            
            print("Excluindo gabaritos...")
            gabaritos_count = GabaritoProva.objects.filter(prova=prova).count()
            GabaritoProva.objects.filter(prova=prova).delete()
            print(f"Gabaritos excluídos: {gabaritos_count}")
            
            print("Excluindo prova...")
            prova.delete()
            
            print("SUCESSO: Prova excluída!")
            return JsonResponse({'success': True, 'message': 'Prova excluída com sucesso'})
                
        except Exception as e:
            print(f"ERRO EXCEPTION: {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'success': False, 'error': f'Erro interno: {str(e)}'})
    
    print(f"ERRO: Método {request.method} não permitido")
    return JsonResponse({'success': False, 'error': 'Método não permitido'})

def gerar_pdf_prova(request, prova_id):
    """Gera PDF de uma prova existente"""
    cpf_professor = request.session.get('usuario')
    if not cpf_professor:
        return redirect('login')
    
    try:
        from .models import Prova, Professor, Questao
        
        # Buscar professor usando a mesma lógica
        professor = Professor.objects.filter(email__contains=cpf_professor).first()
        if not professor:
            return redirect('login')
        
        # Buscar a prova
        prova = Prova.objects.get(id=prova_id, professor=professor)
        
        # Buscar as questões da prova
        questoes_ids = prova.get_questoes_ids_list()
        questoes = []
        
        print(f"DEBUG PDF: Prova ID {prova_id}, Questões IDs: {questoes_ids}")
        
        # Primeiro tentar buscar no Django
        for questao_id in questoes_ids:
            try:
                questao = Questao.objects.get(id=questao_id)
                questoes.append({
                    'enunciado': questao.enunciado,
                    'alternativa_a': questao.alternativa_a,
                    'alternativa_b': questao.alternativa_b,
                    'alternativa_c': questao.alternativa_c,
                    'alternativa_d': questao.alternativa_d,
                    'alternativa_e': questao.alternativa_e,
                    'resposta_correta': questao.resposta_correta,
                    'id': questao.id
                })
                print(f"DEBUG PDF: Questão Django encontrada: {questao_id}")
            except Questao.DoesNotExist:
                print(f"DEBUG PDF: Questão Django não encontrada: {questao_id}")
                # Fallback para sistema de arquivos JSON
                data = load_data()
                questoes_json = data.get('questoes', [])
                for q in questoes_json:
                    if q.get('id') == questao_id:
                        questoes.append(q)
                        print(f"DEBUG PDF: Questão JSON encontrada: {questao_id}")
                        break
        
        print(f"DEBUG PDF: Total de questões encontradas: {len(questoes)}")
        
        return render(request, 'cadastro/visualizar_prova.html', {
            'questoes': questoes,
            'quantidade': len(questoes),
            'disciplina': prova.disciplina,
            'prova_id': prova.id,
            'gabarito_salvo': True,
            'modo_pdf': True,  # Flag para indicar que é modo PDF
            'professor_nome': professor.nome,  # Adicionar nome do professor
            'data_criacao': prova.data_criacao
        })
        
    except Prova.DoesNotExist:
        print(f"DEBUG PDF: Prova {prova_id} não encontrada")
        return redirect('listar_provas')
    except Exception as e:
        print(f"DEBUG PDF: Erro: {str(e)}")
        import traceback
        traceback.print_exc()
        return redirect('listar_provas')