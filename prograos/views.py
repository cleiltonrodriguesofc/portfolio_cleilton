from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
import json

from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.functions import TruncMonth
from django.db.models import Sum, Count, F, ExpressionWrapper, DecimalField

from .models import (
    Amostra, ActivityLog, PesagemCaminhao,
    NotaCarregamento, RegistroFinanceiro, Pagamento
)
from .forms import (
    AmostraForm, PesagemTaraForm, PesagemFinalForm,
    NotaCarregamentoForm, PagamentoForm
)
from .utils import GrainCalculator
from .reports import ReportGenerator
from .utils_demo import get_actor


# ------------------------------------------------------------------------------
# Simple Mixin to resolve the "actor" (user of the query)
# ------------------------------------------------------------------------------
class ActorMixin:
    def actor(self):
        return get_actor(self.request)


# ==============================================================================
# AUTHENTICATION AND DASHBOARD
# ==============================================================================

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
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


class DashboardView(ActorMixin, ListView):
    model = Amostra
    template_name = "prograos/dashboard.html"
    context_object_name = 'dashboard'
    paginate_by = 10

    def get_queryset(self):
        user = self.actor()
        return Amostra.objects.filter(created_by=user).order_by('-data_criacao')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.actor()

        context["total_amostras"] = Amostra.objects.filter(created_by=user).count()
        context["amostras_aceitas"] = Amostra.objects.filter(created_by=user, status="ACEITA").count()
        context["amostras_rejeitadas"] = Amostra.objects.filter(created_by=user, status="REJEITADA").count()
        context["ultimas_pesagens"] = PesagemCaminhao.objects.filter(created_by=user).order_by("-data_final")[:5]
        context["ultimas_notas"] = NotaCarregamento.objects.filter(created_by=user).order_by("-data_criacao")[:5]
        context["ultimos_registros_financeiros"] = (
            RegistroFinanceiro.objects
            .filter(nota__created_by=user)
            .order_by('-nota__data_criacao')[:5]
        )

        receita_expr = ExpressionWrapper(
            F('quantidade_sacos') * F('preco_por_saco'),
            output_field=DecimalField(max_digits=18, decimal_places=2),
        )

        notas_agg = (
            NotaCarregamento.objects
            .filter(created_by=user)
            .annotate(m=TruncMonth('data_criacao'))
            .values('m')
            .annotate(receita=Sum(receita_expr))
            .order_by('m')
        )

        custos_agg = (
            RegistroFinanceiro.objects
            .filter(nota__created_by=user)
            .annotate(m=TruncMonth('nota__data_criacao'))
            .values('m')
            .annotate(custo=Sum('valor_custo_total'))
            .order_by('m')
        )

        receita_by_month = {row['m']: float(row['receita'] or 0) for row in notas_agg}
        custo_by_month = {row['m']: float(row['custo'] or 0) for row in custos_agg}
        all_months = sorted(set(list(receita_by_month.keys()) + list(custo_by_month.keys())))

        def label_pt(dt):
            meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
            return f"{meses[dt.month - 1]}/{str(dt.year)[-2:]}"

        monthly_labels = [label_pt(m) for m in all_months]
        monthly_receita = [receita_by_month.get(m, 0.0) for m in all_months]
        monthly_custo = [custo_by_month.get(m, 0.0) for m in all_months]
        monthly_lucro = [r - c for r, c in zip(monthly_receita, monthly_custo)]

        now = timezone.now()
        start_30 = now - timedelta(days=30)
        receita_30 = (
            NotaCarregamento.objects
            .filter(created_by=user, data_criacao__gte=start_30)
            .aggregate(total=Sum(receita_expr))
            .get('total') or 0
        )
        custo_30 = (
            RegistroFinanceiro.objects
            .filter(nota__created_by=user, nota__data_criacao__gte=start_30)
            .aggregate(total=Sum('valor_custo_total'))
            .get('total') or 0
        )
        lucro_30 = float(receita_30) - float(custo_30)

        status_counts_map = {'PAGO': 0, 'PARCIAL': 0, 'PENDENTE': 0}
        for row in (
            RegistroFinanceiro.objects
            .filter(nota__created_by=user)
            .values('status_pagamento')
            .annotate(c=Count('id'))
        ):
            key = (row['status_pagamento'] or '').upper()
            if key in status_counts_map:
                status_counts_map[key] = row['c'] or 0

        mix_map = {'SOJA': 0, 'MILHO': 0}
        for row in (
            NotaCarregamento.objects
            .filter(created_by=user)
            .values('tipo_grao')
            .annotate(c=Count('id'))
        ):
            tg = (row['tipo_grao'] or '').upper()
            if tg in mix_map:
                mix_map[tg] = row['c'] or 0

        context['monthly_labels_json'] = json.dumps(monthly_labels, ensure_ascii=False)
        context['monthly_receita_json'] = json.dumps(monthly_receita, ensure_ascii=False)
        context['monthly_custo_json'] = json.dumps(monthly_custo, ensure_ascii=False)
        context['monthly_lucro_json'] = json.dumps(monthly_lucro, ensure_ascii=False)
        context['status_pagamentos_json'] = json.dumps(status_counts_map, ensure_ascii=False)
        context['mix_graos_json'] = json.dumps(mix_map, ensure_ascii=False)
        context['kpis_json'] = json.dumps({
            'receita_30': float(receita_30),
            'custo_30': float(custo_30),
            'lucro_30': float(lucro_30),
        }, ensure_ascii=False)

        return context


