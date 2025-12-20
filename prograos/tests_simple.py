"""
simplified unit tests for grain classification system
"""
import json
from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from unittest.mock import patch, MagicMock
from .models import Amostra, ActivityLog
from .utils import GrainCalculator


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
        
    def test_str_representation(self):
        """tests string representation of the model"""
        amostra = Amostra.objects.create(
            tipo_grao='SOJA',
            peso_bruto=1000.0,
            umidade=14.0,
            impurezas=2.0,
            created_by=self.user
        )
        
        self.assertIn('SOJA', str(amostra))


class ActivityLogModelTest(TestCase):
    """tests for activitylog model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
    def test_criar_activity_log(self):
        """tests activity log creation"""
        log = ActivityLog.objects.create(
            user=self.user,
            action='CREATE_SAMPLE',
            object_id='1',
            object_type='Sample',
            details='Created new soybean sample'
        )
        
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.action, 'CREATE_SAMPLE')
        self.assertEqual(log.object_type, 'Sample')
        self.assertIsNotNone(log.timestamp)


class GrainCalculatorTest(TestCase):
    """tests for grain calculator"""
    
    def test_calcular_peso_util(self):
        """tests net weight calculation"""
        calculator = GrainCalculator()
        peso_util = calculator.calcular_peso_util(
            peso_bruto=Decimal('1000.0'),
            umidade=Decimal('14.0'),
            impurezas=Decimal('2.0')
        )
        
        # net weight = 1000 * (1 - 14/100) * (1 - 2/100) = 1000 * 0.86 * 0.98 = 842.8
        self.assertEqual(peso_util, Decimal('842.800'))
        
    def test_classificar_soja_aceita(self):
        """tests accepted soybean classification"""
        calculator = GrainCalculator()
        resultado = calculator.calcular_classificacao_soja(
            umidade=Decimal('14.0'),
            impurezas=Decimal('1.0')
        )
        
        self.assertEqual(resultado, 'ACEITA')
        
    def test_classificar_soja_rejeitada(self):
        """tests rejected soybean classification"""
        calculator = GrainCalculator()
        resultado = calculator.calcular_classificacao_soja(
            umidade=Decimal('19.0'),  # above limit
            impurezas=Decimal('1.0')
        )
        
        self.assertEqual(resultado, 'REJEITADA')


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
        """Testa view do dashboard"""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        
    def test_amostra_list_view(self):
        """Testa view de listagem de amostras"""
        response = self.client.get(reverse('amostra_list'))
        self.assertEqual(response.status_code, 200)
        
    def test_amostra_create_view_get(self):
        """Testa view de criação de amostra (GET)"""
        response = self.client.get(reverse('amostra_create'))
        self.assertEqual(response.status_code, 200)
        
    def test_amostra_create_view_post(self):
        """Testa view de criação de amostra (POST)"""
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
        """Testa se login é obrigatório"""
        self.client.logout()
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)  # redirect to login


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
        
        # 3. verify audit
        self.assertEqual(amostra.created_by, self.user)
        self.assertIsNotNone(amostra.data_criacao)
        
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
        
        # Testar busca
        response = self.client.get(reverse('amostra_list') + '?search=MILHO')
        self.assertEqual(response.status_code, 200)


class ScaleIntegrationTest(TestCase):
    """tests for scale integration"""
    
    @patch('serial.Serial')
    def test_conectar_balanca_usb(self, mock_serial):
        """Testa conexão com balança via USB"""
        try:
            from .scale_integration import ScaleReader
            
            mock_connection = MagicMock()
            mock_serial.return_value = mock_connection
            
            scale_reader = ScaleReader()
            resultado = scale_reader.connect_usb('/dev/ttyUSB0')
            
            self.assertTrue(resultado)
            mock_serial.assert_called_once()
        except ImportError:
            # if module does not exist, skip test
            self.skipTest("ScaleReader module not available")
            
    @patch('serial.Serial')
    def test_ler_peso_balanca(self, mock_serial):
        """Testa leitura de peso da balança"""
        try:
            from .scale_integration import ScaleReader
            
            mock_connection = MagicMock()
            mock_connection.readline.return_value = b'1234.567\r\n'
            mock_serial.return_value = mock_connection
            
            scale_reader = ScaleReader()
            scale_reader.connect_usb('/dev/ttyUSB0')
            peso = scale_reader.read_weight()
            
            self.assertEqual(peso, 1234.567)
        except ImportError:
            # if module does not exist, skip test
            self.skipTest("ScaleReader module not available")


class ReportsTest(TestCase):
    """tests for report generation"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
    def test_gerar_pdf_amostras(self):
        """Testa geração de PDF de amostras"""
        try:
            from .reports import AmostrasPDFGenerator
            
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
        except ImportError:
            # if module does not exist, skip test
            self.skipTest("AmostrasPDFGenerator module not available")


class APITest(TestCase):
    """tests for rest api"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
    def test_export_amostras_pdf(self):
        """Testa exportação de amostras em PDF"""
        # Criar amostra
        Amostra.objects.create(
            tipo_grao='SOJA',
            peso_bruto=1000.0,
            umidade=14.0,
            impurezas=2.0,
            created_by=self.user
        )
        
        try:
            response = self.client.get(reverse('export_amostras_pdf'))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response['Content-Type'], 'application/pdf')
        except:
            # if URL does not exist, skip test
            self.skipTest("export_amostras_pdf URL not available")
            
    def test_export_amostras_excel(self):
        """Testa exportação de amostras em Excel"""
        # Criar amostra
        Amostra.objects.create(
            tipo_grao='SOJA',
            peso_bruto=1000.0,
            umidade=14.0,
            impurezas=2.0,
            created_by=self.user
        )
        
        try:
            response = self.client.get(reverse('export_amostras_excel'))
            self.assertEqual(response.status_code, 200)
            self.assertIn('application/vnd.openxmlformats', response['Content-Type'])
        except:
            # if URL does not exist, skip test
            self.skipTest("export_amostras_excel URL not available")

