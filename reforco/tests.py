from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from core.models import Aluno, Presenca, Pagamento
from datetime import date

class CoreViewsTest(TestCase):
    def setUp(self):
        # create user and login
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client = Client()
        self.client.login(username='testuser', password='12345')

        # create student for tests
        self.aluno = Aluno.objects.create(
            nome='Teste Aluno',
            status=Aluno.ATIVO,
            data_nascimento=date(2000, 1, 1)
        )

        # create payment for the student
        self.pagamento = Pagamento.objects.create(
            aluno=self.aluno,
            mes_referencia=date(2025, 6, 1),
            valor=100,
            pago=False
        )

        # create attendance for the student
        self.presenca = Presenca.objects.create(
            aluno=self.aluno,
            data=date.today(),
            presente=True
        )

    # Dashboard
    def test_dashboard_view(self):
        url = reverse('dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/dashboard.html')
        self.assertIn('total_alunos', response.context)

    # student list
    def test_aluno_list_view(self):
        url = reverse('aluno_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/aluno_list.html')
        self.assertIn(self.aluno, response.context['alunos'])

    # Aluno create GET
    def test_aluno_create_get(self):
        url = reverse('aluno_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/aluno_form.html')

    def test_aluno_create_post_valid(self):
        url = reverse('aluno_create')
        data = {
            'nome': 'Novo Aluno',
            'telefone': '11999999999',
            'status': Aluno.ATIVO,
            'data_entrada': '2025-06-08',
            # optional fields can be omitted
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Aluno.objects.filter(nome='Novo Aluno').exists())

    def test_aluno_update_post_valid(self):
        url = reverse('aluno_update', args=[self.aluno.pk])
        data = {
            'nome': 'Aluno Atualizado',
            'telefone': '11988888888',
            'status': Aluno.ATIVO,
            'data_entrada': self.aluno.data_entrada.strftime('%Y-%m-%d'),
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.aluno.refresh_from_db()
        self.assertEqual(self.aluno.nome, 'Aluno Atualizado')
        self.assertEqual(self.aluno.telefone, '11988888888')


    # Aluno detail
    def test_aluno_detail_view(self):
        url = reverse('aluno_detail', args=[self.aluno.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/aluno_detail.html')
        self.assertEqual(response.context['aluno'], self.aluno)

    # Presenca list
    def test_presenca_list_view(self):
        url = reverse('presenca_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/presenca_list.html')
        self.assertIn(self.presenca, response.context['presencas'])

    # Presenca create GET
    def test_presenca_create_get(self):
        url = reverse('presenca_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/presenca_form.html')

    # Presenca create POST (marcar presença)
    def test_presenca_create_post(self):
        url = reverse('presenca_create')
        data = {
            'data': date.today().strftime('%d/%m/%Y'),
            'presencas': [str(self.aluno.id)],  # mark student present
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        presencas = Presenca.objects.filter(data=date.today(), aluno=self.aluno)
        self.assertTrue(presencas.exists())
        self.assertTrue(presencas.first().presente)

    # Pagamento list
    def test_pagamento_list_view(self):
        url = reverse('pagamento_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/pagamento_list.html')
        self.assertIn(self.pagamento, response.context['pagamentos'])

    # Pagamento create GET
    def test_pagamento_create_get(self):
        url = reverse('pagamento_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/pagamento_form.html')

    # Pagamento create POST válido
    def test_pagamento_create_post_valid(self):
        url = reverse('pagamento_create')
        data = {
            'aluno': self.aluno.pk,
            'mes_referencia': '2025-07-01',
            'valor': 150,
            'pago': True
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Pagamento.objects.filter(valor=150).exists())

    # Pagamento update GET
    def test_pagamento_update_get(self):
        url = reverse('pagamento_update', args=[self.pagamento.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/pagamento_form.html')

    # Pagamento update POST válido
    def test_pagamento_update_post_valid(self):
        url = reverse('pagamento_update', args=[self.pagamento.pk])
        data = {
            'aluno': self.aluno.pk,
            'mes_referencia': '2025-06-01',
            'valor': 200,
            'pago': True
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.pagamento.refresh_from_db()
        self.assertEqual(self.pagamento.valor, 200)

    # attendance report
    def test_relatorio_presenca_view(self):
        url = reverse('relatorio_presenca')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/relatorio_presenca.html')

    # payments report
    def test_relatorio_pagamentos_view(self):
        url = reverse('relatorio_pagamentos')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/relatorio_pagamentos.html')

    # messages view
    def test_mensagens_view(self):
        url = reverse('mensagens')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/mensagens.html')