# ==============================================================================
# FINANCIAL
# ==============================================================================

class RegistroFinanceiroListView(ActorMixin, ListView):
    model = NotaCarregamento
    template_name = 'prograos/financeiro_list.html'
    context_object_name = 'notas'
    paginate_by = 15

    def get_queryset(self):
        user = self.actor()
        return NotaCarregamento.objects.filter(created_by=user).order_by('-data_criacao')


def financeiro_detail_view(request, nota_pk):
    user = get_actor(request)
    nota = get_object_or_404(NotaCarregamento, pk=nota_pk, created_by=user)
    registro_financeiro, criado = RegistroFinanceiro.objects.get_or_create(nota=nota)
    if criado:
        messages.info(request, f"Registro financeiro criado para a Nota #{nota.id}.")
    return render(request, 'prograos/financeiro_detail.html', {'registro': registro_financeiro, 'nota': nota})


# ==============================================================================
# PAYMENTS
# ==============================================================================

class PagamentoListView(ActorMixin, ListView):
    model = Pagamento
    template_name = 'prograos/pagamento_list.html'
    context_object_name = 'pagamentos'
    paginate_by = 20

    def get_queryset(self):
        user = self.actor()
        return Pagamento.objects.filter(
            registro_financeiro__nota__created_by=user
        ).order_by('-data_pagamento')


