# BANCO DE DADOS 

from django.db import models

class Professor(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.nome

class Disciplina(models.Model):
    nome = models.CharField(max_length=100)
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE, related_name='disciplinas')

    def __str__(self):
        return self.nome

class Aluno(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    disciplinas = models.ManyToManyField(Disciplina, related_name='alunos')

    def __str__(self):
        return self.nome

class Questao(models.Model):
    ALTERNATIVAS_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
        ('E', 'E'),
    ]
    
    enunciado = models.TextField()
    alternativa_a = models.CharField(max_length=500)
    alternativa_b = models.CharField(max_length=500)
    alternativa_c = models.CharField(max_length=500)
    alternativa_d = models.CharField(max_length=500)
    alternativa_e = models.CharField(max_length=500)
    resposta_correta = models.CharField(max_length=1, choices=ALTERNATIVAS_CHOICES)
    cpf_professor = models.CharField(max_length=11)  # Para compatibilidade com o sistema atual
    disciplina_nome = models.CharField(max_length=100)  # Para facilitar consultas
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Questão: {self.enunciado[:50]}..."

    class Meta:
        verbose_name = "Questão"
        verbose_name_plural = "Questões"