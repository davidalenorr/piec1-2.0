#!/usr/bin/env python
"""
Script para migrar questões do sistema JSON para o banco Django
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_cadastro.settings')
django.setup()

from cadastro.models import Professor, Questao
from cadastro.views import load_data

def migrar_questoes():
    """Migra questões do JSON para o Django"""
    print("Iniciando migração de questões...")
    
    # Carregar dados do JSON
    data = load_data()
    questoes_json = data.get('questoes', [])
    usuarios = data.get('usuarios', [])
    
    print(f"Encontradas {len(questoes_json)} questões no JSON")
    
    migradas = 0
    erros = 0
    
    for questao in questoes_json:
        try:
            # Buscar professor
            cpf_professor = questao.get('cpf_professor')
            if not cpf_professor:
                print(f"Questão sem CPF do professor: {questao.get('id')}")
                continue
                
            # Buscar professor no Django
            professor = Professor.objects.filter(email__contains=cpf_professor).first()
            
            if not professor:
                # Criar professor se não existir
                usuario = next((u for u in usuarios if u.get('cpf') == cpf_professor), None)
                if usuario:
                    professor, created = Professor.objects.get_or_create(
                        email=f"{cpf_professor}@temp.com",
                        defaults={'nome': usuario.get('nome', 'Professor')}
                    )
                    if created:
                        print(f"Professor criado: {professor.nome}")
                else:
                    print(f"Usuário não encontrado para CPF: {cpf_professor}")
                    continue
            
            # Criar questão no Django se não existir
            questao_id = questao.get('id')
            if not questao_id:
                print(f"Questão sem ID: {questao}")
                continue
                
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
                    'disciplina_nome': questao.get('disciplina_nome', 'Não informada')
                }
            )
            
            if created:
                migradas += 1
                print(f"Questão migrada: {questao_id}")
            else:
                print(f"Questão já existe: {questao_id}")
                
        except Exception as e:
            erros += 1
            print(f"Erro ao migrar questão {questao.get('id', 'sem ID')}: {e}")
    
    print(f"\nMigração concluída:")
    print(f"- Questões migradas: {migradas}")
    print(f"- Erros: {erros}")
    print(f"- Total no Django: {Questao.objects.count()}")

if __name__ == "__main__":
    migrar_questoes()
