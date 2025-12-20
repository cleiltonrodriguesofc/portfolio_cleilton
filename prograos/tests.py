"""
unit tests for grain classification system
"""
import json
import io
from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch, MagicMock
from .models import Amostra, ActivityLog
from .utils import GrainCalculator
from .scale_integration import ScaleReader
from .reports import AmostrasPDFGenerator


class AmostraModelTest(TestCase):
    """tests for amostra model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
    def test_criar_amostra_soja(self):
        """tests soybean sample creation"""
        amostra = Amostra.objects.create(
            tipo_grao='SOJA',
            peso_bruto=1000.500,
            umidade=14.5,
            impurezas=2.0,
            created_by=self.user
        )
        
        self.assertEqual(amostra.tipo_grao, 'SOJA')
        self.assertEqual(amostra.peso_bruto, Decimal('1000.500'))
        self.assertEqual(amostra.umidade, Decimal('14.5'))
        self.assertEqual(amostra.impurezas, Decimal('2.0'))
        self.assertEqual(amostra.created_by, self.user)
        self.assertIsNotNone(amostra.id_amostra)
        
    def test_criar_amostra_milho(self):
        """tests corn sample creation"""
        amostra = Amostra.objects.create(
            tipo_grao='MILHO',
            peso_bruto=2000.750,
            umidade=16.0,
            impurezas=1.5,
            created_by=self.user
        )
        
        self.assertEqual(amostra.tipo_grao, 'MILHO')
        self.assertEqual(amostra.peso_bruto, Decimal('2000.750'))
        
    def test_calcular_peso_util(self):
        """tests net weight calculation"""
        amostra = Amostra.objects.create(
            tipo_grao='SOJA',
            peso_bruto=1000.0,
            umidade=14.0,
            impurezas=2.0,
            created_by=self.user
        )
        
        # Peso útil = peso - (peso * impurezas/100)
        peso_util_esperado = 1000.0 - (1000.0 * 2.0 / 100)
        if amostra.peso_util:
            self.assertEqual(float(amostra.peso_util), peso_util_esperado)
        
    def test_str_representation(self):
        """tests string representation of the model"""
        amostra = Amostra.objects.create(
            tipo_grao='SOJA',
            peso_bruto=1000.0,
            umidade=14.0,
            impurezas=2.0,
            created_by=self.user
        )
        
        expected_str = f"{amostra.id_amostra} - SOJA"
        self.assertEqual(str(amostra), expected_str)


class ActivityLogModelTest(TestCase):
    """tests for activitylog model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
    def test_criar_activity_log(self):
        """Testa criação de log de atividade"""
        log = ActivityLog.objects.create(
            user=self.user,
            action='CREATE_AMOSTRA',
            object_id='1',
            object_type='Amostra',
            details='Criou nova amostra de soja'
        )
        
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.action, 'CREATE_AMOSTRA')
        self.assertEqual(log.object_type, 'Amostra')
        self.assertIsNotNone(log.timestamp)
        
    def test_str_representation_activity_log(self):
        """Testa representação string do ActivityLog"""
        log = ActivityLog.objects.create(
            user=self.user,
            action='CREATE_AMOSTRA'
        )
        
        expected_str = f"{self.user} - CREATE_AMOSTRA at {log.timestamp}"
        self.assertEqual(str(log), expected_str)


class ClassificadorGraosTest(TestCase):
    """tests for grain classifier"""
    
    def test_classificar_soja_aceita(self):
        """tests accepted soybean classification"""
        classificador = ClassificadorGraos()
        resultado = classificador.classificar_soja(
            umidade=14.0,
            impurezas=1.0,
            peso_util=980.0
        )
        
        self.assertEqual(resultado['status'], 'ACEITA')
        self.assertIn('qualidade', resultado)
        
    def test_classificar_soja_rejeitada_umidade(self):
        """tests soybean rejected by humidity classification"""
        classificador = ClassificadorGraos()
        resultado = classificador.classificar_soja(
            umidade=16.0,  # Acima do limite
            impurezas=1.0,
            peso_util=980.0
        )
        
        self.assertEqual(resultado['status'], 'REJEITADA')
        self.assertIn('Umidade muito alta', resultado['motivo'])
        
    def test_classificar_milho_aceito(self):
        """tests accepted corn classification"""
        classificador = ClassificadorGraos()
        resultado = classificador.classificar_milho(
            umidade=15.0,
            impurezas=1.5,
            peso_util=985.0
        )
        
        self.assertEqual(resultado['status'], 'ACEITA')
        
    def test_classificar_milho_rejeitado_impurezas(self):
        """tests corn rejected by impurities classification"""
        classificador = ClassificadorGraos()
        resultado = classificador.classificar_milho(
            umidade=15.0,
            impurezas=4.0,  # Acima do limite
            peso_util=985.0
        )
        
        self.assertEqual(resultado['status'], 'REJEITADA')
        self.assertIn('Impurezas muito altas', resultado['motivo'])


