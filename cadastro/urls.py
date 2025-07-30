#AS PATHS DIRECIONAMENTO

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('cadastrar_disciplina/', views.cadastrar_disciplina, name='cadastrar_disciplina'),
    path('cadastrar_aluno/', views.cadastrar_aluno, name='cadastrar_aluno'),
    path('cadastrar_questao/', views.cadastrar_questao, name='cadastrar_questao'),
    path('lista_questoes/', views.lista_questoes, name='lista_questoes'),
    path('gerar_prova/', views.gerar_prova, name='gerar_prova'),
    path('selecionar_questoes/', views.selecionar_questoes, name='selecionar_questoes'),
    path('login/', views.login_view, name='login'),
    path('cadastro_usuario/', views.cadastro_usuario, name='cadastro_usuario'),
    path('disciplina/<int:disciplina_id>/', views.detalhe_disciplina, name='detalhe_disciplina'),
    path('logout/', views.logout_view, name='logout'),
    path('alunos/', views.lista_alunos, name='lista_alunos'),
]