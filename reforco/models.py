from django.db import models
from django.utils import timezone

class Aluno(models.Model):
    """
    Modelo para armazenar informações dos alunos.
    """
    ATIVO = 'A'
    INATIVO = 'I'
    STATUS_CHOICES = [
        (ATIVO, 'Ativo'),
        (INATIVO, 'Inativo'),
    ]
    
    nome = models.CharField(max_length=100, verbose_name='Nome')
    telefone = models.CharField(max_length=20, verbose_name='Telefone/WhatsApp')
    nome_responsavel = models.CharField(max_length=100, blank=True, null=True, verbose_name='Nome do Responsável')
    data_nascimento = models.DateField(blank=True, null=True, verbose_name='Data de Nascimento')
    data_entrada = models.DateField(default=timezone.now, verbose_name='Data de Entrada no Reforço')
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=ATIVO, verbose_name='Status')
    observacoes = models.TextField(blank=True, null=True, verbose_name='Observações')
    data_cadastro = models.DateTimeField(default=timezone.now, verbose_name='Data de Cadastro')
    
    class Meta:
        verbose_name = 'Aluno'
        verbose_name_plural = 'Alunos'
        ordering = ['nome']
    
    def __str__(self):
        return self.nome
    
    def get_status_display_badge(self):
        """
        Retorna uma classe CSS para exibir o status como um badge.
        """
        if self.status == self.ATIVO:
            return 'badge bg-success'
        return 'badge bg-danger'
    
    def is_aniversariante_mes(self):
        """
        Verifica se o aluno faz aniversário no mês atual.
        """
        if not self.data_nascimento:
            return False
        return self.data_nascimento.month == timezone.now().month


class Presenca(models.Model):
    """
    Modelo para registrar a presença dos alunos.
    """
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='presencas', verbose_name='Aluno')
    data = models.DateField(default=timezone.now, verbose_name='Data')
    presente = models.BooleanField(default=True, verbose_name='Presente')
    
    class Meta:
        verbose_name = 'Presença'
        verbose_name_plural = 'Presenças'
        ordering = ['-data', 'aluno__nome']
        unique_together = ['aluno', 'data']  # Um aluno só pode ter uma presença por dia
    
    def __str__(self):
        status = 'Presente' if self.presente else 'Ausente'
        return f'{self.aluno.nome} - {self.data.strftime("%d/%m/%Y")} - {status}'


class Pagamento(models.Model):
    """
    Modelo para registrar os pagamentos dos alunos.
    """
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='pagamentos', verbose_name='Aluno')
    mes_referencia = models.DateField(verbose_name='Mês de Referência')
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Valor')
    pago = models.BooleanField(default=False, verbose_name='Pago')
    data_pagamento = models.DateField(blank=True, null=True, verbose_name='Data do Pagamento')
    observacao = models.TextField(blank=True, null=True, verbose_name='Observação')
    
    class Meta:
        verbose_name = 'Pagamento'
        verbose_name_plural = 'Pagamentos'
        ordering = ['-mes_referencia', 'aluno__nome']
        unique_together = ['aluno', 'mes_referencia']  # Um aluno só pode ter um pagamento por mês
    
    def __str__(self):
        status = 'Pago' if self.pago else 'Pendente'
        return f'{self.aluno.nome} - {self.mes_referencia.strftime("%m/%Y")} - {status}'
    
    def get_status_display_badge(self):
        """
        Retorna uma classe CSS para exibir o status como um badge.
        """
        if self.pago:
            return 'badge bg-success'
        return 'badge bg-danger'