class ScaleIntegrationTest(TestCase):
    """tests for scale integration"""
    
    @patch('serial.Serial')
    def test_conectar_balanca_usb(self, mock_serial):
        """tests scale connection via usb"""
        mock_connection = MagicMock()
        mock_serial.return_value = mock_connection
        
        scale_reader = ScaleReader()
        resultado = scale_reader.connect_usb('/dev/ttyUSB0')
        
        self.assertTrue(resultado)
        mock_serial.assert_called_once()
        
    @patch('serial.Serial')
    def test_ler_peso_balanca(self, mock_serial):
        """tests scale weight reading"""
        mock_connection = MagicMock()
        mock_connection.readline.return_value = b'1234.567\r\n'
        mock_serial.return_value = mock_connection
        
        scale_reader = ScaleReader()
        scale_reader.connect_usb('/dev/ttyUSB0')
        peso = scale_reader.read_weight()
        
        self.assertEqual(peso, 1234.567)
        
    @patch('serial.Serial')
    def test_erro_conexao_balanca(self, mock_serial):
        """tests error handling in scale connection"""
        mock_serial.side_effect = Exception("Porta não encontrada")
        
        scale_reader = ScaleReader()
        resultado = scale_reader.connect_usb('/dev/ttyUSB0')
        
        self.assertFalse(resultado)


class ViewsTest(TestCase):
    """tests for system views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
    def test_dashboard_view(self):
        """tests dashboard view"""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard')
        
    def test_amostra_list_view(self):
        """tests sample list view"""
        response = self.client.get(reverse('amostra_list'))
        self.assertEqual(response.status_code, 200)
        
    def test_amostra_create_view_get(self):
        """tests sample creation view (get)"""
        response = self.client.get(reverse('amostra_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nova Amostra')
        
    def test_amostra_create_view_post(self):
        """tests sample creation view (post)"""
        data = {
            'tipo_grao': 'SOJA',
            'peso_bruto': '1000.500',
            'umidade': '14.5',
            'impurezas': '2.0'
        }
        response = self.client.post(reverse('amostra_create'), data)
        self.assertEqual(response.status_code, 302)  # redirect after creation
        
        # verify sample was created
        amostra = Amostra.objects.get(tipo_grao='SOJA')
        self.assertEqual(amostra.peso_bruto, Decimal('1000.500'))
        
    def test_login_required(self):
        """tests if login is required"""
        self.client.logout()
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)  # redirect to login


class ReportsTest(TestCase):
    """tests for report generation"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
    def test_gerar_pdf_amostras(self):
        """tests pdf sample generation"""
        # Criar algumas amostras
        Amostra.objects.create(
            tipo_grao='SOJA',
            peso_bruto=1000.0,
            umidade=14.0,
            impurezas=2.0,
            created_by=self.user
        )
        
        generator = AmostrasPDFGenerator()
        amostras = Amostra.objects.all()
        pdf_content = generator.gerar_relatorio(amostras)
        
        self.assertIsInstance(pdf_content, bytes)
        self.assertTrue(len(pdf_content) > 0)


