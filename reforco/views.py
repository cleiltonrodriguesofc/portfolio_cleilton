from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Aluno, Presenca, Pagamento
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Sum, Count, Q
from django.contrib.auth import logout as auth_logout

def logout(request):
    #isso encerra a sessão
    auth_logout(request)  
    # redireciona para a URL de login
    return render(request, 'core/project_list.html')  



# Dashboard
# @login_required
def dashboard(request):
    """
    View para a página inicial (dashboard) do sistema.
    """
    # Total de alunos ativos
    total_alunos = Aluno.objects.filter(status=Aluno.ATIVO).count()
    
    # Presentes hoje
    hoje = timezone.now().date()
    presentes_hoje = Presenca.objects.filter(data=hoje, presente=True).select_related('aluno')
    total_presentes = presentes_hoje.count()
    
    # Pagamentos pendentes
    pagamentos_pendentes = Pagamento.objects.filter(pago=False).select_related('aluno').order_by('mes_referencia')
    total_pendentes = pagamentos_pendentes.count()
    
    # Aniversariantes do mês
    mes_atual = timezone.now().month
    aniversariantes = Aluno.objects.filter(
        status=Aluno.ATIVO,
        data_nascimento__month=mes_atual
    ).order_by('data_nascimento__day')
    total_aniversariantes = aniversariantes.count()
    
    context = {
        'total_alunos': total_alunos,
        'total_presentes': total_presentes,
        'total_pendentes': total_pendentes,
        'total_aniversariantes': total_aniversariantes,
        'presentes_hoje': presentes_hoje,
        'pagamentos_pendentes': pagamentos_pendentes[:5],  # Limita a 5 para não sobrecarregar o dashboard
        'aniversariantes': aniversariantes,
    }
    
    return render(request, 'reforco/dashboard.html', context)

# Views para Alunos
# @login_required
def aluno_list(request):
    """
    View para listar todos os alunos.
    """
    # Filtro por status
    status_filter = request.GET.get('status', None)
    if status_filter:
        alunos = Aluno.objects.filter(status=status_filter)
    else:
        alunos = Aluno.objects.all()
    
    # Ordenação
    alunos = alunos.order_by('nome')
    
    context = {
        'alunos': alunos,
        'status_filter': status_filter,
    }
    
    return render(request, 'reforco/aluno_list.html', context)

# @login_required
def aluno_create(request):
    """
    View para criar um novo aluno.
    """
    from .forms import AlunoForm
    
    if request.method == 'POST':
        form = AlunoForm(request.POST)
        if form.is_valid():
            aluno = form.save()
            messages.success(request, f'Aluno {aluno.nome} cadastrado com sucesso!')
            return redirect('aluno_list')
    else:
        form = AlunoForm()
    
    context = {
        'form': form,
        'title': 'Novo Aluno',
    }
    
    return render(request, 'reforco/aluno_form.html', context)

# @login_required
def aluno_update(request, pk):
    """
    View para atualizar um aluno existente.
    """
    from .forms import AlunoForm
    
    aluno = get_object_or_404(Aluno, pk=pk)
    
    if request.method == 'POST':
        form = AlunoForm(request.POST, instance=aluno)
        if form.is_valid():
            aluno = form.save()
            messages.success(request, f'Aluno {aluno.nome} atualizado com sucesso!')
            return redirect('aluno_list')
    else:
        form = AlunoForm(instance=aluno)
    
    context = {
        'form': form,
        'aluno': aluno,
        'title': f'Editar Aluno: {aluno.nome}',
    }
    
    return render(request, 'reforco/aluno_form.html', context)

# @login_required
def aluno_detail(request, pk):
    """
    View para visualizar detalhes de um aluno.
    """
    aluno = get_object_or_404(Aluno, pk=pk)
    
    # Histórico de presenças
    presencas = Presenca.objects.filter(aluno=aluno).order_by('-data')
    
    # Histórico de pagamentos
    pagamentos = Pagamento.objects.filter(aluno=aluno).order_by('-mes_referencia')
    
    context = {
        'aluno': aluno,
        'presencas': presencas,
        'pagamentos': pagamentos,
    }
    
    return render(request, 'reforco/aluno_detail.html', context)

