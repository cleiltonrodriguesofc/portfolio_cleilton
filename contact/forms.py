from django import forms
from .models import Contact

class ContactForm(forms.ModelForm):
    """Contact form"""
    
    class Meta:
        model = Contact
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Seu nome'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Seu email'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Assunto (opcional)'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Sua mensagem',
                'rows': 5
            }),
        }

