from django.shortcuts import render

def project_list(request):
    return render(request, 'core/project_list.html') 

def home(request):
    """View da página inicial do portfólio"""
    context = {
        'title': 'Cleilton - Desenvolvedor Full-Stack',
        'description': 'Portfólio profissional de Cleilton, desenvolvedor apaixonado por tecnologia e investimentos.',
    }
    return render(request, 'core/home.html', context)

def about(request):
    """View da página sobre"""
    context = {
        'title': 'Sobre - Cleilton',
        'description': 'Conheça mais sobre minha trajetória profissional e experiências.',
    }
    return render(request, 'core/about.html', context)
