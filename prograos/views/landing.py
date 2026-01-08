from django.shortcuts import render, redirect
from django.views.generic import View


class LandingPageView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('prograos:dashboard')
        return render(request, 'landing_page.html')
