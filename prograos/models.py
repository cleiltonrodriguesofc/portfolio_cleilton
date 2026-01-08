from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
from decimal import Decimal
from django.db.models import Sum
from django.db.models.functions import Coalesce


class Amostra(models.Model):
    GRAO_CHOICES = [
        ('SOJA', 'Soja'),
        ('MILHO', 'Milho'),
    ]

    id_amostra = models.CharField(max_length=100, unique=True, blank=True, null=True)
    tipo_grao = models.CharField(max_length=10, choices=GRAO_CHOICES)
    peso_bruto = models.DecimalField(max_digits=10, decimal_places=2)
    umidade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    impurezas = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    peso_util = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, default='PENDENTE')  # ACEITA, REJEITADA, PENDENTE
    data_criacao = models.DateTimeField(auto_now_add=True)
    ultima_atualizacao = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL,
                                   related_name='amostras_criadas', null=True, blank=True)
    last_updated_by = models.ForeignKey(User, on_delete=models.SET_NULL,
                                        related_name='amostras_atualizadas', null=True, blank=True)

    def __str__(self):
        return f'{self.id_amostra} - {self.tipo_grao}'


class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    object_id = models.CharField(max_length=255, null=True, blank=True)
    object_type = models.CharField(max_length=255, null=True, blank=True)
    details = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'{self.user} - {self.action} at {self.timestamp}'


class PesagemCaminhao(models.Model):
    GRAO_CHOICES = [
        ('SOJA', 'Soja'),
        ('MILHO', 'Milho'),
    ]

    class Status(models.TextChoices):
        PENDENTE = 'PENDENTE', 'Pendente'
        CONCLUIDO = 'CONCLUIDO', 'Concluído'

    # --- Controle de processo ---
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDENTE)
    data_tara = models.DateTimeField(null=True, blank=True, verbose_name="Data da Tara")
    data_final = models.DateTimeField(null=True, blank=True, verbose_name="Data Final")

    # --- Dados do veículo e operador ---
    placa = models.CharField(max_length=10, verbose_name="Placa Carreta/Placa")
    placa_cavalo = models.CharField(max_length=10, blank=True, null=True, verbose_name="Placa Veíc/Cavalo")
    motorista = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nome do Motorista")
    transportadora = models.CharField(max_length=255, blank=True, null=True, verbose_name="Transportadora")
    operador = models.CharField(max_length=100, blank=True, null=True, verbose_name="Operador")

    # --- Pesos e produto ---
    tara = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Peso da Tara (kg)")
    peso_carregado = models.DecimalField(max_digits=10, decimal_places=2, null=True,
                                         blank=True, verbose_name="Peso Carregado (kg)")
    peso_liquido = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tipo_grao = models.CharField(max_length=10, choices=GRAO_CHOICES)
    quantidade_sacos = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)

    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name='pesagens_criadas', null=True, blank=True
    )

    # --- Custo base ---
    valor_custo_por_saco = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        default=Decimal('0.00'),
        verbose_name="Custo por Saco (R$)"
    )

    # --- Campos de frete ---
    valor_frete_por_tonelada = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        default=Decimal('0.00'),
        verbose_name="Valor Frete (R$/Ton)"
    )
    frete_total_calculado = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    frete_por_saco_calculado = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def save(self, *args, **kwargs):
        # 1) Cálculo de peso líquido
        if self.tara is not None and self.peso_carregado is not None:
            self.peso_liquido = self.peso_carregado - self.tara
            self.quantidade_sacos = (self.peso_liquido / Decimal('60')) if self.peso_liquido is not None else None
        else:
            self.peso_liquido = None
            self.quantidade_sacos = None

        # 2) Cálculo de frete (somente se preenchido)
        frete_preenchido = (
            self.valor_frete_por_tonelada is not None
            and self.valor_frete_por_tonelada > Decimal('0')
        )

        if frete_preenchido and self.peso_liquido is not None:
            peso_toneladas = self.peso_liquido / Decimal('1000')
            self.frete_total_calculado = (peso_toneladas * self.valor_frete_por_tonelada).quantize(Decimal('0.01'))
            if self.quantidade_sacos and self.quantidade_sacos > 0:
                self.frete_por_saco_calculado = (self.frete_total_calculado /
                                                 self.quantidade_sacos).quantize(Decimal('0.01'))
            else:
                self.frete_por_saco_calculado = None
        else:
            self.frete_total_calculado = None
            self.frete_por_saco_calculado = None

        super().save(*args, **kwargs)

        # 3) Atualiza financeiro vinculado
        try:
            for nota in self.notacarregamento_set.all():
                if getattr(nota, 'financeiro', None):
                    nota.financeiro.atualizar_status()
        except Exception:
            pass

    def __str__(self):
        return f"Placa: {self.placa} (ID: {self.id})"


