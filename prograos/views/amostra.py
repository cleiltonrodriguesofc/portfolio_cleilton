from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from prograos.models import Amostra
from prograos.forms import AmostraForm
from prograos.utils import GrainCalculator


class AmostraListView(LoginRequiredMixin, ListView):
    model = Amostra
    template_name = 'prograos/amostra_list.html'
    context_object_name = 'amostras'
    paginate_by = 20

    def get_queryset(self):
        return Amostra.objects.filter(created_by=self.request.user).order_by('-data_criacao')


class AmostraDetailView(LoginRequiredMixin, DetailView):
    model = Amostra
    template_name = 'prograos/amostra_detail.html'
    context_object_name = 'amostra'

    def get_queryset(self):
        return Amostra.objects.filter(created_by=self.request.user)


class AmostraCreateView(LoginRequiredMixin, CreateView):
    model = Amostra
    form_class = AmostraForm
    template_name = 'prograos/amostra_form.html'
    success_url = reverse_lazy('prograos:dashboard')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        amostra = form.save(commit=False)
        calculos = GrainCalculator.aplicar_calculos(amostra)
        amostra.peso_util = calculos.get('peso_util')
        amostra.status = calculos.get('status')
        amostra.save()
        messages.success(self.request, f"Amostra #{amostra.id} criada com sucesso!")
        return redirect(self.success_url)


class AmostraUpdateView(LoginRequiredMixin, UpdateView):
    model = Amostra
    form_class = AmostraForm
    template_name = 'prograos/amostra_form.html'
    success_url = reverse_lazy('prograos:dashboard')

    def get_queryset(self):
        return Amostra.objects.filter(created_by=self.request.user)

    def form_valid(self, form):
        form.instance.last_updated_by = self.request.user
        amostra = form.save(commit=False)
        calculos = GrainCalculator.aplicar_calculos(amostra)
        amostra.peso_util = calculos.get('peso_util')
        amostra.status = calculos.get('status')
        amostra.save()
        messages.success(self.request, f"Amostra #{amostra.id} atualizada com sucesso!")
        return redirect(self.success_url)


class AmostraDeleteView(LoginRequiredMixin, DeleteView):
    model = Amostra
    template_name = 'prograos/amostra_confirm_delete.html'
    success_url = reverse_lazy('prograos:dashboard')

    def get_queryset(self):
        return Amostra.objects.filter(created_by=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, f"Amostra #{self.get_object().id} deletada com sucesso!")
        return super().form_valid(form)
