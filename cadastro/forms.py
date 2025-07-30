#Projeto django
from django import forms

class ProfessorForm(forms.Form):
    nome = forms.CharField(max_length=100, label='Nome do Professor')
    email = forms.EmailField(label='Email do Professor')

class DisciplinaForm(forms.Form):
    nome = forms.CharField(max_length=100, label='Nome da Disciplina')
    professor = forms.CharField(max_length=100, label='Professor Responsável')

class AlunoForm(forms.Form):
    nome = forms.CharField(max_length=100, label='Nome do Aluno')
    matricula = forms.CharField(max_length=20, label='Matrícula do Aluno')

class QuestaoForm(forms.Form):
    ALTERNATIVAS_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
        ('E', 'E'),
    ]
    
    enunciado = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'cols': 50}),
        label='Enunciado da Questão'
    )
    alternativa_a = forms.CharField(max_length=500, label='Alternativa A')
    alternativa_b = forms.CharField(max_length=500, label='Alternativa B')
    alternativa_c = forms.CharField(max_length=500, label='Alternativa C')
    alternativa_d = forms.CharField(max_length=500, label='Alternativa D')
    alternativa_e = forms.CharField(max_length=500, label='Alternativa E')
    resposta_correta = forms.ChoiceField(
        choices=ALTERNATIVAS_CHOICES,
        widget=forms.RadioSelect,
        label='Resposta Correta'
    )
    disciplina = forms.CharField(max_length=100, label='Disciplina')