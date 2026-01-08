from django.db.models import Sum, Count, F, ExpressionWrapper, DecimalField
from django.db.models.functions import TruncMonth, Coalesce
from django.utils import timezone
from datetime import datetime
import json
from decimal import Decimal

from prograos.models import Amostra, PesagemCaminhao, NotaCarregamento, RegistroFinanceiro


class DashboardService:
    @staticmethod
    def get_dashboard_stats(user):
        """
        Returns stats for the dashboard: counts, recent items, and aggregations.
        """
        context = {}

        # Counts
        context["total_amostras"] = Amostra.objects.filter(created_by=user).count()
        context["amostras_aceitas"] = Amostra.objects.filter(created_by=user, status="ACEITA").count()
        context["amostras_rejeitadas"] = Amostra.objects.filter(created_by=user, status="REJEITADA").count()

        # Recents
        context["ultimas_pesagens"] = PesagemCaminhao.objects.filter(created_by=user).order_by("-data_final")[:5]
        context["ultimas_notas"] = NotaCarregamento.objects.filter(created_by=user).order_by("-data_criacao")[:5]
        context["ultimos_registros_financeiros"] = (
            RegistroFinanceiro.objects
            .filter(nota__created_by=user)
            .select_related('nota', 'nota__pesagem')
            .order_by('-nota__data_criacao')[:5]
        )

        return context

    @staticmethod
    def get_kpis_and_charts(user, request_GET):
        """
        Calculates KPIs, Charts data, and Monthly report data.
        """
        context = {}

        # Expressions
        receita_expr = ExpressionWrapper(
            F('quantidade_sacos') * F('preco_por_saco'),
            output_field=DecimalField(max_digits=18, decimal_places=2),
        )

        # Aggregations by Month
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

        frete_agg = (
            RegistroFinanceiro.objects
            .filter(nota__created_by=user)
            .annotate(m=TruncMonth('nota__data_criacao'))
            .values('m')
            .annotate(frete=Sum(Coalesce('nota__pesagem__frete_total_calculado', Decimal(0.0)), output_field=DecimalField()))
            .order_by('m')
        )

        receita_by_month = {row['m']: float(row['receita'] or 0) for row in notas_agg}
        custo_by_month = {row['m']: float(row['custo'] or 0) for row in custos_agg}
        frete_by_month = {row['m']: float(row['frete'] or 0) for row in frete_agg}

        all_months = sorted(set(list(receita_by_month.keys()) +
                            list(custo_by_month.keys()) + list(frete_by_month.keys())))

        def label_pt(dt):
            meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
            return f"{meses[dt.month-1]}/{str(dt.year)[-2:]}"

        monthly_labels = [label_pt(m) for m in all_months]
        monthly_receita = [receita_by_month.get(m, 0.0) for m in all_months]
        monthly_custo = [custo_by_month.get(m, 0.0) for m in all_months]
        monthly_frete = [frete_by_month.get(m, 0.0) for m in all_months]

        monthly_custo_base = [c - f for c, f in zip(monthly_custo, monthly_frete)]
        monthly_lucro = [r - c for r, c in zip(monthly_receita, monthly_custo)]

        # Serialize Charts
        context['monthly_labels_json'] = json.dumps(monthly_labels, ensure_ascii=False)
        context['monthly_receita_json'] = json.dumps(monthly_receita, ensure_ascii=False)
        context['monthly_custo_json'] = json.dumps(monthly_custo, ensure_ascii=False)
        context['monthly_lucro_json'] = json.dumps(monthly_lucro, ensure_ascii=False)
        context['monthly_custo_base_json'] = json.dumps(monthly_custo_base, ensure_ascii=False)
        context['monthly_frete_json'] = json.dumps(monthly_frete, ensure_ascii=False)

        # Mix & Status
        status_counts_map = {'PAGO': 0, 'PARCIAL': 0, 'PENDENTE': 0}
        for row in (RegistroFinanceiro.objects.filter(nota__created_by=user).values('status_pagamento').annotate(c=Count('id'))):
            key = (row['status_pagamento'] or '').upper()
            if key in status_counts_map:
                status_counts_map[key] = row['c'] or 0
        context['status_pagamentos_json'] = json.dumps(status_counts_map, ensure_ascii=False)

        mix_map = {'SOJA': 0, 'MILHO': 0}
        for row in (NotaCarregamento.objects.filter(created_by=user).values('tipo_grao').annotate(c=Count('id'))):
            tg = (row['tipo_grao'] or '').upper()
            if tg in mix_map:
                mix_map[tg] = row['c'] or 0
        context['mix_graos_json'] = json.dumps(mix_map, ensure_ascii=False)

        # Monthly Selection Logic
        today = timezone.now().date()
        try:
            selected_month = int(request_GET.get('month', today.month))
            selected_year = int(request_GET.get('year', today.year))
        except ValueError:
            selected_month = today.month
            selected_year = today.year

        import calendar
        _, last_day = calendar.monthrange(selected_year, selected_month)
        start_date = datetime(selected_year, selected_month, 1)
        end_date = datetime(selected_year, selected_month, last_day, 23, 59, 59)

        if timezone.is_aware(timezone.now()):
            current_timezone = timezone.get_current_timezone()
            start_date = timezone.make_aware(start_date, current_timezone)
            end_date = timezone.make_aware(end_date, current_timezone)

        # KPIs for Selected Month
        receita_month = NotaCarregamento.objects.filter(created_by=user, data_criacao__range=(
            start_date, end_date)).aggregate(total=Sum(receita_expr)).get('total') or 0
        custo_month = RegistroFinanceiro.objects.filter(nota__created_by=user, nota__data_criacao__range=(
            start_date, end_date)).aggregate(total=Sum('valor_custo_total')).get('total') or 0
        frete_month = RegistroFinanceiro.objects.filter(nota__created_by=user, nota__data_criacao__range=(start_date, end_date)).aggregate(
            total=Sum(Coalesce('nota__pesagem__frete_total_calculado', Decimal(0.0)), output_field=DecimalField())).get('total') or 0
        lucro_month = float(receita_month) - float(custo_month)

        context['kpis_json'] = json.dumps({
            'receita_30': float(receita_month),
            'custo_30': float(custo_month),
            'lucro_30': float(lucro_month),
            'frete_30': float(frete_month),
            'period_label': f"({label_pt(start_date)})"
        }, ensure_ascii=False)

        # Monthly Transactions list
        context['monthly_transactions'] = NotaCarregamento.objects.filter(created_by=user, data_criacao__range=(
            start_date, end_date)).select_related('pesagem', 'financeiro').order_by('-data_criacao')

        # Available Months Dropdown
        available_months_qs = NotaCarregamento.objects.filter(created_by=user).annotate(
            m=TruncMonth('data_criacao')).values('m').distinct().order_by('-m')
        available_months = []
        for item in available_months_qs:
            dt = item['m']
            if dt:
                available_months.append({
                    'value': f"{dt.year}-{dt.month}",
                    'label': f"{label_pt(dt)}",
                    'year': dt.year,
                    'month': dt.month,
                    'selected': (dt.year == selected_year and dt.month == selected_month)
                })

        has_current = any(m['year'] == today.year and m['month'] == today.month for m in available_months)
        if not has_current:
            available_months.insert(0, {
                'value': f"{today.year}-{today.month}",
                'label': f"{label_pt(today)}",
                'year': today.year,
                'month': today.month,
                'selected': (today.year == selected_year and today.month == selected_month)
            })

        context['selected_month_label'] = label_pt(start_date)
        context['selected_year'] = selected_year
        context['selected_month'] = selected_month
        context['available_months'] = available_months

        return context
