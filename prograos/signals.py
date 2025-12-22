from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import NotaCarregamento, RegistroFinanceiro


@receiver(post_save, sender=NotaCarregamento)
def criar_registro_financeiro_para_nota(sender, instance, created, **kwargs):
    """
    Cria um RegistroFinanceiro automaticamente quando uma nova NotaCarregamento é criada.
    """
    if created:
        RegistroFinanceiro.objects.create(nota=instance)