class NotaCarregamento(models.Model):
    GRAO_CHOICES = [
        ("SOJA", "Soja"),
        ("MILHO", "Milho"),
    ]
    nome_recebedor = models.CharField(max_length=255)
    cpf_cnpj_recebedor = models.CharField(max_length=20, blank=True, null=True)
    telefone_recebedor = models.CharField(max_length=20, blank=True, null=True)
    endereco_recebedor = models.TextField(blank=True, null=True)
    tipo_grao = models.CharField(max_length=10, choices=GRAO_CHOICES)
    quantidade_sacos = models.DecimalField(max_digits=10, decimal_places=3)
    preco_por_saco = models.DecimalField(max_digits=10, decimal_places=2)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='notas_criadas', null=True, blank=True)
    pesagem = models.ForeignKey('PesagemCaminhao', on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.valor_total = self.quantidade_sacos * self.preco_por_saco
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Nota {self.id} - {self.nome_recebedor}"


class RegistroFinanceiro(models.Model):
    """
    Representa o registro financeiro completo de uma Nota de Carregamento.
    Este model NÃO altera o NotaCarregamento, apenas se relaciona com ele.
    """
    class StatusPagamento(models.TextChoices):
        PENDENTE = 'PENDENTE', 'Pendente'
        PARCIAL = 'PARCIAL', 'Parcial'
        PAGO = 'PAGO', 'Pago'

    # Relação de um-para-um: Cada Nota tem apenas um RegistroFinanceiro.
    nota = models.OneToOneField(
        NotaCarregamento,
        on_delete=models.CASCADE,
        related_name='financeiro'
    )

    status_pagamento = models.CharField(
        max_length=10,
        choices=StatusPagamento.choices,
        default=StatusPagamento.PENDENTE
    )

    valor_pago = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    valor_custo_total = models.DecimalField(max_digits=10, decimal_places=2,
                                            null=True, blank=True, verbose_name="Custo Total da Operação")
    lucro = models.DecimalField(max_digits=10, decimal_places=2, null=True,
                                blank=True, verbose_name="Lucro da Operação")

    def calcular_valor_restante(self):
        """Calcula o valor restante com base no valor total da nota."""
        return self.nota.valor_total - self.valor_pago

    def atualizar_status(self):
        """Soma os pagamentos filhos e atualiza o status e os totais."""

        total_pago = self.pagamentos.aggregate(
            total=Coalesce(Sum('valor'), Decimal('0.00'))
        )['total']
        self.valor_pago = total_pago

        # ✅ Sempre inicia em Decimal
        custo_base_grao = Decimal('0.00')
        custo_frete = Decimal('0.00')

        # 2. Busca os custos na Pesagem (via Nota)
        if self.nota.pesagem:
            pesagem = self.nota.pesagem

            # Custo base (Grão)
            if pesagem.valor_custo_por_saco is not None:
                custo_base_grao = pesagem.valor_custo_por_saco * self.nota.quantidade_sacos

            # Custo do Frete (lendo direto da pesagem)
            if pesagem.frete_total_calculado is not None:
                custo_frete = pesagem.frete_total_calculado

        # 3. Cálculo Final
        self.valor_custo_total = custo_base_grao + custo_frete
        self.lucro = self.nota.valor_total - self.valor_custo_total
        # --------------------------------------------------

        if self.valor_pago >= self.nota.valor_total:
            self.status_pagamento = self.StatusPagamento.PAGO
        elif self.valor_pago > Decimal('0.00'):
            self.status_pagamento = self.StatusPagamento.PARCIAL
        else:
            self.status_pagamento = self.StatusPagamento.PENDENTE

        self.save()

    def __str__(self):
        return f"Financeiro da Nota #{self.nota.id}"


def comprovante_upload_path(instance, filename):
    """Gera um caminho único para o arquivo para evitar nomes duplicados."""
    # Exemplo de output: uploads/comprovantes/nota_101/pagamento_1_comprovante.pdf
    return f'uploads/comprovantes/nota_{instance.registro_financeiro.nota.id}/pagamento_{instance.id}_{filename}'


class Pagamento(models.Model):
    """Registra uma parcela de pagamento individual."""
    class MetodoPagamento(models.TextChoices):
        PIX = 'PIX', 'Pix'
        BOLETO = 'BOLETO', 'Boleto'
        DINHEIRO = 'DINHEIRO', 'Dinheiro'

    # Relação: Um pagamento pertence a um RegistroFinanceiro.
    registro_financeiro = models.ForeignKey(
        RegistroFinanceiro,
        on_delete=models.CASCADE,
        related_name='pagamentos'
    )

    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data_pagamento = models.DateTimeField(default=timezone.now)
    metodo_pagamento = models.CharField(
        max_length=10,
        choices=MetodoPagamento.choices,
        default=MetodoPagamento.PIX  # <-- VALOR PADRÃO
    )
    observacoes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Ao salvar, avisa o "pai" (RegistroFinanceiro) para se atualizar.
        self.registro_financeiro.atualizar_status()

    def delete(self, *args, **kwargs):
        registro = self.registro_financeiro
        super().delete(*args, **kwargs)
        # Ao deletar, também avisa o "pai" para se atualizar.
        registro.atualizar_status()

    def __str__(self):
        return f"Pagamento de R$ {self.valor} para a Nota #{self.registro_financeiro.nota.id}"
    # --- NOVO CAMPO OPCIONAL PARA COMPROVANTE ---
    comprovante = models.FileField(
        upload_to=comprovante_upload_path,
        blank=True,  # Permite que o campo fique em branco no formulário
        null=True,  # Permite que o valor no banco de dados seja NULO
        verbose_name="Comprovante de Pagamento"
    )


class Invoice(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Rascunho'
        READY = 'READY', 'Pronto para Emissão'
        ISSUED = 'ISSUED', 'Emitida'
        CANCELLED = 'CANCELLED', 'Cancelada'

    number = models.CharField(max_length=20, unique=True, verbose_name="Número Interno")
    customer_name = models.CharField(max_length=255, verbose_name="Nome do Cliente")
    customer_document = models.CharField(max_length=20, verbose_name="CPF/CNPJ")
    weighing_record = models.ForeignKey('PesagemCaminhao', on_delete=models.PROTECT,
                                        verbose_name="Pesagem Vinculada", null=True, blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Valor Total")
    issue_date = models.DateTimeField(default=timezone.now, verbose_name="Data de Emissão")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, verbose_name="Status")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Invoice #{self.number} - {self.customer_name}"


class NFe(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pendente'
        AUTHORIZED = 'AUTHORIZED', 'Autorizada'
        DENIED = 'DENIED', 'Denegada'
        CANCELLED = 'CANCELLED', 'Cancelada'

    class Environment(models.TextChoices):
        HOMOLOGATION = 'HOMOLOGATION', 'Homologação'
        PRODUCTION = 'PRODUCTION', 'Produção'

    invoice = models.OneToOneField(Invoice, on_delete=models.CASCADE, related_name='nfe')
    access_key = models.CharField(max_length=44, blank=True, null=True, verbose_name="Chave de Acesso")
    series = models.IntegerField(default=1, verbose_name="Série")
    number = models.IntegerField(verbose_name="Número NF-e")
    xml = models.TextField(blank=True, null=True, verbose_name="XML Autorizado")
    protocol = models.CharField(max_length=100, blank=True, null=True, verbose_name="Protocolo de Autorização")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    environment = models.CharField(max_length=20, choices=Environment.choices, default=Environment.HOMOLOGATION)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"NF-e {self.number} - {self.status}"


class NFeItem(models.Model):
    nfe = models.ForeignKey(NFe, on_delete=models.CASCADE, related_name='items')
    product_name = models.CharField(max_length=255, verbose_name="Produto")
    ncm = models.CharField(max_length=8, verbose_name="NCM")
    cfop = models.CharField(max_length=4, verbose_name="CFOP")
    quantity = models.DecimalField(max_digits=12, decimal_places=4, verbose_name="Quantidade")
    unit_price = models.DecimalField(max_digits=12, decimal_places=4, verbose_name="Valor Unitário")
    total_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Valor Total")

    def __str__(self):
        return f"{self.product_name} ({self.quantity})"
# ==============================================================================
# NF-e PRODUCTION MODELS - Fiscal Configuration
# ==============================================================================


class EmitterConfig(models.Model):
    """
    Singleton model for company fiscal configuration.
    Only one instance should exist in the database.
    """
    # Company identification
    razao_social = models.CharField(max_length=255, verbose_name="Razão Social")
    nome_fantasia = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nome Fantasia")
    cnpj = models.CharField(max_length=14, verbose_name="CNPJ")
    ie = models.CharField(max_length=20, verbose_name="Inscrição Estadual")
    im = models.CharField(max_length=20, blank=True, null=True, verbose_name="Inscrição Municipal")
    regime_tributario = models.CharField(
        max_length=1,
        choices=[('1', 'Simples Nacional'), ('2', 'Simples Exc. Receita'), ('3', 'Regime Normal')],
        default='1',
        verbose_name="Regime Tributário"
    )

    # Address
    logradouro = models.CharField(max_length=255, verbose_name="Logradouro")
    numero = models.CharField(max_length=10, verbose_name="Número")
    complemento = models.CharField(max_length=100, blank=True, null=True, verbose_name="Complemento")
    bairro = models.CharField(max_length=100, verbose_name="Bairro")
    cep = models.CharField(max_length=8, verbose_name="CEP")
    municipio = models.CharField(max_length=100, verbose_name="Município")
    c_mun = models.CharField(max_length=7, verbose_name="Código IBGE Município")
    uf = models.CharField(max_length=2, verbose_name="UF")

    # NF-e configuration
    serie_nfe = models.IntegerField(default=1, verbose_name="Série NF-e")
    numero_atual_nfe = models.IntegerField(default=1, verbose_name="Próximo Número NF-e")
    ambiente = models.IntegerField(
        choices=[(2, 'Homologação'), (1, 'Produção')],
        default=2,
        verbose_name="Ambiente"
    )

    # Security
    production_enabled = models.BooleanField(
        default=False,
        verbose_name="Produção Habilitada",
        help_text="ATENÇÃO: Habilite apenas após validação do contador"
    )
    accountant_validated_at = models.DateTimeField(blank=True, null=True, verbose_name="Validado pelo Contador em")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Configuração do Emitente"
        verbose_name_plural = "Configuração do Emitente"

    def save(self, *args, **kwargs):
        # Enforce singleton
        if not self.pk and EmitterConfig.objects.exists():
            raise Exception("Apenas uma configuração de emitente é permitida")
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.razao_social} - {self.cnpj}"

    def get_next_nfe_number(self):
        """Get and increment NF-e number atomically"""
        self.numero_atual_nfe += 1
        self.save(update_fields=['numero_atual_nfe'])
        return self.numero_atual_nfe - 1


class CertificateConfig(models.Model):
    """
    A1 Digital Certificate configuration
    """
    name = models.CharField(max_length=100, verbose_name="Nome do Certificado")
    certificate_file = models.FileField(
        upload_to='certificates/',
        verbose_name="Arquivo do Certificado (.pfx)",
        help_text="Upload do arquivo .pfx do certificado A1"
    )
    password = models.CharField(
        max_length=255,
        verbose_name="Senha do Certificado",
        help_text="Senha será criptografada no banco de dados"
    )
    valid_from = models.DateField(verbose_name="Válido de")
    valid_to = models.DateField(verbose_name="Válido até")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Certificado Digital"
        verbose_name_plural = "Certificados Digitais"
        ordering = ['-is_active', '-created_at']

    def __str__(self):
        return f"{self.name} (válido até {self.valid_to})"

    def is_valid(self):
        from django.utils import timezone
        today = timezone.now().date()
        return self.is_active and self.valid_from <= today <= self.valid_to


class TaxProfile(models.Model):
    """
    Tax configuration profile for products (grain types)
    """
    GRAO_CHOICES = [
        ('SOJA', 'Soja'),
        ('MILHO', 'Milho'),
    ]

    CFOP_CHOICES = [
        ('5101', '5101 - Venda de produção do estabelecimento'),
        ('5102', '5102 - Venda de mercadoria adquirida'),
        ('6101', '6101 - Venda de produção - fora do estado'),
        ('6102', '6102 - Venda de mercadoria - fora do estado'),
    ]

    # Product identification
    grain_type = models.CharField(
        max_length=10,
        choices=GRAO_CHOICES,
        unique=True,
        verbose_name="Tipo de Grão"
    )
    description = models.CharField(max_length=255, verbose_name="Descrição do Produto")

    # Tax codes
    ncm = models.CharField(
        max_length=8,
        verbose_name="NCM",
        help_text="Ex: 12019000 para Soja, 10059000 para Milho"
    )
    cfop_inside_state = models.CharField(
        max_length=4,
        choices=CFOP_CHOICES,
        default='5101',
        verbose_name="CFOP - Dentro do Estado"
    )
    cfop_outside_state = models.CharField(
        max_length=4,
        choices=CFOP_CHOICES,
        default='6101',
        verbose_name="CFOP - Fora do Estado"
    )

    # ICMS configuration
    cst_csosn = models.CharField(
        max_length=3,
        default='101',
        verbose_name="CST/CSOSN",
        help_text="Ex: 101 para Simples Nacional com crédito"
    )
    icms_aliquota = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="Alíquota ICMS (%)"
    )

    # PIS/COFINS
    pis_aliquota = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="Alíquota PIS (%)"
    )
    cofins_aliquota = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="Alíquota COFINS (%)"
    )

    # Unit
    unit_com = models.CharField(
        max_length=10,
        default='KG',
        verbose_name="Unidade Comercial",
        help_text="Ex: KG, TON, SC (saco)"
    )

    # Validation
    accountant_validated = models.BooleanField(
        default=False,
        verbose_name="Validado pelo Contador"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observações",
        help_text="Notas do contador sobre esta configuração"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Perfil Tributário"
        verbose_name_plural = "Perfis Tributários"

    def __str__(self):
        status = "✓" if self.accountant_validated else "⚠"
        return f"{status} {self.get_grain_type_display()} - NCM {self.ncm}"


class NFeEvent(models.Model):
    """
    NF-e events (cancelamento, CCe, inutilização)
    """
    EVENT_TYPES = [
        ('CANCELAMENTO', 'Cancelamento'),
        ('CCE', 'Carta de Correção Eletrônica'),
        ('INUTILIZACAO', 'Inutilização'),
    ]

    nfe = models.ForeignKey(
        NFe,
        on_delete=models.CASCADE,
        related_name='events',
        verbose_name="NF-e"
    )
    event_type = models.CharField(
        max_length=20,
        choices=EVENT_TYPES,
        verbose_name="Tipo de Evento"
    )
    description = models.TextField(verbose_name="Descrição/Justificativa")
    xml_event = models.TextField(blank=True, null=True, verbose_name="XML do Evento")
    protocol = models.CharField(max_length=100, blank=True, null=True, verbose_name="Protocolo")
    status = models.CharField(
        max_length=20,
        choices=[('PENDING', 'Pendente'), ('SUCCESS', 'Sucesso'), ('ERROR', 'Erro')],
        default='PENDING',
        verbose_name="Status"
    )
    error_message = models.TextField(blank=True, null=True, verbose_name="Mensagem de Erro")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Evento NF-e"
        verbose_name_plural = "Eventos NF-e"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_event_type_display()} - NF-e {self.nfe.number} - {self.status}"
