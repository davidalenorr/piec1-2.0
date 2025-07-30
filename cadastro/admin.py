#configurar o admin do django
from django.contrib import admin
from .models import Professor, Disciplina, Aluno

admin.site.register(Professor)
admin.site.register(Disciplina)
admin.site.register(Aluno)