class APITest(TestCase):
    """tests for rest api"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
    def test_scale_read_endpoint(self):
        """tests scale reading endpoint"""
        with patch('prograos.scale_integration.ScaleReader.read_weight') as mock_read:
            mock_read.return_value = 1234.567
            
            response = self.client.get(reverse('scale_read'))
            self.assertEqual(response.status_code, 200)
            
            data = json.loads(response.content)
            self.assertEqual(data['peso'], 1234.567)
            
    def test_scale_ports_endpoint(self):
        """tests port listing endpoint"""
        response = self.client.get(reverse('scale_ports'))
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertIn('portas', data)
        
    def test_export_amostras_pdf(self):
        """tests pdf sample export"""
        # Criar amostra
        Amostra.objects.create(
            tipo_grao='SOJA',
            peso_bruto=1000.0,
            umidade=14.0,
            impurezas=2.0,
            created_by=self.user
        )
        
        response = self.client.get(reverse('export_amostras_pdf'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        
    def test_export_amostras_excel(self):
        """tests excel sample export"""
        # Criar amostra
        Amostra.objects.create(
            tipo_grao='SOJA',
            peso_bruto=1000.0,
            umidade=14.0,
            impurezas=2.0,
            created_by=self.user
        )
        
        response = self.client.get(reverse('export_amostras_excel'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('application/vnd.openxmlformats', response['Content-Type'])


class IntegrationTest(TestCase):
    """full system integration tests"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
    def test_fluxo_completo_amostra(self):
        """tests full sample flow"""
        # 1. create sample
        data_amostra = {
            'tipo_grao': 'SOJA',
            'peso_bruto': '1000.500',
            'umidade': '14.5',
            'impurezas': '2.0'
        }
        response = self.client.post(reverse('amostra_create'), data_amostra)
        self.assertEqual(response.status_code, 302)
        
        amostra = Amostra.objects.get(tipo_grao='SOJA')
        
        # 2. verify sample was created
        self.assertEqual(amostra.peso_bruto, Decimal('1000.500'))
        self.assertEqual(amostra.umidade, Decimal('14.5'))
        self.assertEqual(amostra.impurezas, Decimal('2.0'))
        
        # 3. export report
        response = self.client.get(reverse('export_amostras_pdf'))
        self.assertEqual(response.status_code, 200)
        
        # 4. edit sample
        data_edit = {
            'tipo_grao': 'SOJA',
            'peso_bruto': '1000.500',
            'umidade': '16.0',  # Acima do limite
            'impurezas': '2.0'
        }
        response = self.client.post(reverse('amostra_update', args=[amostra.id]), data_edit)
        self.assertEqual(response.status_code, 302)
        
        amostra.refresh_from_db()
        self.assertEqual(amostra.umidade, Decimal('16.0'))
        
    def test_sistema_auditoria(self):
        """tests audit system"""
        # Criar amostra
        data_amostra = {
            'tipo_grao': 'SOJA',
            'peso_bruto': '1000.500',
            'umidade': '14.5',
            'impurezas': '2.0'
        }
        response = self.client.post(reverse('amostra_create'), data_amostra)
        self.assertEqual(response.status_code, 302)
        
        amostra = Amostra.objects.get(tipo_grao='SOJA')
        
        # verify who created it was recorded
        self.assertEqual(amostra.created_by, self.user)
        self.assertIsNotNone(amostra.data_criacao)
        
    def test_validacoes_formulario(self):
        """tests form validations"""
        # try creating sample with invalid data
        data_invalida = {
            'tipo_grao': 'INVALIDO',
            'peso_bruto': '-100',  # Peso negativo
            'umidade': '150',  # Umidade impossível
            'impurezas': '-5'  # Impurezas negativas
        }
        response = self.client.post(reverse('amostra_create'), data_invalida)
        
        # must return validation error
        self.assertEqual(response.status_code, 200)  # returns to form
        
    def test_busca_e_filtros(self):
        """tests search and filter functionality"""
        # Criar amostras de teste
        Amostra.objects.create(
            tipo_grao='SOJA',
            peso_bruto=1000.0,
            umidade=14.0,
            impurezas=2.0,
            created_by=self.user
        )
        
        Amostra.objects.create(
            tipo_grao='MILHO',
            peso_bruto=2000.0,
            umidade=15.0,
            impurezas=1.5,
            created_by=self.user
        )
        
        # test filter by grain type
        response = self.client.get(reverse('amostra_list') + '?tipo_grao=SOJA')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'SOJA')
        
        # test search
        response = self.client.get(reverse('amostra_list') + '?search=MILHO')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'MILHO')


if __name__ == '__main__':
    import django
    from django.conf import settings
    from django.test.utils import get_runner
    
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["prograos.tests"])


