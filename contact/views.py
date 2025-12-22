from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ContactForm


def contact(request):
    """View for the contact form"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Message sent successfully! I will contact you soon.')
            return redirect('contact:contact')
    else:
        form = ContactForm()

    context = {
        'title': 'Contato - Cleilton',
        'description': 'Entre em contato comigo para projetos, oportunidades ou dúvidas.',
        'form': form,
    }
    return render(request, 'contact/contact.html', context)
