from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from decimal import Decimal
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.decorators import login_required

from prograos.models import NotaCarregamento, RegistroFinanceiro, Pagamento, PesagemCaminhao
from prograos.forms import NotaCarregamentoForm, PagamentoForm, CalculadoraFreteForm
from prograos.services.finance_service import FinanceService
from prograos.services.weighing_service import WeighingService
from prograos.reports import ReportGenerator

# --- Mixin for Nota Forms ---


class NotaFormContextMixin:
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pesagens = PesagemCaminhao.objects.filter(created_by=self.request.user)
        pesagens_data = {
            str(p.id): {
                'tipo_grao': p.tipo_grao,
                'tara': float(p.tara or 0.0),
                'peso_carregado': float(p.peso_carregado or 0.0)
            } for p in pesagens
        }
        context['pesagens_json'] = json.dumps(pesagens_data, cls=DjangoJSONEncoder)
        return context

# --- NOTA VIEWS ---


class NotaListView(LoginRequiredMixin, ListView):
    model = NotaCarregamento
    template_name = 'prograos/nota_list.html'
    context_object_name = 'notas'
    paginate_by = 10

    def get_queryset(self):
        return NotaCarregamento.objects.filter(created_by=self.request.user).order_by('-data_criacao')


class NotaDetailView(LoginRequiredMixin, DetailView):
    model = NotaCarregamento
    template_name = 'prograos/nota_detail.html'
    context_object_name = 'nota'

    def get_queryset(self):
        return NotaCarregamento.objects.filter(created_by=self.request.user)


class NotaCreateView(LoginRequiredMixin, NotaFormContextMixin, CreateView):
    model = NotaCarregamento
    form_class = NotaCarregamentoForm
    template_name = 'prograos/create_nota.html'
    success_url = reverse_lazy('prograos:nota_list')

    def form_valid(self, form):
        nota = form.save(commit=False)
        nota.created_by = self.request.user

        pesagem_selecionada = form.cleaned_data.get('pesagem')
        if pesagem_selecionada:
            nota.tipo_grao = pesagem_selecionada.tipo_grao
            # Use Service
            net_weight = WeighingService.calculate_net_weight(
                pesagem_selecionada.tara, pesagem_selecionada.peso_carregado)
            nota.quantidade_sacos = WeighingService.calculate_sacks(net_weight)

        nota.save()
        messages.success(self.request, f"Nota Placa #{nota.pesagem.placa} criada com sucesso!")
        return redirect(self.success_url)


class NotaUpdateView(LoginRequiredMixin, NotaFormContextMixin, UpdateView):
    model = NotaCarregamento
    form_class = NotaCarregamentoForm
    template_name = 'prograos/create_nota.html'
    success_url = reverse_lazy('prograos:nota_list')

    def get_queryset(self):
        return NotaCarregamento.objects.filter(created_by=self.request.user)

    def form_valid(self, form):
        nota = form.save(commit=False)
        pesagem_selecionada = form.cleaned_data.get('pesagem')
        if pesagem_selecionada:
            nota.tipo_grao = pesagem_selecionada.tipo_grao
            net_weight = WeighingService.calculate_net_weight(
                pesagem_selecionada.tara, pesagem_selecionada.peso_carregado)
            nota.quantidade_sacos = WeighingService.calculate_sacks(net_weight)

        nota.save()
        messages.success(self.request, f"Nota Placa #{nota.pesagem.placa} atualizada com sucesso!")
        return redirect(self.success_url)


class NotaDeleteView(LoginRequiredMixin, DeleteView):
    model = NotaCarregamento
    template_name = 'prograos/nota_confirm_delete.html'
    success_url = reverse_lazy('prograos:nota_list')

    def get_queryset(self):
        return NotaCarregamento.objects.filter(created_by=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, f"Nota #{self.get_object().id} deletada com sucesso!")
        return super().form_valid(form)


def generate_nota_carregamento_pdf_view(request, pk):
    nota = get_object_or_404(NotaCarregamento, id=pk, created_by=request.user)
    return ReportGenerator.generate_nota_pdf(nota)

