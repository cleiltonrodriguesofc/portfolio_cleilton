from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings


class Amostra(models.Model):
    GRAO_CHOICES = [
        ('SOJA', 'Soja'),
        ('MILHO', 'Milho'),
    ]

    id_amostra = models.CharField(max_length=100, unique=True, blank=True, null=True)
    tipo_grao = models.CharField(max_length=10, choices=GRAO_CHOICES)
    peso_bruto = models.DecimalField(max_digits=10, decimal_places=3)
    umidade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    impurezas = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    peso_util = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    status = models.CharField(max_length=20, default='PENDENTE')  # ACEITA, REJEITADA, PENDENTE
    data_criacao = models.DateTimeField(auto_now_add=True)
    ultima_atualizacao = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='amostras_criadas',
        null=True,
        blank=True)
    last_updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='amostras_atualizadas',
        null=True,
        blank=True)

    def __str__(self):
        return f'Amostra {self.id_amostra} - {self.tipo_grao}'

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and not self.id_amostra:
            self.id_amostra = f"AMS-{self.id:04d}"
            super().save(update_fields=['id_amostra'])


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

    # Fields for tracking the two-step process
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDENTE)
    data_tara = models.DateTimeField(null=True, blank=True, verbose_name="Data da Tara")
    data_final = models.DateTimeField(null=True, blank=True, verbose_name="Data Final")

    # Vehicle and personnel details
    placa = models.CharField(max_length=10, verbose_name="Placa Carreta/Placa")
    placa_cavalo = models.CharField(max_length=10, blank=True, null=True, verbose_name="Placa Veíc/Cavalo")
    motorista = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nome do Motorista")
    transportadora = models.CharField(max_length=255, blank=True, null=True, verbose_name="Transportadora")
    operador = models.CharField(max_length=100, blank=True, null=True, verbose_name="Operador")

    # Weighing and product details
    tara = models.DecimalField(max_digits=10, decimal_places=3, verbose_name="Peso da Tara (kg)")
    # CHANGED: This field must be optional for the first step
    peso_carregado = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        null=True,
        blank=True,
        verbose_name="Peso Carregado (kg)")
    peso_liquido = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    tipo_grao = models.CharField(max_length=10, choices=GRAO_CHOICES)
    quantidade_sacos = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='pesagens_criadas',
        null=True,
        blank=True)
    # Calculate profit based on cost
    valor_custo_por_saco = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        default=0.00,
        verbose_name="Custo por Saco (R$)")
    # CHANGED: The save logic is now safer

    def save(self, *args, **kwargs):
        # Only calculate the net weight if both tara and peso_carregado have values
        if self.tara is not None and self.peso_carregado is not None:
            self.peso_liquido = self.peso_carregado - self.tara
            self.quantidade_sacos = self.peso_liquido / 60
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Pesagem {self.id} - {self.placa} ({self.status})"


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
    represents the complete financial record of a loading note.
    this model does not alter notacarregamento, only relates to it.
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
    valor_pago = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    valor_custo_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Custo Total da Operação")
    lucro = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Lucro da Operação")

    def calcular_valor_restante(self):
        """calculates the remaining amount based on the total note value."""
        return self.nota.valor_total - self.valor_pago

    def atualizar_status(self):
        """sums child payments and updates status and totals."""
        # self.pagamentos refers to the related_name of the pagamento model
        total_pago = sum(p.valor for p in self.pagamentos.all())
        self.valor_pago = total_pago
        # --- new lines for cost and profit calculation ---
        if self.nota.pesagem and self.nota.pesagem.valor_custo_por_saco is not None:
            self.valor_custo_total = self.nota.pesagem.valor_custo_por_saco * self.nota.quantidade_sacos
            self.lucro = self.nota.valor_total - self.valor_custo_total
        # --------------------------------------------------

        if self.valor_pago >= self.nota.valor_total:
            self.status_pagamento = self.StatusPagamento.PAGO
        elif self.valor_pago > 0:
            self.status_pagamento = self.StatusPagamento.PARCIAL
        else:
            self.status_pagamento = self.StatusPagamento.PENDENTE

        self.save()

    def __str__(self):
        return f"Financeiro da Nota #{self.nota.id}"


def comprovante_upload_path(instance, filename):
    """generates a unique file path to avoid duplicate names."""
    # Exemplo de output: uploads/comprovantes/nota_101/pagamento_1_comprovante.pdf
    return f'uploads/comprovantes/nota_{instance.registro_financeiro.nota.id}/pagamento_{instance.id}_{filename}'


class Pagamento(models.Model):
    """registers an individual payment installment."""
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
        # when saving, notify the "parent" (registrofinanceiro) to update.
        self.registro_financeiro.atualizar_status()

    def delete(self, *args, **kwargs):
        registro = self.registro_financeiro
        super().delete(*args, **kwargs)
        # when deleting, also notify the "parent" to update.
        registro.atualizar_status()

    def __str__(self):
        return f"Pagamento de R$ {self.valor} para a Nota #{self.registro_financeiro.nota.id}"
    # --- new optional field for receipt ---
    comprovante = models.FileField(
        upload_to=comprovante_upload_path,
        blank=True,  # Permite que o campo fique em branco no formulário
        null=True,  # Permite que o valor no banco de dados seja NULO
        verbose_name="Comprovante de Pagamento"
    )
