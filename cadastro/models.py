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
    cpf_professor = models.CharField(max_length=11)  
    disciplina_nome = models.CharField(max_length=100)  
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Questão: {self.enunciado[:50]}..."

    class Meta:
        verbose_name = "Questão"
        verbose_name_plural = "Questões"

class Prova(models.Model):
    titulo = models.CharField(max_length=200, default="Prova")
    disciplina = models.CharField(max_length=100)
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE, related_name='provas')
    quantidade_questoes = models.IntegerField()
    data_criacao = models.DateTimeField(auto_now_add=True)
    questoes_ids = models.TextField()

    def __str__(self):
        return f"{self.titulo} - {self.disciplina} ({self.quantidade_questoes} questões)"
    
    def get_questoes_ids_list(self):
        """Retorna a lista de IDs das questões"""
        import json
        try:
            return json.loads(self.questoes_ids)
        except:
            return []
    
    def set_questoes_ids_list(self, ids_list):
        """Define a lista de IDs das questões"""
        import json
        self.questoes_ids = json.dumps(ids_list)
    
    class Meta:
        verbose_name = "Prova"
        verbose_name_plural = "Provas"
        ordering = ['-data_criacao']

class GabaritoProva(models.Model):
    prova = models.OneToOneField(Prova, on_delete=models.CASCADE, related_name='gabarito')
    respostas_corretas = models.TextField()
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Gabarito - {self.prova.titulo}"
    
    def get_respostas_dict(self):
        """Retorna o dicionário de respostas corretas"""
        import json
        try:
            return json.loads(self.respostas_corretas)
        except:
            return {}
    
    def set_respostas_dict(self, respostas_dict):
        """Define o dicionário de respostas corretas"""
        import json
        self.respostas_corretas = json.dumps(respostas_dict)
    
    def calcular_nota(self, respostas_aluno):
        """
        Calcula a nota do aluno baseado nas respostas
        respostas_aluno: dict {questao_id: resposta_aluno}
        retorna: (acertos, total_questoes, nota_percentual)
        """
        gabarito = self.get_respostas_dict()
        total_questoes = len(gabarito)
        acertos = 0
        
        for questao_id, resposta_correta in gabarito.items():
            resposta_aluno = respostas_aluno.get(str(questao_id), '')
            if resposta_aluno.upper() == resposta_correta.upper():
                acertos += 1
        
        nota_percentual = (acertos / total_questoes * 100) if total_questoes > 0 else 0
        return acertos, total_questoes, round(nota_percentual, 2)
    
    class Meta:
        verbose_name = "Gabarito da Prova"
        verbose_name_plural = "Gabaritos das Provas"

class ResultadoAluno(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='resultados')
    prova = models.ForeignKey(Prova, on_delete=models.CASCADE, related_name='resultados')
    respostas_aluno = models.TextField()  # JSON com {questao_id: resposta_aluno}
    acertos = models.IntegerField()
    total_questoes = models.IntegerField()
    nota_percentual = models.DecimalField(max_digits=5, decimal_places=2)
    data_realizacao = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.aluno.nome} - {self.prova.titulo} ({self.nota_percentual}%)"
    
    def get_respostas_dict(self):
        """Retorna o dicionário de respostas do aluno"""
        import json
        try:
            return json.loads(self.respostas_aluno)
        except:
            return {}
    
    def set_respostas_dict(self, respostas_dict):
        """Define o dicionário de respostas do aluno"""
        import json
        self.respostas_aluno = json.dumps(respostas_dict)
    
    class Meta:
        verbose_name = "Resultado do Aluno"
        verbose_name_plural = "Resultados dos Alunos"
        unique_together = ['aluno', 'prova'] 
        ordering = ['-data_realizacao']