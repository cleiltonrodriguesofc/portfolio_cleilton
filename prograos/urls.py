# prograos/urls.py  — público (sem exigir login)

from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from rest_framework.routers import DefaultRouter

# ---- APIs utilitárias / integrações ----
from .scale_views import read_scale_weight, list_scale_ports, test_scale_connection
from .reports import export_amostras_pdf, export_amostras_excel
from .test_views import get_csrf_token, health_check

# ---- Views HTML (UI) ----
from .views import (
    DashboardView,
    AmostraListView, AmostraDetailView, AmostraCreateView, AmostraUpdateView, AmostraDeleteView,
    PesagemListView, PesagemCreateView, PesagemDetailView, PesagemDeleteView, PesagemUpdateView,
    NotaListView, NotaDetailView, NotaCreateView, NotaUpdateView, NotaDeleteView,
    generate_nota_carregamento_pdf_view, generate_pesagem_ticket_pdf_view,
    RegistroFinanceiroListView, financeiro_detail_view,
    PagamentoListView, PagamentoCreateView, PagamentoUpdateView, PagamentoDeleteView,
)


app_name = "prograos"
# ------------------ DRF Router (adicione seus ViewSets aqui se quiser expor JSON) ------------------
# router = DefaultRouter()
# Ex.: router.register(r'amostras', AmostraViewSet, basename='amostra')
# Ex.: router.register(r'activity-logs', ActivityLogViewSet, basename='activity-log')

# ------------------ API URLs (prefixo /api/) ------------------
api_patterns = [
    # path('', include(router.urls)),

    # Utilidades / integrações
    path('scale/ports/', list_scale_ports, name='scale_ports'),
    path('scale/read/', read_scale_weight, name='scale_read'),
    path('scale/test/', test_scale_connection, name='scale_test'),

    path('reports/amostras/pdf/', export_amostras_pdf, name='export_amostras_pdf'),
    path('reports/amostras/excel/', export_amostras_excel, name='export_amostras_excel'),

    path('csrf-token/', get_csrf_token, name='get_csrf_token'),
    path('health/', health_check, name='health_check'),
]

# ------------------ UI (HTML) URLs — todas públicas ------------------
ui_patterns = [
    # Admin (leave only in dev; comment in production if you don't want to expose)
    path("admin/", admin.site.urls),

    # Dashboard / Home
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("", DashboardView.as_view(), name="home"),

    # Amostras
    path("amostras/", AmostraListView.as_view(), name="amostra_list"),
    path("amostras/nova/", AmostraCreateView.as_view(), name="amostra_create"),
    path("amostras/<int:pk>/", AmostraDetailView.as_view(), name="amostra_detail"),
    path("amostras/<int:pk>/editar/", AmostraUpdateView.as_view(), name="amostra_update"),
    path("amostras/<int:pk>/excluir/", AmostraDeleteView.as_view(), name="amostra_delete"),

    # Pesagens
    path('pesagens/', PesagemListView.as_view(), name='pesagem_list'),
    path('pesagens/nova/', PesagemCreateView.as_view(), name='pesagem_create'),
    path('pesagem/<int:pk>/', PesagemDetailView.as_view(), name='pesagem_detail'),
    path('pesagem/<int:pk>/editar/', PesagemUpdateView.as_view(), name='pesagem_update'),
    path('pesagem/<int:pk>/excluir/', PesagemDeleteView.as_view(), name='pesagem_delete'),

    # Notas
    path('notas/', NotaListView.as_view(), name='nota_list'),
    path('nota/nova/', NotaCreateView.as_view(), name='nota_create'),
    path('nota/<int:pk>/', NotaDetailView.as_view(), name='nota_detail'),
    path('nota/<int:pk>/editar/', NotaUpdateView.as_view(), name='nota_update'),
    path('nota/<int:pk>/excluir/', NotaDeleteView.as_view(), name='nota_delete'),
    path('nota/<int:pk>/pdf/', generate_nota_carregamento_pdf_view, name='nota_pdf'),

    # PDFs / tickets
    path('pesagem/<int:pk>/ticket/', generate_pesagem_ticket_pdf_view, name='pesagem_ticket_pdf'),

    # Financeiro
    path('financeiro/', RegistroFinanceiroListView.as_view(), name='financeiro_list'),
    path('financeiro/nota/<int:nota_pk>/', financeiro_detail_view, name='financeiro_detail'),

    # Pagamentos
    path('pagamentos/', PagamentoListView.as_view(), name='pagamento_list'),
    path('pagamento/nota/<int:nota_pk>/novo/', PagamentoCreateView.as_view(), name='pagamento_create'),
    path('pagamento/<int:pk>/editar/', PagamentoUpdateView.as_view(), name='pagamento_update'),
    path('pagamento/<int:pk>/excluir/', PagamentoDeleteView.as_view(), name='pagamento_delete'),
]

# ------------------ Final urlpatterns ------------------
urlpatterns = [
    path('api/', include((api_patterns, 'api'))),
] + ui_patterns

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