# Views para Presença
# @login_required
def presenca_list(request):
    """
    View para listar presenças.
    """
    # Filtro por data
    data_filter = request.GET.get('data', None)
    if data_filter:
        try:
            data = datetime.strptime(data_filter, '%Y-%m-%d').date()
            presencas = Presenca.objects.filter(data=data)
        except ValueError:
            presencas = Presenca.objects.all().order_by('-data')
    else:
        presencas = Presenca.objects.all().order_by('-data')
    
    context = {
        'presencas': presencas,
        'data_filter': data_filter,
    }
    
    return render(request, 'reforco/presenca_list.html', context)

# @login_required
def presenca_create(request):
    """
    View para marcar presença dos alunos.
    """
    from .forms import PresencaMultiForm
    
    # Obter apenas alunos ativos
    alunos = Aluno.objects.filter(status=Aluno.ATIVO).order_by("nome")
    
    # Obter a data da requisição (GET ou POST)
    data_selecionada_str = request.GET.get("data") or request.POST.get("data")
    data_selecionada = None
    if data_selecionada_str:
        try:
            data_selecionada = datetime.strptime(data_selecionada_str, "%d/%m/%Y").date()
        except ValueError:
            messages.error(request, "Formato de data inválido. Use DD/MM/AAAA.")
            data_selecionada = timezone.now().date()  # Volta para a data de hoje em caso de erro
    else:
        data_selecionada = timezone.now().date()

    if request.method == "POST":
        # Validar data
        data = request.POST.get("data")
        if not data:
            messages.error(request, "Selecione a data.")
            return redirect("presenca_create")

        try:
            data = datetime.strptime(data, "%d/%m/%Y").date()
        except ValueError:
            messages.error(request, "Formato de data inválido. Use DD/MM/AAAA.")
            return redirect("presenca_create")
        
        # Recebe os IDs dos alunos marcados como presentes
        presencas_ids = request.POST.getlist("presencas")

        # Remove presenças já salvas para a data
        Presenca.objects.filter(data=data).delete()

        # Cria novas presenças (presente=True se marcado, False se não marcado)
        presencas_criadas = 0
        for aluno in alunos:
            presente = str(aluno.id) in presencas_ids
            Presenca.objects.create(
                aluno=aluno,
                data=data,
                presente=presente
            )
            if presente:
                presencas_criadas += 1

        messages.success(
            request,
            f"Presença registrada com sucesso para {data.strftime('%d/%m/%Y')}! {presencas_criadas} alunos presentes."
        )
        return redirect("presenca_create")
    else:
        # Pré-preencher o formulário com a data selecionada e presenças existentes
        initial_data = {"data": data_selecionada}
        form = PresencaMultiForm(initial=initial_data, alunos=alunos, data_inicial=data_selecionada)
        
        presencas_existentes = Presenca.objects.filter(data=data_selecionada)
        alunos_presentes_ids = set(presenca.aluno.id for presenca in presencas_existentes if presenca.presente)
        for presenca in presencas_existentes:
            if f"aluno_{presenca.aluno.id}" in form.fields:
                form.fields[f"aluno_{presenca.aluno.id}"].initial = presenca.presente

    context = {
        "form": form,
        "alunos": alunos,
        "data_selecionada": data_selecionada.strftime("%d/%m/%Y"),  # Formato DD/MM/YYYY para input do datepicker
        "alunos_presentes_ids": alunos_presentes_ids,
    }
    return render(request, "reforco/presenca_form.html", context)

# Views para Pagamentos
# @login_required
def pagamento_list(request):
    """
    View para listar pagamentos.
    """
    # Filtro por status (pago/pendente)
    status_filter = request.GET.get('status', None)
    if status_filter == 'pago':
        pagamentos = Pagamento.objects.filter(pago=True)
    elif status_filter == 'pendente':
        pagamentos = Pagamento.objects.filter(pago=False)
    else:
        pagamentos = Pagamento.objects.all()
    
    # Filtro por aluno
    aluno_filter = request.GET.get('aluno', None)
    if aluno_filter:
        pagamentos = pagamentos.filter(aluno_id=aluno_filter)
    
    # Ordenação
    pagamentos = pagamentos.order_by('-mes_referencia', 'aluno__nome')
    
    # Lista de alunos para o filtro
    alunos = Aluno.objects.filter(status=Aluno.ATIVO).order_by('nome')
    
    context = {
        'pagamentos': pagamentos,
        'status_filter': status_filter,
        'aluno_filter': aluno_filter,
        'alunos': alunos,
    }
    
    return render(request, 'reforco/pagamento_list.html', context)