# --- FINANCE VIEWS ---


class RegistroFinanceiroListView(LoginRequiredMixin, ListView):
    model = NotaCarregamento
    template_name = 'prograos/financeiro_list.html'
    context_object_name = 'notas'
    paginate_by = 15

    def get_queryset(self):
        return NotaCarregamento.objects.filter(created_by=self.request.user).order_by('-data_criacao')


def financeiro_detail_view(request, nota_pk):
    nota = get_object_or_404(NotaCarregamento, pk=nota_pk, created_by=request.user)
    registro_financeiro, criado = RegistroFinanceiro.objects.get_or_create(nota=nota)

    if criado:
        messages.info(request, f"Registro financeiro criado para a Nota #{nota.id}.")

    preco_venda_saco = registro_financeiro.nota.preco_por_saco or Decimal('0.0')
    frete_saco = Decimal('0.0')
    if registro_financeiro.nota.pesagem:
        frete_saco = registro_financeiro.nota.pesagem.frete_por_saco_calculado or Decimal('0.0')

    venda_liquida_saco = FinanceService.calculate_net_sale_per_sack(preco_venda_saco, frete_saco)

    context = {
        'registro': registro_financeiro,
        'venda_liquida_por_saco': venda_liquida_saco
    }
    return render(request, 'prograos/financeiro_detail.html', context)

# --- PAGAMENTO VIEWS ---


class PagamentoListView(LoginRequiredMixin, ListView):
    model = Pagamento
    template_name = 'prograos/pagamento_list.html'
    context_object_name = 'pagamentos'
    paginate_by = 20

    def get_queryset(self):
        return Pagamento.objects.filter(registro_financeiro__nota__created_by=self.request.user).order_by('-data_pagamento')


