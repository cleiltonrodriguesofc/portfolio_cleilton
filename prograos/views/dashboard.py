from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from prograos.models import Amostra
from prograos.services.dashboard_service import DashboardService
from prograos.reports import ReportGenerator
from django.shortcuts import redirect


class DashboardView(LoginRequiredMixin, ListView):
    model = Amostra
    template_name = 'prograos/dashboard.html'
    context_object_name = 'ultimas_amostras'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Get Stats from Service
        stats = DashboardService.get_dashboard_stats(user)
        context.update(stats)

        # Get KPIs and Charts from Service
        kpis = DashboardService.get_kpis_and_charts(user, self.request.GET)
        context.update(kpis)

        return context


def download_monthly_report_pdf_view(request, year, month):
    """
    Download consolidated monthly report.
    """
    if not request.user.is_authenticated:
        return redirect('prograos:login')

    return ReportGenerator.generate_monthly_report_pdf(request.user, year, month)
