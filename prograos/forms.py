from django import forms
from .models import Amostra, PesagemCaminhao, NotaCarregamento, Pagamento, Invoice


class PagamentoForm(forms.ModelForm):
    class Meta:
        model = Pagamento
        fields = ['valor', 'data_pagamento', 'metodo_pagamento', 'observacoes', 'comprovante']
        widgets = {
            'valor': forms.TextInput(attrs={'class': 'form-control money-mask'}),

            # --- CORREÇÃO APLICADA AQUI ---
            'data_pagamento': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'  # <-- FORMATO ADICIONADO
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
        localized_fields = ('valor',)


class NotaCarregamentoForm(forms.ModelForm):
    class Meta:
        model = NotaCarregamento
        fields = [
            'nome_recebedor', 'cpf_cnpj_recebedor', 'telefone_recebedor',
            'endereco_recebedor', 'tipo_grao', 'quantidade_sacos', 'preco_por_saco', 'pesagem'
        ]
        widgets = {
            'nome_recebedor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do recebedor'}),
            'cpf_cnpj_recebedor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '000.000.000-00 ou 00.000.000/0000-00'}),
            'telefone_recebedor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(00) 00000-0000'}),
            'endereco_recebedor': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Endereço completo'}),
            'tipo_grao': forms.Select(attrs={'class': 'form-select'}, choices=NotaCarregamento.GRAO_CHOICES),
            # 0 dec
            'quantidade_sacos': forms.TextInput(attrs={'class': 'form-control integer-mask', 'placeholder': '1000'}),
            'preco_por_saco': forms.TextInput(attrs={'class': 'form-control money-mask', 'placeholder': '0,00'}),
            'pesagem': forms.Select(attrs={'class': 'form-select'}),
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
        localized_fields = ('quantidade_sacos', 'preco_por_saco')

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

# --- Formulário para a Etapa 1: Captura dos dados iniciais e da tara ---


class PesagemTaraForm(forms.ModelForm):
    class Meta:
        model = PesagemCaminhao
        fields = [
            'placa', 'placa_cavalo', 'motorista', 'transportadora',
            'operador', 'tara', 'tipo_grao', 'valor_custo_por_saco',
            # Novo campo valor frete
            'valor_frete_por_tonelada'
        ]
        widgets = {
            'placa': forms.TextInput(attrs={'class': 'form-control'}),
            'placa_cavalo': forms.TextInput(attrs={'class': 'form-control'}),
            'motorista': forms.TextInput(attrs={'class': 'form-control'}),
            'transportadora': forms.TextInput(attrs={'class': 'form-control'}),
            'operador': forms.TextInput(attrs={'class': 'form-control'}),
            'tara': forms.TextInput(attrs={'class': 'form-control weight-2-mask', 'placeholder': '0,00'}),
            'tipo_grao': forms.Select(attrs={'class': 'form-select'}),
            'valor_custo_por_saco': forms.TextInput(attrs={'class': 'form-control money-mask', 'placeholder': '0,00'}),
            # Novo campo valor frete
            'valor_frete_por_tonelada': forms.TextInput(attrs={'class': 'form-control money-mask', 'placeholder': '0,00'}),
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
            # Valor frete
            'valor_frete_por_tonelada': 'Valor Frete (R$/Ton)',
        }
        localized_fields = ('tara', 'valor_custo_por_saco', 'valor_frete_por_tonelada')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Clear default 0.00 values to show placeholders
        for field in ['valor_custo_por_saco', 'valor_frete_por_tonelada']:
            if self.initial.get(field) == 0:
                self.initial[field] = None

# --- Formulário para a Etapa 2: Captura apenas do peso final carregado ---


class PesagemFinalForm(forms.ModelForm):
    class Meta:
        model = PesagemCaminhao
        fields = ['peso_carregado']
        widgets = {
            'peso_carregado': forms.TextInput(attrs={'class': 'form-control weight-2-mask', 'placeholder': '0,00'}),
        }
        localized_fields = ('peso_carregado',)
        labels = {
            'peso_carregado': 'Peso Carregado (kg)',
        }

    def clean_peso_carregado(self):
        # Validação para garantir que o peso carregado é maior que a tara
        peso_carregado = self.cleaned_data.get('peso_carregado')
        tara = self.instance.tara  # Acessa a tara do objeto que está sendo editado
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
                "step": "0.01",
                "placeholder": "0.00",
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


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['customer_name', 'customer_document', 'weighing_record', 'total_amount', 'issue_date']
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'customer_document': forms.TextInput(attrs={'class': 'form-control'}),
            'weighing_record': forms.Select(attrs={'class': 'form-select'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'issue_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['weighing_record'].queryset = PesagemCaminhao.objects.filter(created_by=user)
        else:
            self.fields['weighing_record'].queryset = PesagemCaminhao.objects.none()


class CalculadoraFreteForm(forms.Form):
    """
    Formulário para a ferramenta de calculadora de frete.
    Não está ligado a nenhum modelo.
    """
    UNIDADE_CHOICES = [
        ('sacos', 'Sacos'),
        ('toneladas', 'Toneladas'),
    ]

    # Entrada 1: Custo do grão por saco (ex: 60)
    custo_grao_por_saco = forms.DecimalField(
        label="Custo do Grão (R$ por Saco)",
        decimal_places=2,
        localize=True,
        widget=forms.TextInput(attrs={'class': 'form-control money-mask', 'placeholder': '60,00'})
    )

    # Entrada 2: Preço de venda base (ex: 62)
    preco_base_venda_por_saco = forms.DecimalField(
        label="Preço de Venda Base (R$ por Saco)",
        help_text="O preço que você venderia *sem* o custo do frete.",
        decimal_places=2,
        localize=True,
        widget=forms.TextInput(attrs={'class': 'form-control money-mask', 'placeholder': '62,00'})
    )

    # Entrada 3: Frete por tonelada (ex: 140)
    frete_por_tonelada = forms.DecimalField(
        label="Custo do Frete (R$ por Tonelada)",
        decimal_places=2,
        localize=True,
        widget=forms.TextInput(attrs={'class': 'form-control money-mask', 'placeholder': '140,00'})
    )

    # Entrada 4: Quantidade
    quantidade = forms.DecimalField(
        label="Quantidade da Carga",
        decimal_places=0,
        localize=True,
        widget=forms.TextInput(attrs={'class': 'form-control integer-mask', 'placeholder': '1000'})
    )

    # Entrada 5: Unidade da Quantidade
    unidade_quantidade = forms.ChoiceField(
        label="Unidade da Quantidade",
        choices=UNIDADE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def clean(self):
        cleaned_data = super().clean()

        custo = cleaned_data.get('custo_grao_por_saco')
        preco_base = cleaned_data.get('preco_base_venda_por_saco')

        if custo and preco_base and preco_base < custo:
            raise forms.ValidationError(
                "O Preço de Venda Base (R$ %(preco)s) não pode ser menor que o Custo do Grão (R$ %(custo)s).",
                code='preco_menor_que_custo',
                params={'preco': preco_base, 'custo': custo}
            )
        return cleaned_data