class PagamentoCreateView(LoginRequiredMixin, CreateView):
    model = Pagamento
    form_class = PagamentoForm
    template_name = 'prograos/pagamento_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        nota = get_object_or_404(NotaCarregamento, pk=self.kwargs['nota_pk'], created_by=self.request.user)
        context['nota'] = nota
        context['registro_financeiro'] = nota.financeiro
        return context

    def form_valid(self, form):
        nota = get_object_or_404(NotaCarregamento, pk=self.kwargs['nota_pk'], created_by=self.request.user)
        registro_financeiro, _ = RegistroFinanceiro.objects.get_or_create(nota=nota)
        form.instance.registro_financeiro = registro_financeiro
        form.instance.created_by = self.request.user
        messages.success(self.request, "Pagamento registrado com sucesso!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('prograos:financeiro_detail', kwargs={'nota_pk': self.kwargs['nota_pk']})


class PagamentoUpdateView(LoginRequiredMixin, UpdateView):
    model = Pagamento
    form_class = PagamentoForm
    template_name = 'prograos/pagamento_form.html'

    def get_queryset(self):
        return Pagamento.objects.filter(created_by=self.request.user)

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


class PagamentoDeleteView(LoginRequiredMixin, DeleteView):
    model = Pagamento
    template_name = 'prograos/pagamento_confirm_delete.html'

    def get_queryset(self):
        return Pagamento.objects.filter(created_by=self.request.user)

        return reverse('prograos:financeiro_detail', kwargs={'nota_pk': self.object.registro_financeiro.nota.pk})

# --- CALCULADORA FRETE ---


def calculadora_frete_view(request):
    context = {}
    if request.method == 'POST':
        form = CalculadoraFreteForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            K_SACO_EM_KG = Decimal('60.0')
            K_TONELADA_EM_KG = Decimal('1000.0')
            SACOS_POR_TONELADA = K_TONELADA_EM_KG / K_SACO_EM_KG

            custo_grao_saco = data['custo_grao_por_saco']
            preco_base_saco = data['preco_base_venda_por_saco']
            frete_tonelada = data['frete_por_tonelada']
            quantidade_input = data['quantidade']
            unidade = data['unidade_quantidade']

            # 1. Calculations per Sack
            frete_por_saco = frete_tonelada / SACOS_POR_TONELADA
            # lucro_bruto_saco = preco_base_saco - custo_grao_saco
            lucro_liquido_saco = preco_base_saco - custo_grao_saco

            # 2. Total Quantities
            if unidade == 'toneladas':
                total_sacos = (quantidade_input * K_TONELADA_EM_KG) / K_SACO_EM_KG
            else:  # sacos
                total_sacos = quantidade_input

            # 3. Aggregates
            venda_total_carga = total_sacos * (preco_base_saco + frete_por_saco)
            frete_total_carga = total_sacos * frete_por_saco
            lucro_total_carga = total_sacos * lucro_liquido_saco

            # 4. Pack for Template
            context['results'] = {
                'frete_tonelada': frete_tonelada,
                'frete_por_saco': frete_por_saco,
                'lucro_base_saco': lucro_liquido_saco,
                'preco_venda_final_saco': preco_base_saco + frete_por_saco,
                'total_sacos': total_sacos,
                'venda_total_carga': venda_total_carga,
                'frete_total_carga': frete_total_carga,
                'lucro_total_carga': lucro_total_carga,
                'resultado_calculado': True
            }
    else:
        form = CalculadoraFreteForm()

    context['form'] = form
    return render(request, 'calculadora_frete.html', context)


@login_required
def export_recibo_pdf(request, pk):
    """
    View para exportar o Recibo de Pagamento (NotaCarregamento) em PDF.
    """
    try:
        nota = get_object_or_404(NotaCarregamento, pk=pk)
        return ReportGenerator.generate_nota_receipt_pdf(nota)
    except Exception as e:
        messages.error(request, f"Erro ao gerar recibo: {str(e)}")
        return redirect('prograos:financeiro_list')

# --- CALCULADORA FRETE ---


def calculadora_frete_view(request):
    context = {}
    if request.method == 'POST':
        form = CalculadoraFreteForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            K_SACO_EM_KG = Decimal('60.0')
            K_TONELADA_EM_KG = Decimal('1000.0')
            SACOS_POR_TONELADA = K_TONELADA_EM_KG / K_SACO_EM_KG

            custo_grao_saco = data['custo_grao_por_saco']
            preco_base_saco = data['preco_base_venda_por_saco']
            frete_tonelada = data['frete_por_tonelada']
            quantidade_input = data['quantidade']
            unidade = data['unidade_quantidade']

            # 1. Calculations per Sack
            frete_por_saco = frete_tonelada / SACOS_POR_TONELADA
            # lucro_bruto_saco = preco_base_saco - custo_grao_saco
            lucro_liquido_saco = preco_base_saco - custo_grao_saco

            # 2. Total Quantities
            if unidade == 'toneladas':
                total_sacos = (quantidade_input * K_TONELADA_EM_KG) / K_SACO_EM_KG
            else:  # sacos
                total_sacos = quantidade_input

            # 3. Aggregates
            venda_total_carga = total_sacos * (preco_base_saco + frete_por_saco)
            frete_total_carga = total_sacos * frete_por_saco
            lucro_total_carga = total_sacos * lucro_liquido_saco

            # 4. Pack for Template
            context['results'] = {
                'frete_tonelada': frete_tonelada,
                'frete_por_saco': frete_por_saco,
                'lucro_base_saco': lucro_liquido_saco,
                'preco_venda_final_saco': preco_base_saco + frete_por_saco,
                'total_sacos': total_sacos,
                'venda_total_carga': venda_total_carga,
                'frete_total_carga': frete_total_carga,
                'lucro_total_carga': lucro_total_carga,
                'resultado_calculado': True
            }
    else:
        form = CalculadoraFreteForm()

    context['form'] = form
    return render(request, 'prograos/calculadora_frete.html', context)


@login_required
def export_recibo_pdf(request, pk):
    """
    View para exportar o Recibo de Pagamento (NotaCarregamento) em PDF.
    """
    try:
        nota = get_object_or_404(NotaCarregamento, pk=pk)
        return ReportGenerator.generate_nota_receipt_pdf(nota)
    except Exception as e:
        messages.error(request, f"Erro ao gerar recibo: {str(e)}")
        return redirect('prograos:financeiro_list')
