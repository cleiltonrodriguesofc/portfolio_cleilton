from django.urls import path
from . import views
# from django.contrib.auth.decorators import login_required

urlpatterns = [
    # logout
    path('logout/', views.logout, name='logout'),
    # home page (dashboard)
    path('', views.dashboard, name='dashboard'),
    
    # urls for students
    path('alunos/', views.aluno_list, name='aluno_list'),
    path('alunos/adicionar/', views.aluno_create, name='aluno_create'),
    path('alunos/<int:pk>/editar/', views.aluno_update, name='aluno_update'),
    path('alunos/<int:pk>/detalhes/', views.aluno_detail, name='aluno_detail'),
    
    # urls for attendance
    path('presenca/', views.presenca_list, name='presenca_list'),
    path('presenca/marcar/', views.presenca_create, name='presenca_create'),
    
    # urls for payments
    path('pagamentos/', views.pagamento_list, name='pagamento_list'),
    path('pagamentos/adicionar/', views.pagamento_create, name='pagamento_create'),
    path('pagamentos/<int:pk>/editar/', views.pagamento_update, name='pagamento_update'),
    
    # urls for reports
    path('relatorios/presenca/', views.relatorio_presenca, name='relatorio_presenca'),
    path('relatorios/pagamentos/', views.relatorio_pagamentos, name='relatorio_pagamentos'),
    
    # urls for messages
    path('mensagens/', views.mensagens, name='mensagens'),
]