class AmostraModelTest(TestCase):
    """tests for amostra model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
    def test_criar_amostra_soja(self):
        """tests soybean sample creation"""
        amostra = Amostra.objects.create(
            tipo_grao='SOJA',
            peso=1000.500,
            umidade=14.5,
            impurezas=2.0,
            created_by=self.user
        )
        
        self.assertEqual(amostra.tipo_grao, 'SOJA')
        self.assertEqual(amostra.peso, Decimal('1000.500'))
        self.assertEqual(amostra.umidade, Decimal('14.5'))
        self.assertEqual(amostra.impurezas, Decimal('2.0'))
        self.assertEqual(amostra.created_by, self.user)
        self.assertIsNotNone(amostra.id_amostra)
        
    def test_criar_amostra_milho(self):
        """tests corn sample creation"""
        amostra = Amostra.objects.create(
            tipo_grao='MILHO',
            peso=2000.750,
            umidade=16.0,
            impurezas=1.5,
            created_by=self.user
        )
        
        self.assertEqual(amostra.tipo_grao, 'MILHO')
        self.assertEqual(amostra.peso, Decimal('2000.750'))
        
    def test_calcular_peso_util(self):
        """tests net weight calculation"""
        amostra = Amostra.objects.create(
            tipo_grao='SOJA',
            peso=1000.0,
            umidade=14.0,
            impurezas=2.0,
            created_by=self.user
        )
        
        # net weight = weight - (weight * impurities/100)
        self.assertEqual(float(amostra.peso_util), peso_util_esperado)
        
    def test_str_representation(self):
        """tests string representation of the model"""
        amostra = Amostra.objects.create(
            tipo_grao='SOJA',
            peso=1000.0,
            umidade=14.0,
            impurezas=2.0,
            created_by=self.user
        )
        
        expected_str = f"Amostra {amostra.id_amostra} - SOJA"
        self.assertEqual(str(amostra), expected_str)


class PesagemCaminhaoModelTest(TestCase):
    """tests for pesagemcaminhao model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
    def test_criar_pesagem_caminhao(self):
        """tests truck weighing creation"""
        pesagem = PesagemCaminhao.objects.create(
            placa='ABC-1234',
            tara=15000.0,
            peso_carregado=45000.0,
            tipo_grao='SOJA',
            created_by=self.user
        )
        
        self.assertEqual(pesagem.placa, 'ABC-1234')
        self.assertEqual(pesagem.tara, Decimal('15000.0'))
        self.assertEqual(pesagem.peso_carregado, Decimal('45000.0'))
        self.assertEqual(pesagem.tipo_grao, 'SOJA')
        
    def test_calcular_peso_liquido(self):
        """tests automatic net weight calculation"""
        pesagem = PesagemCaminhao.objects.create(
            placa='ABC-1234',
            tara=15000.0,
            peso_carregado=45000.0,
            tipo_grao='SOJA',
            created_by=self.user
        )
        
        peso_liquido_esperado = 45000.0 - 15000.0
        self.assertEqual(float(pesagem.peso_liquido), peso_liquido_esperado)
        
    def test_calcular_quantidade_sacos(self):
        """tests automatic bag quantity calculation"""
        pesagem = PesagemCaminhao.objects.create(
            placa='ABC-1234',
            tara=15000.0,
            peso_carregado=45000.0,
            tipo_grao='SOJA',
            created_by=self.user
        )
        
        peso_liquido = 30000.0  # 45000 - 15000
        quantidade_sacos_esperada = peso_liquido / 60.0  # 500 bags
        self.assertEqual(float(pesagem.quantidade_sacos), quantidade_sacos_esperada)
        
    def test_validacao_peso_carregado_maior_que_tara(self):
        """tests validation of loaded weight greater than tare"""
        with self.assertRaises(Exception):
            pesagem = PesagemCaminhao.objects.create(
                placa='ABC-1234',
                tara=45000.0,  # tare greater than loaded weight
                peso_carregado=15000.0,
                tipo_grao='SOJA',
                created_by=self.user
            )
            pesagem.full_clean()


