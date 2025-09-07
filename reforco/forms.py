from django import forms
from .models import Aluno, Presenca, Pagamento
from django.utils import timezone

class AlunoForm(forms.ModelForm):
    """
    Formulário para criação e edição de alunos.
    """
    class Meta:
        model = Aluno
        fields = ["nome", "telefone", "nome_responsavel", "data_nascimento", "data_entrada", "status", "observacoes"]
        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nome completo"}),
            "telefone": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: (11) 99999-9999"}),
            "nome_responsavel": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nome do responsável (se aplicável)"}),
            "data_nascimento": forms.DateInput(attrs={"class": "form-control datepicker", "placeholder": "DD/MM/AAAA"}),
            "data_entrada": forms.DateInput(attrs={"class": "form-control datepicker", "placeholder": "DD/MM/AAAA"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "observacoes": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Observações adicionais"}),
        }


class PresencaForm(forms.ModelForm):
    """
    Formulário para registro de presença.
    """
    class Meta:
        model = Presenca
        fields = ["aluno", "data", "presente"]
        widgets = {
            "aluno": forms.Select(attrs={"class": "form-select"}),
            "data": forms.DateInput(attrs={"class": "form-control datepicker", "placeholder": "DD/MM/AAAA"}),
            "presente": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class PagamentoForm(forms.ModelForm):
    """
    Formulário para registro de pagamento.
    """
    class Meta:
        model = Pagamento
        fields = ["aluno", "mes_referencia", "valor", "pago", "data_pagamento", "observacao"]
        widgets = {
            "aluno": forms.Select(attrs={"class": "form-select"}),
            "mes_referencia": forms.DateInput(attrs={"class": "form-control datepicker", "placeholder": "MM/AAAA"}),
            "valor": forms.NumberInput(attrs={"class": "form-control", "placeholder": "R$ 0,00"}),
            "pago": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "data_pagamento": forms.DateInput(attrs={"class": "form-control datepicker", "placeholder": "DD/MM/AAAA"}),
            "observacao": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Observações sobre o pagamento"}),
        }


class PresencaMultiForm(forms.Form):
    """
    Formulário para marcação de presença de múltiplos alunos.
    """
    data = forms.DateField(
        label="Data",
        widget=forms.DateInput(attrs={"class": "form-control datepicker", "placeholder": "DD/MM/AAAA"}),
        initial=timezone.now().date(),
        input_formats=["%d/%m/%Y", "%Y-%m-%d"] # Adiciona formatos de entrada
    )
    
    def __init__(self, *args, **kwargs):
        alunos = kwargs.pop("alunos", None)
        data_inicial = kwargs.pop("data_inicial", timezone.now().date()) # Novo parâmetro
        super(PresencaMultiForm, self).__init__(*args, **kwargs)
        
        self.fields["data"].initial = data_inicial # Define a data inicial

        if alunos:
            for aluno in alunos:
                self.fields[f"aluno_{aluno.id}"] = forms.BooleanField(
                    label=aluno.nome,
                    required=False,
                    widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
                )