# @login_required
def pagamento_create(request):
    """
    View para registrar um novo pagamento.
    """
    from .forms import PagamentoForm
    
    if request.method == 'POST':
        form = PagamentoForm(request.POST)
        if form.is_valid():
            pagamento = form.save()
            messages.success(request, f'Pagamento registrado com sucesso para {pagamento.aluno.nome}!')
            return redirect('pagamento_list')
    else:
        # Pré-selecionar o aluno se vier da página de detalhes do aluno
        aluno_id = request.GET.get('aluno', None)
        if aluno_id:
            form = PagamentoForm(initial={'aluno': aluno_id})
        else:
            form = PagamentoForm()
    
    context = {
        'form': form,
        'title': 'Novo Pagamento',
    }
    
    return render(request, 'reforco/pagamento_form.html', context)

# @login_required
def pagamento_update(request, pk):
    """
    View para atualizar um pagamento existente.
    """
    from .forms import PagamentoForm
    
    pagamento = get_object_or_404(Pagamento, pk=pk)
    
    if request.method == 'POST':
        form = PagamentoForm(request.POST, instance=pagamento)
        if form.is_valid():
            pagamento = form.save()
            messages.success(request, f'Pagamento atualizado com sucesso para {pagamento.aluno.nome}!')
            return redirect('pagamento_list')
    else:
        form = PagamentoForm(instance=pagamento)
    
    context = {
        'form': form,
        'pagamento': pagamento,
        'title': f'Editar Pagamento: {pagamento.aluno.nome} - {pagamento.mes_referencia.strftime("%m/%Y")}',
    }
    
    return render(request, 'reforco/pagamento_form.html', context)

# Views para Relatórios
# @login_required
def relatorio_presenca(request):
    """
    View para gerar relatório de presenças.
    """
    # Filtros
    aluno_id = request.GET.get('aluno', None)
    data_inicio = request.GET.get('data_inicio', None)
    data_fim = request.GET.get('data_fim', None)
    
    # Lista de alunos para o filtro
    alunos = Aluno.objects.filter(status=Aluno.ATIVO).order_by('nome')
    
    # Inicializar variáveis
    presencas = None
    aluno_selecionado = None
    total_presencas = 0
    total_faltas = 0
    percentual_presenca = 0
    
    # Aplicar filtros se fornecidos
    if aluno_id:
        try:
            aluno_selecionado = Aluno.objects.get(pk=aluno_id)
            presencas_query = Presenca.objects.filter(aluno=aluno_selecionado)
            
            if data_inicio:
                try:
                    data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d').date()
                    presencas_query = presencas_query.filter(data__gte=data_inicio_obj)
                except ValueError:
                    pass
            
            if data_fim:
                try:
                    data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d').date()
                    presencas_query = presencas_query.filter(data__lte=data_fim_obj)
                except ValueError:
                    pass
            
            presencas = presencas_query.order_by('-data')
            
            # Calcular estatísticas
            total_presencas = presencas.filter(presente=True).count()
            total_faltas = presencas.filter(presente=False).count()
            total_dias = total_presencas + total_faltas
            
            if total_dias > 0:
                percentual_presenca = (total_presencas / total_dias) * 100
        except Aluno.DoesNotExist:
            pass
    
    context = {
        'alunos': alunos,
        'aluno_selecionado': aluno_selecionado,
        'presencas': presencas,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'total_presencas': total_presencas,
        'total_faltas': total_faltas,
        'percentual_presenca': percentual_presenca,
    }
    
    return render(request, 'reforco/relatorio_presenca.html', context)