class NotaCarregamentoModelTest(TestCase):
    """tests for notacarregamento model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.pesagem = PesagemCaminhao.objects.create(
            placa='ABC-1234',
            tara=15000.0,
            peso_carregado=45000.0,
            tipo_grao='SOJA',
            created_by=self.user
        )
        
    def test_criar_nota_carregamento(self):
        """tests loading note creation"""
        nota = NotaCarregamento.objects.create(
            pesagem_caminhao=self.pesagem,
            nome_recebedor='João Silva',
            cpf_cnpj_recebedor='123.456.789-00',
            telefone_recebedor='(11) 99999-9999',
            endereco_recebedor='Rua das Flores, 123',
            preco_por_saco=50.00,
            created_by=self.user
        )
        
        self.assertEqual(nota.nome_recebedor, 'João Silva')
        self.assertEqual(nota.cpf_cnpj_recebedor, '123.456.789-00')
        self.assertIsNotNone(nota.numero_nota)
        
    def test_calcular_valor_total(self):
        """tests automatic total value calculation"""
        nota = NotaCarregamento.objects.create(
            pesagem_caminhao=self.pesagem,
            nome_recebedor='João Silva',
            cpf_cnpj_recebedor='123.456.789-00',
            endereco_recebedor='Rua das Flores, 123',
            preco_por_saco=50.00,
            created_by=self.user
        )
        
        # total value = bag_quantity * price_per_bag
        valor_esperado = float(self.pesagem.quantidade_sacos) * 50.00
        self.assertEqual(float(nota.valor_total), valor_esperado)
        
    def test_gerar_numero_nota_unico(self):
        """tests unique note number generation"""
        nota1 = NotaCarregamento.objects.create(
            pesagem_caminhao=self.pesagem,
            nome_recebedor='João Silva',
            cpf_cnpj_recebedor='123.456.789-00',
            endereco_recebedor='Rua das Flores, 123',
            created_by=self.user
        )
        
        # create second weighing for second note
        pesagem2 = PesagemCaminhao.objects.create(
            placa='DEF-5678',
            tara=16000.0,
            peso_carregado=46000.0,
            tipo_grao='MILHO',
            created_by=self.user
        )
        
        nota2 = NotaCarregamento.objects.create(
            pesagem_caminhao=pesagem2,
            nome_recebedor='Maria Santos',
            cpf_cnpj_recebedor='987.654.321-00',
            endereco_recebedor='Av. Principal, 456',
            created_by=self.user
        )
        
        self.assertNotEqual(nota1.numero_nota, nota2.numero_nota)


class ClassificadorGraosTest(TestCase):
    """tests for grain classifier"""
    
    def test_classificar_soja_aceita(self):
        """tests accepted soybean classification"""
        classificador = ClassificadorGraos()
        resultado = classificador.classificar_soja(
            umidade=14.0,
            impurezas=1.0,
            peso_util=980.0
        )
        
        self.assertEqual(resultado['status'], 'ACEITA')
        self.assertIn('qualidade', resultado)
        
    def test_classificar_soja_rejeitada_umidade(self):
        """tests rejected soybean classification due to moisture"""
        classificador = ClassificadorGraos()
        resultado = classificador.classificar_soja(
            umidade=16.0,  # above limit
            impurezas=1.0,
            peso_util=980.0
        )
        
        self.assertEqual(resultado['status'], 'REJEITADA')
        self.assertIn('Umidade muito alta', resultado['motivo'])
        
    def test_classificar_milho_aceito(self):
        """tests accepted corn classification"""
        classificador = ClassificadorGraos()
        resultado = classificador.classificar_milho(
            umidade=15.0,
            impurezas=1.5,
            peso_util=985.0
        )
        
        self.assertEqual(resultado['status'], 'ACEITA')
        
    def test_classificar_milho_rejeitado_impurezas(self):
        """tests rejected corn classification due to impurities"""
        classificador = ClassificadorGraos()
        resultado = classificador.classificar_milho(
            umidade=15.0,
            impurezas=4.0,  # above limit
            peso_util=985.0
        )
        
        self.assertEqual(resultado['status'], 'REJEITADA')
        self.assertIn('Impurezas muito altas', resultado['motivo'])


class ScaleIntegrationTest(TestCase):
    """tests for scale integration"""
    
    @patch('serial.Serial')
    def test_conectar_balanca_usb(self, mock_serial):
        """tests scale connection via usb"""
        mock_connection = MagicMock()
        mock_serial.return_value = mock_connection
        
        scale_reader = ScaleReader()
        resultado = scale_reader.connect_usb('/dev/ttyUSB0')
        
        self.assertTrue(resultado)
        mock_serial.assert_called_once()
        
    @patch('serial.Serial')
    def test_ler_peso_balanca(self, mock_serial):
        """tests scale weight reading"""
        mock_connection = MagicMock()
        mock_connection.readline.return_value = b'1234.567\r\n'
        mock_serial.return_value = mock_connection
        
        scale_reader = ScaleReader()
        scale_reader.connect_usb('/dev/ttyUSB0')
        peso = scale_reader.read_weight()
        
        self.assertEqual(peso, 1234.567)
        
    @patch('serial.Serial')
    def test_erro_conexao_balanca(self, mock_serial):
        """tests error handling in scale connection"""
        mock_serial.side_effect = Exception("Porta não encontrada")
        
        scale_reader = ScaleReader()
        resultado = scale_reader.connect_usb('/dev/ttyUSB0')
        
        self.assertFalse(resultado)


class ViewsTest(TestCase):
    """tests for system views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
    def test_dashboard_view(self):
        """tests dashboard view"""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard')
        
    def test_amostra_list_view(self):
        """tests sample list view"""
        response = self.client.get(reverse('amostra_list'))
        self.assertEqual(response.status_code, 200)
        
    def test_amostra_create_view_get(self):
        """tests sample creation view (get)"""
        response = self.client.get(reverse('amostra_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nova Amostra')
        
    def test_amostra_create_view_post(self):
        """tests sample creation view (post)"""
        data = {
            'tipo_grao': 'SOJA',
            'peso': '1000.500',
            'umidade': '14.5',
            'impurezas': '2.0'
        }
        response = self.client.post(reverse('amostra_create'), data)
        self.assertEqual(response.status_code, 302)  # redirect after creation
        
        # verify if sample was created
        amostra = Amostra.objects.get(tipo_grao='SOJA')
        self.assertEqual(amostra.peso, Decimal('1000.500'))
        
    def test_pesagem_create_view_post(self):
        """tests weighing creation view"""
        data = {
            'placa': 'ABC-1234',
            'tara': '15000.0',
            'peso_carregado': '45000.0',
            'tipo_grao': 'SOJA'
        }
        response = self.client.post(reverse('pesagem_create'), data)
        self.assertEqual(response.status_code, 302)
        
        # verify if weighing was created
        pesagem = PesagemCaminhao.objects.get(placa='ABC-1234')
        self.assertEqual(pesagem.peso_liquido, Decimal('30000.0'))
        
    def test_nota_create_view_post(self):
        """tests loading note creation view"""
        # create weighing first
        pesagem = PesagemCaminhao.objects.create(
            placa='ABC-1234',
            tara=15000.0,
            peso_carregado=45000.0,
            tipo_grao='SOJA',
            created_by=self.user
        )
        
        data = {
            'pesagem_caminhao': pesagem.id,
            'nome_recebedor': 'João Silva',
            'cpf_cnpj_recebedor': '123.456.789-00',
            'endereco_recebedor': 'Rua das Flores, 123',
            'preco_por_saco': '50.00'
        }
        response = self.client.post(reverse('nota_create'), data)
        self.assertEqual(response.status_code, 302)
        
        # verify if note was created
        nota = NotaCarregamento.objects.get(nome_recebedor='João Silva')
        self.assertIsNotNone(nota.numero_nota)
        
    def test_login_required(self):
        """tests if login is required"""
        self.client.logout()
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)  # redirect to login


