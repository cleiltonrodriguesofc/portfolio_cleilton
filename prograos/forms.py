from django import forms
from .models import Amostra, PesagemCaminhao, NotaCarregamento, Pagamento


class PagamentoForm(forms.ModelForm):
    class Meta:
        model = Pagamento
        fields = ['valor', 'data_pagamento', 'metodo_pagamento', 'observacoes', 'comprovante']
        widgets = {
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),

            # --- correction applied here ---
            'data_pagamento': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'  # <-- format added
            ),
            # -----------------------------

            'metodo_pagamento': forms.Select(attrs={'class': 'form-select'}),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Detalhes do pagamento, se necessário...'
            }),
            'comprovante': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'valor': 'Valor Pago (R$)',
            'data_pagamento': 'Data e Hora do Pagamento',
            'metodo_pagamento': 'Método de Pagamento',
            'observacoes': 'Observações (Opcional)',
            'comprovante': 'Comprovante (Opcional)',
        }


class NotaCarregamentoForm(forms.ModelForm):
    class Meta:
        model = NotaCarregamento
        fields = [
            'nome_recebedor', 'cpf_cnpj_recebedor', 'telefone_recebedor',
            'endereco_recebedor', 'tipo_grao', 'quantidade_sacos', 'preco_por_saco', 'pesagem'
        ]
        widgets = {
            'nome_recebedor': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Nome do recebedor'}),
            'cpf_cnpj_recebedor': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': '000.000.000-00 ou 00.000.000/0000-00'}),
            'telefone_recebedor': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': '(00) 00000-0000'}),
            'endereco_recebedor': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': 'Endereço completo'}),
            'tipo_grao': forms.Select(
                attrs={
                    'class': 'form-select'},
                choices=NotaCarregamento.GRAO_CHOICES),
            'quantidade_sacos': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.001',
                    'placeholder': '0.000'}),
            'preco_por_saco': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.01',
                    'placeholder': '0.00'}),
            'pesagem': forms.Select(
                attrs={
                    'class': 'form-select'}),
        }
        labels = {
            'nome_recebedor': 'Nome do Recebedor',
            'cpf_cnpj_recebedor': 'CPF/CNPJ',
            'telefone_recebedor': 'Telefone',
            'endereco_recebedor': 'Endereço',
            'tipo_grao': 'Tipo de Grão',
            'quantidade_sacos': 'Quantidade de Sacos',
            'preco_por_saco': 'Preço por Saco (R$)',
            'pesagem': 'Pesagem do Caminhão (Placa)',
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['pesagem'].queryset = PesagemCaminhao.objects.filter(created_by=user)
        else:
            self.fields['pesagem'].queryset = PesagemCaminhao.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        pesagem = cleaned_data.get('pesagem')
        tipo_grao = cleaned_data.get('tipo_grao')
        if pesagem and tipo_grao and pesagem.tipo_grao != tipo_grao:
            raise forms.ValidationError("O tipo de grão deve corresponder ao tipo de grão da pesagem selecionada.")
        return cleaned_data

    def clean_quantidade_sacos(self):
        quantidade = self.cleaned_data.get('quantidade_sacos')
        if quantidade <= 0:
            raise forms.ValidationError("A quantidade de sacos deve ser maior que zero.")
        return quantidade

    def clean_preco_por_saco(self):
        preco = self.cleaned_data.get('preco_por_saco')
        if preco <= 0:
            raise forms.ValidationError("O preço por saco deve ser maior que zero.")
        return preco

# --- form for step 1: capture of initial data and tare ---


class PesagemTaraForm(forms.ModelForm):
    class Meta:
        model = PesagemCaminhao
        fields = [
            'placa', 'placa_cavalo', 'motorista', 'transportadora',
            'operador', 'tara', 'tipo_grao', 'valor_custo_por_saco'
        ]
        widgets = {
            'placa': forms.TextInput(attrs={'class': 'form-control'}),
            'placa_cavalo': forms.TextInput(attrs={'class': 'form-control'}),
            'motorista': forms.TextInput(attrs={'class': 'form-control'}),
            'transportadora': forms.TextInput(attrs={'class': 'form-control'}),
            'operador': forms.TextInput(attrs={'class': 'form-control'}),
            'tara': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'tipo_grao': forms.Select(attrs={'class': 'form-select'}),
            'valor_custo_por_saco': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
        labels = {
            'placa': 'Placa Carreta/Placa',
            'placa_cavalo': 'Placa Veíc/Cavalo',
            'motorista': 'Nome do Motorista',
            'transportadora': 'Transportadora',
            'operador': 'Operador',
            'tara': 'Peso da Tara (kg)',
            'tipo_grao': 'Tipo de Grão',
            'valor_custo_por_saco': 'Custo por Saco (R$)',
        }

# --- form for step 2: capture only of final loaded weight ---


class PesagemFinalForm(forms.ModelForm):
    class Meta:
        model = PesagemCaminhao
        fields = ['peso_carregado']
        widgets = {
            'peso_carregado': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
        }
        labels = {
            'peso_carregado': 'Peso Carregado (kg)',
        }

    def clean_peso_carregado(self):
        # validation to ensure loaded weight is greater than tare
        peso_carregado = self.cleaned_data.get('peso_carregado')
        tara = self.instance.tara  # accesses the tare of the object being edited
        if peso_carregado is not None and tara is not None:
            if tara >= peso_carregado:
                raise forms.ValidationError("O peso carregado deve ser maior que o peso da tara.")
        return peso_carregado


class AmostraForm(forms.ModelForm):
    class Meta:
        model = Amostra
        fields = ["tipo_grao", "peso_bruto", "umidade", "impurezas"]
        widgets = {
            "tipo_grao": forms.Select(attrs={
                "class": "form-select",
                "id": "id_tipo_grao",
                "required": "required"
            }),
            "peso_bruto": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.001",
                "placeholder": "0.000",
                "required": "required"
            }),
            "umidade": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "placeholder": "0.00"
            }),
            "impurezas": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "placeholder": "0.00"
            }),
        }