# @login_required
def relatorio_pagamentos(request):
    """
    View para gerar relatório de pagamentos.
    """
    # Filtros
    aluno_id = request.GET.get('aluno', None)
    status = request.GET.get('status', None)
    data_inicio = request.GET.get('data_inicio', None)
    data_fim = request.GET.get('data_fim', None)
    
    # Lista de alunos para o filtro
    alunos = Aluno.objects.filter(status=Aluno.ATIVO).order_by('nome')
    
    # Inicializar variáveis
    pagamentos = None
    aluno_selecionado = None
    total_pagos = 0
    total_pendentes = 0
    valor_total_pago = 0
    valor_total_pendente = 0
    
    # Aplicar filtros
    pagamentos_query = Pagamento.objects.all()
    
    if aluno_id:
        try:
            aluno_selecionado = Aluno.objects.get(pk=aluno_id)
            pagamentos_query = pagamentos_query.filter(aluno=aluno_selecionado)
        except Aluno.DoesNotExist:
            pass
    
    if status:
        if status == 'pago':
            pagamentos_query = pagamentos_query.filter(pago=True)
        elif status == 'pendente':
            pagamentos_query = pagamentos_query.filter(pago=False)
    
    if data_inicio:
        try:
            data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d').date()
            pagamentos_query = pagamentos_query.filter(mes_referencia__gte=data_inicio_obj)
        except ValueError:
            pass
    
    if data_fim:
        try:
            data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d').date()
            pagamentos_query = pagamentos_query.filter(mes_referencia__lte=data_fim_obj)
        except ValueError:
            pass
    
    pagamentos = pagamentos_query.order_by('-mes_referencia', 'aluno__nome')
    
    # Calcular estatísticas
    total_pagos = pagamentos.filter(pago=True).count()
    total_pendentes = pagamentos.filter(pago=False).count()
    
    # Calcular valores totais
    for pagamento in pagamentos:
        if pagamento.pago:
            valor_total_pago += pagamento.valor
        else:
            valor_total_pendente += pagamento.valor
    
    context = {
        'alunos': alunos,
        'aluno_selecionado': aluno_selecionado,
        'pagamentos': pagamentos,
        'status': status,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'total_pagos': total_pagos,
        'total_pendentes': total_pendentes,
        'valor_total_pago': valor_total_pago,
        'valor_total_pendente': valor_total_pendente,
    }
    
    return render(request, 'reforco/relatorio_pagamentos.html', context)

# Views para Mensagens
# @login_required
def mensagens(request):
    """
    View para gerar mensagens para WhatsApp.
    """
    # Lista de alunos para o filtro
    alunos = Aluno.objects.filter(status=Aluno.ATIVO).order_by('nome')
    
    # Inicializar variáveis
    aluno_selecionado = None
    pagamentos_pendentes = None
    
    # Filtro por aluno
    aluno_id = request.GET.get('aluno', None)
    if aluno_id:
        try:
            aluno_selecionado = Aluno.objects.get(pk=aluno_id)
            pagamentos_pendentes = Pagamento.objects.filter(
                aluno=aluno_selecionado,
                pago=False
            ).order_by('mes_referencia')
        except Aluno.DoesNotExist:
            pass
    
    # Tipos de mensagens disponíveis
    tipos_mensagem = [
        {
            'id': 'cobranca',
            'nome': 'Cobrança de Pagamento',
            'descricao': 'Mensagem para cobrar pagamentos pendentes.',
            'icone': 'fas fa-money-bill-wave',
        },
        {
            'id': 'aniversario',
            'nome': 'Felicitação de Aniversário',
            'descricao': 'Mensagem para parabenizar pelo aniversário.',
            'icone': 'fas fa-birthday-cake',
        },
        {
            'id': 'ausencia',
            'nome': 'Aviso de Ausência',
            'descricao': 'Mensagem para avisar sobre ausências recentes.',
            'icone': 'fas fa-user-clock',
        },
        {
            'id': 'informativo',
            'nome': 'Informativo Geral',
            'descricao': 'Mensagem para informações gerais.',
            'icone': 'fas fa-info-circle',
        },
    ]
    
    context = {
        'alunos': alunos,
        'aluno_selecionado': aluno_selecionado,
        'pagamentos_pendentes': pagamentos_pendentes,
        'tipos_mensagem': tipos_mensagem,
    }
    
    return render(request, 'reforco/mensagens.html', context)

