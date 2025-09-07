from django.contrib import admin
from .models import Aluno, Presenca, Pagamento

@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'telefone', 'nome_responsavel', 'status', 'data_nascimento')
    list_filter = ('status',)
    search_fields = ('nome', 'telefone', 'nome_responsavel')
    date_hierarchy = 'data_cadastro'
    list_per_page = 20


@admin.register(Presenca)
class PresencaAdmin(admin.ModelAdmin):
    list_display = ('aluno', 'data', 'presente')
    list_filter = ('data', 'presente')
    search_fields = ('aluno__nome',)
    date_hierarchy = 'data'
    list_per_page = 50


@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    list_display = ('aluno', 'mes_referencia', 'valor', 'pago', 'data_pagamento')
    list_filter = ('pago', 'mes_referencia')
    search_fields = ('aluno__nome',)
    date_hierarchy = 'mes_referencia'
    list_per_page = 50