class ReportsTest(TestCase):
    """tests for report generation"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
    def test_gerar_pdf_amostras(self):
        """tests sample pdf generation"""
        # Criar algumas amostras
        Amostra.objects.create(
            tipo_grao='SOJA',
            peso=1000.0,
            umidade=14.0,
            impurezas=2.0,
            created_by=self.user
        )
        
        generator = AmostrasPDFGenerator()
        amostras = Amostra.objects.all()
        pdf_content = generator.gerar_relatorio(amostras)
        
        self.assertIsInstance(pdf_content, bytes)
        self.assertTrue(len(pdf_content) > 0)
        
    def test_gerar_pdf_nota_carregamento(self):
        """tests loading note pdf generation"""
        # create weighing and note
        pesagem = PesagemCaminhao.objects.create(
            placa='ABC-1234',
            tara=15000.0,
            peso_carregado=45000.0,
            tipo_grao='SOJA',
            created_by=self.user
        )
        
        nota = NotaCarregamento.objects.create(
            pesagem_caminhao=pesagem,
            nome_recebedor='João Silva',
            cpf_cnpj_recebedor='123.456.789-00',
            endereco_recebedor='Rua das Flores, 123',
            preco_por_saco=50.00,
            created_by=self.user
        )
        
        generator = NotaCarregamentoPDFGenerator()
        pdf_content = generator.gerar_pdf(nota)
        
        self.assertIsInstance(pdf_content, bytes)
        self.assertTrue(len(pdf_content) > 0)


class APITest(TestCase):
    """tests for rest api"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
    def test_scale_read_endpoint(self):
        """tests scale reading endpoint"""
        with patch('prograos.scale_integration.ScaleReader.read_weight') as mock_read:
            mock_read.return_value = 1234.567
            
            response = self.client.get(reverse('scale_read'))
            self.assertEqual(response.status_code, 200)
            
            data = json.loads(response.content)
            self.assertEqual(data['peso'], 1234.567)
            
    def test_scale_ports_endpoint(self):
        """tests port listing endpoint"""
        response = self.client.get(reverse('scale_ports'))
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertIn('portas', data)
        
    def test_export_amostras_pdf(self):
        """tests sample pdf export"""
        # Criar amostra
        Amostra.objects.create(
            tipo_grao='SOJA',
            peso=1000.0,
            umidade=14.0,
            impurezas=2.0,
            created_by=self.user
        )
        
        response = self.client.get(reverse('export_amostras_pdf'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        
    def test_export_amostras_excel(self):
        """tests sample excel export"""
        # Criar amostra
        Amostra.objects.create(
            tipo_grao='SOJA',
            peso=1000.0,
            umidade=14.0,
            impurezas=2.0,
            created_by=self.user
        )
        
        response = self.client.get(reverse('export_amostras_excel'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('application/vnd.openxmlformats', response['Content-Type'])


class IntegrationTest(TestCase):
    """full system integration tests"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
    def test_fluxo_completo_pesagem_e_nota(self):
        """tests full flow: weighing -> note -> pdf"""
        # 1. create weighing
        data_pesagem = {
            'placa': 'ABC-1234',
            'tara': '15000.0',
            'peso_carregado': '45000.0',
            'tipo_grao': 'SOJA'
        }
        response = self.client.post(reverse('pesagem_create'), data_pesagem)
        self.assertEqual(response.status_code, 302)
        
        pesagem = PesagemCaminhao.objects.get(placa='ABC-1234')
        
        # 2. create loading note
        data_nota = {
            'pesagem_caminhao': pesagem.id,
            'nome_recebedor': 'João Silva',
            'cpf_cnpj_recebedor': '123.456.789-00',
            'endereco_recebedor': 'Rua das Flores, 123',
            'preco_por_saco': '50.00'
        }
        response = self.client.post(reverse('nota_create'), data_nota)
        self.assertEqual(response.status_code, 302)
        
        nota = NotaCarregamento.objects.get(nome_recebedor='João Silva')
        
        # 3. Gerar PDF da nota
        response = self.client.get(reverse('nota_pdf', args=[nota.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        
        # 4. Verificar cálculos
        self.assertEqual(pesagem.peso_liquido, Decimal('30000.0'))
        self.assertEqual(pesagem.quantidade_sacos, Decimal('500.00'))
        self.assertEqual(nota.valor_total, Decimal('25000.00'))  # 500 * 50
        
    def test_fluxo_completo_amostra(self):
        """Testa fluxo completo de amostra"""
        # 1. Criar amostra
        data_amostra = {
            'tipo_grao': 'SOJA',
            'peso': '1000.500',
            'umidade': '14.5',
            'impurezas': '2.0'
        }
        response = self.client.post(reverse('amostra_create'), data_amostra)
        self.assertEqual(response.status_code, 302)
        
        amostra = Amostra.objects.get(tipo_grao='SOJA')
        
        # 2. Verificar cálculos automáticos
        self.assertEqual(amostra.peso_util, Decimal('980.490'))  # 1000.5 - (1000.5 * 0.02)
        self.assertEqual(amostra.status, 'ACEITA')  # Dentro dos parâmetros
        
        # 3. Exportar relatório
        response = self.client.get(reverse('export_amostras_pdf'))
        self.assertEqual(response.status_code, 200)
        
        # 4. Editar amostra
        data_edit = {
            'tipo_grao': 'SOJA',
            'peso': '1000.500',
            'umidade': '16.0',  # Acima do limite
            'impurezas': '2.0'
        }
        response = self.client.post(reverse('amostra_update', args=[amostra.id]), data_edit)
        self.assertEqual(response.status_code, 302)
        
        amostra.refresh_from_db()
        self.assertEqual(amostra.status, 'REJEITADA')  # Umidade alta


if __name__ == '__main__':
    import django
    from django.conf import settings
    from django.test.utils import get_runner
    
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["prograos.tests"])

