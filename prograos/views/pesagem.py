from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from prograos.models import PesagemCaminhao
from prograos.forms import PesagemTaraForm, PesagemFinalForm
from prograos.reports import ReportGenerator


class PesagemListView(LoginRequiredMixin, ListView):
    model = PesagemCaminhao
    template_name = 'prograos/pesagem_list.html'
    context_object_name = 'pesagens'
    paginate_by = 10

    def get_queryset(self):
        return PesagemCaminhao.objects.filter(created_by=self.request.user).order_by('status', '-data_final', '-data_tara')


class PesagemCreateView(LoginRequiredMixin, CreateView):
    model = PesagemCaminhao
    form_class = PesagemTaraForm
    template_name = 'prograos/pesagem_create.html'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.data_tara = timezone.now()
        form.instance.status = PesagemCaminhao.Status.PENDENTE
        messages.success(
            self.request, f"Pesagem inicial para a placa {form.instance.placa} salva. Agora, insira o peso final.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('prograos:pesagem_update', kwargs={'pk': self.object.pk})


class PesagemUpdateView(LoginRequiredMixin, UpdateView):
    model = PesagemCaminhao
    form_class = PesagemTaraForm
    template_name = 'prograos/pesagem_update.html'
    success_url = reverse_lazy('prograos:pesagem_list')

    def get_queryset(self):
        return PesagemCaminhao.objects.filter(created_by=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.object
        if 'tara_form' in kwargs and 'final_form' in kwargs:
            context['tara_form'] = kwargs['tara_form']
            context['final_form'] = kwargs['final_form']
        else:
            context['tara_form'] = PesagemTaraForm(instance=obj)
            context['final_form'] = PesagemFinalForm(instance=obj)
        context['is_finalizing'] = (obj.status == PesagemCaminhao.Status.PENDENTE)
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        tara_form = PesagemTaraForm(request.POST, instance=self.object)
        final_form = PesagemFinalForm(request.POST, instance=self.object)

        if not (tara_form.is_valid() and final_form.is_valid()):
            return self.render_to_response(self.get_context_data(tara_form=tara_form, final_form=final_form))

        pesagem = tara_form.save(commit=False)
        peso_carregado = final_form.cleaned_data.get('peso_carregado')
        pesagem.peso_carregado = peso_carregado

        # Use Service for Calculations can be added to model save or here.
        # Currently model has logic? Let's check model. No, model checks are minimal.
        # Let's use logic here or standard save.

        if self.object.status == PesagemCaminhao.Status.PENDENTE:
            pesagem.data_final = timezone.now()
            pesagem.status = PesagemCaminhao.Status.CONCLUIDO

        pesagem.save()

        if pesagem.status == PesagemCaminhao.Status.CONCLUIDO and self.object.status == PesagemCaminhao.Status.PENDENTE:
            messages.success(request, f"Pesagem para a placa {pesagem.placa} finalizada com sucesso!")
        else:
            messages.success(request, f"Pesagem para a placa {pesagem.placa} atualizada com sucesso!")

        return redirect(self.success_url)


class PesagemDetailView(LoginRequiredMixin, DetailView):
    model = PesagemCaminhao
    template_name = 'prograos/pesagem_detail.html'
    context_object_name = 'pesagem'

    def get_queryset(self):
        return PesagemCaminhao.objects.filter(created_by=self.request.user)


class PesagemDeleteView(LoginRequiredMixin, DeleteView):
    model = PesagemCaminhao
    template_name = 'prograos/pesagem_confirm_delete.html'
    success_url = reverse_lazy('prograos:pesagem_list')

    def get_queryset(self):
        return PesagemCaminhao.objects.filter(created_by=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, f"Pesagem para a placa {self.get_object().placa} deletada com sucesso!")
        return super().form_valid(form)


def generate_pesagem_ticket_pdf_view(request, pk):
    pesagem = get_object_or_404(PesagemCaminhao, id=pk, created_by=request.user)
    return ReportGenerator.generate_pesagem_ticket_pdf(pesagem)
