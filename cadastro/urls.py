#AS PATHS DIRECIONAMENTO

from django.urls import path
from . import views

urlpatterns = [
    # URL para a página inicial
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
    path('disciplina/nome/<str:nome_disciplina>/', views.detalhe_disciplina_por_nome, name='detalhe_disciplina_por_nome'),
    path('logout/', views.logout_view, name='logout'),
    path('alunos/', views.lista_alunos, name='lista_alunos'),
    # URLs para questões
    path('questao/editar/<int:questao_id>/', views.editar_questao, name='editar_questao'),
    path('questao/excluir/<int:questao_id>/', views.excluir_questao, name='excluir_questao'),
    # Novas URLs para provas e gabaritos
    path('provas/', views.listar_provas, name='listar_provas'),
    path('provas/<str:disciplina>/', views.listar_provas, name='listar_provas_disciplina'),
    path('prova/excluir/<int:prova_id>/', views.excluir_prova, name='excluir_prova'),
    path('prova/pdf/<int:prova_id>/', views.gerar_pdf_prova, name='gerar_pdf_prova'),
    path('gabarito/<int:prova_id>/', views.visualizar_gabarito, name='visualizar_gabarito'),
    path('processar_omr/', views.processar_omr, name='processar_omr'),
    path('aplicar_nota_omr/', views.aplicar_nota_omr, name='aplicar_nota_omr'),
    path('api/provas/<str:disciplina>/', views.api_provas_disciplina, name='api_provas_disciplina'),
]