class PagamentoCreateView(ActorMixin, CreateView):
    model = Pagamento
    form_class = PagamentoForm
    template_name = 'prograos/pagamento_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.actor()
        nota = get_object_or_404(NotaCarregamento, pk=self.kwargs['nota_pk'], created_by=user)
        context['nota'] = nota
        context['registro_financeiro'] = getattr(nota, 'financeiro', None)
        return context

    def form_valid(self, form):
        user = self.actor()
        nota = get_object_or_404(NotaCarregamento, pk=self.kwargs['nota_pk'], created_by=user)
        registro_financeiro, _ = RegistroFinanceiro.objects.get_or_create(nota=nota)
        form.instance.registro_financeiro = registro_financeiro
        form.instance.created_by = user
        messages.success(self.request, "Pagamento registrado com sucesso!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('prograos:financeiro_detail', kwargs={'nota_pk': self.kwargs['nota_pk']})


class PagamentoUpdateView(ActorMixin, UpdateView):
    model = Pagamento
    form_class = PagamentoForm
    template_name = 'prograos/pagamento_form.html'

    def get_queryset(self):
        user = self.actor()
        return Pagamento.objects.filter(created_by=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['registro_financeiro'] = self.object.registro_financeiro
        context['nota'] = self.object.registro_financeiro.nota
        return context

    def form_valid(self, form):
        messages.success(self.request, "Pagamento atualizado com sucesso!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('prograos:financeiro_detail', kwargs={'nota_pk': self.object.registro_financeiro.nota.pk})


class PagamentoDeleteView(ActorMixin, DeleteView):
    model = Pagamento
    template_name = 'prograos/pagamento_confirm_delete.html'

    def get_queryset(self):
        user = self.actor()
        return Pagamento.objects.filter(created_by=user)

    def get_success_url(self):
        messages.success(self.request, "Pagamento excluído com sucesso!")
        return reverse('prograos:financeiro_detail', kwargs={'nota_pk': self.object.registro_financeiro.nota.pk})


# ==============================================================================
# PDFS
# ==============================================================================

def generate_pesagem_ticket_pdf_view(request, pk):
    user = get_actor(request)
    pesagem = get_object_or_404(PesagemCaminhao, id=pk, created_by=user)
    return ReportGenerator.generate_pesagem_ticket_pdf(pesagem)


def generate_nota_carregamento_pdf_view(request, pk):
    user = get_actor(request)
    nota = get_object_or_404(NotaCarregamento, id=pk, created_by=user)
    return ReportGenerator.generate_nota_pdf(nota)


# ==============================================================================
# SAMPLES (CRUD)
# ==============================================================================

class AmostraListView(ActorMixin, ListView):
    model = Amostra
    template_name = 'prograos/amostra_list.html'
    context_object_name = 'amostras'
    paginate_by = 20

    def get_queryset(self):
        user = self.actor()
        return Amostra.objects.filter(created_by=user).order_by('-data_criacao')


class AmostraDetailView(ActorMixin, DetailView):
    model = Amostra
    template_name = 'prograos/amostra_detail.html'
    context_object_name = 'amostra'

    def get_queryset(self):
        user = self.actor()
        return Amostra.objects.filter(created_by=user)


class AmostraCreateView(ActorMixin, CreateView):
    model = Amostra
    form_class = AmostraForm
    template_name = 'prograos/amostra_form.html'
    success_url = reverse_lazy('prograos:dashboard')

    def form_valid(self, form):
        user = self.actor()
        form.instance.created_by = user
        amostra = form.save(commit=False)
        calculos = GrainCalculator.aplicar_calculos(amostra)
        amostra.peso_util = calculos.get('peso_util')
        amostra.status = calculos.get('status')
        amostra.save()
        messages.success(self.request, f"Amostra #{amostra.id} criada com sucesso!")
        return redirect(self.success_url)


class AmostraUpdateView(ActorMixin, UpdateView):
    model = Amostra
    form_class = AmostraForm
    template_name = 'prograos/amostra_form.html'
    success_url = reverse_lazy('prograos:dashboard')

    def get_queryset(self):
        user = self.actor()
        return Amostra.objects.filter(created_by=user)

    def form_valid(self, form):
        user = self.actor()
        form.instance.last_updated_by = user
        amostra = form.save(commit=False)
        calculos = GrainCalculator.aplicar_calculos(amostra)
        amostra.peso_util = calculos.get('peso_util')
        amostra.status = calculos.get('status')
        amostra.save()
        messages.success(self.request, f"Amostra #{amostra.id} atualizada com sucesso!")
        return redirect(self.success_url)


class AmostraDeleteView(ActorMixin, DeleteView):
    model = Amostra
    template_name = 'prograos/amostra_confirm_delete.html'
    success_url = reverse_lazy('prograos:dashboard')

    def get_queryset(self):
        user = self.actor()
        return Amostra.objects.filter(created_by=user)

    def form_valid(self, form):
        messages.success(self.request, f"Amostra #{self.get_object().id} deletada com sucesso!")
        return super().form_valid(form)


# ==============================================================================
# TRUCK WEIGHING (CRUD)
# ==============================================================================

class PesagemListView(ActorMixin, ListView):
    model = PesagemCaminhao
    template_name = 'prograos/pesagem_list.html'
    context_object_name = 'pesagens'
    paginate_by = 10

    def get_queryset(self):
        user = self.actor()
        return PesagemCaminhao.objects.filter(
            created_by=user
        ).order_by('status', '-data_final', '-data_tara')


class PesagemCreateView(ActorMixin, CreateView):
    model = PesagemCaminhao
    form_class = PesagemTaraForm
    template_name = 'prograos/pesagem_create.html'

    def form_valid(self, form):
        user = self.actor()
        form.instance.created_by = user
        form.instance.data_tara = timezone.now()
        form.instance.status = PesagemCaminhao.Status.PENDENTE
        messages.success(
            self.request, f"Pesagem inicial para a placa {
                form.instance.placa} salva. Agora, insira o peso final.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('prograos:pesagem_update', kwargs={'pk': self.object.pk})


class PesagemUpdateView(ActorMixin, UpdateView):
    model = PesagemCaminhao
    template_name = 'prograos/pesagem_update.html'
    success_url = reverse_lazy('prograos:pesagem_list')

    def get_queryset(self):
        user = self.actor()
        return PesagemCaminhao.objects.filter(created_by=user)

    def get_form_class(self):
        if self.object.status == PesagemCaminhao.Status.PENDENTE:
            return PesagemFinalForm
        return PesagemTaraForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_finalizing'] = (self.object.status == PesagemCaminhao.Status.PENDENTE)
        return context

    def form_valid(self, form):
        if self.object.status == PesagemCaminhao.Status.PENDENTE:
            form.instance.data_final = timezone.now()
            form.instance.status = PesagemCaminhao.Status.CONCLUIDO
            messages.success(self.request, f"Pesagem para a placa {self.object.placa} finalizada com sucesso!")
        else:
            messages.success(self.request, f"Pesagem para a placa {self.object.placa} atualizada com sucesso!")
        return super().form_valid(form)


class PesagemDetailView(ActorMixin, DetailView):
    model = PesagemCaminhao
    template_name = 'prograos/pesagem_detail.html'
    context_object_name = 'pesagem'

    def get_queryset(self):
        user = self.actor()
        return PesagemCaminhao.objects.filter(created_by=user)


class PesagemDeleteView(ActorMixin, DeleteView):
    model = PesagemCaminhao
    template_name = 'prograos/pesagem_confirm_delete.html'
    success_url = reverse_lazy('prograos:pesagem_list')

    def get_queryset(self):
        user = self.actor()
        return PesagemCaminhao.objects.filter(created_by=user)

    def form_valid(self, form):
        messages.success(self.request, f"Pesagem para a placa {self.get_object().placa} deletada com sucesso!")
        return super().form_valid(form)


# ==============================================================================
# LOADING ORDER (CRUD)
# ==============================================================================

class NotaFormContextMixin(ActorMixin):
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.actor()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.actor()
        pesagens = PesagemCaminhao.objects.filter(created_by=user)
        pesagens_data = {
            str(p.id): {
                'tipo_grao': p.tipo_grao,
                'tara': float(p.tara or 0.0),
                'peso_carregado': float(p.peso_carregado or 0.0)
            } for p in pesagens
        }
        context['pesagens_json'] = json.dumps(pesagens_data, cls=DjangoJSONEncoder)
        return context


class NotaListView(NotaFormContextMixin, ListView):
    model = NotaCarregamento
    template_name = 'prograos/nota_list.html'
    context_object_name = 'notas'
    paginate_by = 10

    def get_queryset(self):
        user = self.actor()
        return NotaCarregamento.objects.filter(created_by=user).order_by('-data_criacao')


class NotaDetailView(ActorMixin, DetailView):
    model = NotaCarregamento
    template_name = 'prograos/nota_detail.html'
    context_object_name = 'nota'

    def get_queryset(self):
        user = self.actor()
        return NotaCarregamento.objects.filter(created_by=user)


class NotaCreateView(NotaFormContextMixin, CreateView):
    model = NotaCarregamento
    form_class = NotaCarregamentoForm
    template_name = 'prograos/create_nota.html'
    success_url = reverse_lazy('prograos:nota_list')

    def form_valid(self, form):
        user = self.actor()
        nota = form.save(commit=False)
        nota.created_by = user

        pesagem_selecionada = form.cleaned_data.get('pesagem')
        if pesagem_selecionada:
            nota.tipo_grao = pesagem_selecionada.tipo_grao
            nota.quantidade_sacos = (pesagem_selecionada.peso_carregado - pesagem_selecionada.tara) / 60

        nota.save()
        messages.success(self.request, f"Nota Placa #{nota.pesagem.placa} criada com sucesso!")
        return redirect(self.success_url)


class NotaUpdateView(NotaFormContextMixin, UpdateView):
    model = NotaCarregamento
    form_class = NotaCarregamentoForm
    template_name = 'prograos/create_nota.html'
    success_url = reverse_lazy('prograos:nota_list')

    def get_queryset(self):
        user = self.actor()
        return NotaCarregamento.objects.filter(created_by=user)

    def form_valid(self, form):
        nota = form.save(commit=False)
        pesagem_selecionada = form.cleaned_data.get('pesagem')
        if pesagem_selecionada:
            nota.tipo_grao = pesagem_selecionada.tipo_grao
            nota.quantidade_sacos = pesagem_selecionada.peso_carregado - pesagem_selecionada.tara
        nota.save()
        messages.success(self.request, f"Nota Placa #{nota.pesagem.placa} atualizada com sucesso!")
        return redirect(self.success_url)


class NotaDeleteView(ActorMixin, DeleteView):
    model = NotaCarregamento
    template_name = 'prograos/nota_confirm_delete.html'
    success_url = reverse_lazy('prograos:nota_list')

    def get_queryset(self):
        user = self.actor()
        return NotaCarregamento.objects.filter(created_by=user)

    def form_valid(self, form):
        messages.success(self.request, f"Nota #{self.get_object().id} deletada com sucesso!")
        return super().form_valid(form)
