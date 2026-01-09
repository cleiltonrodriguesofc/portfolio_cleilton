from django.contrib import admin
from .models import (
    Amostra, ActivityLog, PesagemCaminhao, NotaCarregamento, 
    RegistroFinanceiro, Pagamento, Invoice, NFe, NFeItem, 
    EmitterConfig, CertificateConfig, TaxProfile, NFeEvent
)

@admin.register(Amostra)
class AmostraAdmin(admin.ModelAdmin):
    list_display = ('id_amostra', 'tipo_grao', 'status', 'created_by', 'data_criacao')
    list_filter = ('status', 'tipo_grao', 'data_criacao')
    search_fields = ('id_amostra', 'created_by__username')

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'timestamp')
    list_filter = ('timestamp', 'action')
    search_fields = ('user__username', 'action')

@admin.register(PesagemCaminhao)
class PesagemCaminhaoAdmin(admin.ModelAdmin):
    list_display = ('placa', 'motorista', 'status', 'tipo_grao', 'peso_liquido')
    list_filter = ('status', 'tipo_grao', 'data_final')
    search_fields = ('placa', 'motorista', 'transportadora')

@admin.register(NotaCarregamento)
class NotaCarregamentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome_recebedor', 'tipo_grao', 'quantidade_sacos', 'valor_total')
    list_filter = ('tipo_grao', 'data_criacao')
    search_fields = ('nome_recebedor', 'cpf_cnpj_recebedor')

@admin.register(RegistroFinanceiro)
class RegistroFinanceiroAdmin(admin.ModelAdmin):
    list_display = ('nota', 'status_pagamento', 'valor_pago', 'lucro')
    list_filter = ('status_pagamento',)

@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    list_display = ('registro_financeiro', 'valor', 'metodo_pagamento', 'data_pagamento')
    list_filter = ('metodo_pagamento', 'data_pagamento')

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('number', 'customer_name', 'total_amount', 'status', 'issue_date')
    list_filter = ('status', 'issue_date')
    search_fields = ('number', 'customer_name', 'customer_document')

class NFeItemInline(admin.TabularInline):
    model = NFeItem
    extra = 0

@admin.register(NFe)
class NFeAdmin(admin.ModelAdmin):
    list_display = ('number', 'status', 'environment', 'created_at')
    list_filter = ('status', 'environment')
    inlines = [NFeItemInline]

@admin.register(EmitterConfig)
class EmitterConfigAdmin(admin.ModelAdmin):
    list_display = ('razao_social', 'cnpj', 'ambiente', 'production_enabled')

@admin.register(CertificateConfig)
class CertificateConfigAdmin(admin.ModelAdmin):
    list_display = ('name', 'valid_to', 'is_active')
    list_filter = ('is_active', 'valid_to')

@admin.register(TaxProfile)
class TaxProfileAdmin(admin.ModelAdmin):
    list_display = ('grain_type', 'ncm', 'cfop_inside_state', 'accountant_validated')
    list_filter = ('grain_type', 'accountant_validated')

@admin.register(NFeEvent)
class NFeEventAdmin(admin.ModelAdmin):
    list_display = ('nfe', 'event_type', 'status', 'created_at')
    list_filter = ('event_type', 'status')
