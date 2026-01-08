from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from prograos.models import ActivityLog
from prograos.services.auth_service import AuthService


def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            AuthService.register_user(form)
            messages.success(request, 'Sua conta foi criada! Aguarde a aprovação do administrador para fazer login.')
            return redirect('prograos:login')
    else:
        form = UserCreationForm()
    return render(request, 'prograos/registration/register.html', {'form': form})


class CustomLoginView(LoginView):
    template_name = 'prograos/registration/login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        response = super().form_valid(form)
        ActivityLog.objects.create(
            user=self.request.user,
            action="Login",
            details=f"User {self.request.user.username} logged in."
        )
        messages.success(self.request, f"Welcome, {self.request.user.username}!")
        return response
