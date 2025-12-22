from django.db import models


class Contact(models.Model):
    """model to store contact messages"""

    name = models.CharField(max_length=100, verbose_name="Nome")
    email = models.EmailField(verbose_name="Email")
    subject = models.CharField(max_length=200, verbose_name="Assunto", blank=True)
    message = models.TextField(verbose_name="Mensagem")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Enviado em")
    is_read = models.BooleanField(default=False, verbose_name="Lida")

    class Meta:
        verbose_name = "Mensagem de Contato"
        verbose_name_plural = "Mensagens de Contato"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject or 'Sem assunto'}"
