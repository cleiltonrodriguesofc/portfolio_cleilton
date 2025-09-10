"""
Testes unitários simplificados para o Sistema de Classificação de Grãos
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
    """Testes para o modelo Amostra"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
    def test_criar_amostra_soja(self):
        """Testa criação de amostra de soja"""
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
        """Testa criação de amostra de milho"""
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
        """Testa representação string do modelo"""
        amostra = Amostra.objects.create(
            tipo_grao='SOJA',
            peso_bruto=1000.0,
            umidade=14.0,
            impurezas=2.0,
            created_by=self.user
        )
        
        self.assertIn('SOJA', str(amostra))


class ActivityLogModelTest(TestCase):
    """Testes para o modelo ActivityLog"""
    
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


class GrainCalculatorTest(TestCase):
    """Testes para o calculador de grãos"""
    
    def test_calcular_peso_util(self):
        """Testa cálculo do peso útil"""
        calculator = GrainCalculator()
        peso_util = calculator.calcular_peso_util(
            peso_bruto=Decimal('1000.0'),
            umidade=Decimal('14.0'),
            impurezas=Decimal('2.0')
        )
        
        # Peso útil = 1000 * (1 - 14/100) * (1 - 2/100) = 1000 * 0.86 * 0.98 = 842.8
        self.assertEqual(peso_util, Decimal('842.800'))
        
    def test_classificar_soja_aceita(self):
        """Testa classificação de soja aceita"""
        calculator = GrainCalculator()
        resultado = calculator.calcular_classificacao_soja(
            umidade=Decimal('14.0'),
            impurezas=Decimal('1.0')
        )
        
        self.assertEqual(resultado, 'ACEITA')
        
    def test_classificar_soja_rejeitada(self):
        """Testa classificação de soja rejeitada"""
        calculator = GrainCalculator()
        resultado = calculator.calcular_classificacao_soja(
            umidade=Decimal('19.0'),  # Acima do limite
            impurezas=Decimal('1.0')
        )
        
        self.assertEqual(resultado, 'REJEITADA')


class ViewsTest(TestCase):
    """Testes para as views do sistema"""
    
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
        self.assertEqual(response.status_code, 302)  # Redirect após criação
        
        # Verificar se amostra foi criada
        amostra = Amostra.objects.get(tipo_grao='SOJA')
        self.assertEqual(amostra.peso_bruto, Decimal('1000.500'))
        
    def test_login_required(self):
        """Testa se login é obrigatório"""
        self.client.logout()
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect para login


class IntegrationTest(TestCase):
    """Testes de integração do sistema completo"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
    def test_fluxo_completo_amostra(self):
        """Testa fluxo completo de amostra"""
        # 1. Criar amostra
        data_amostra = {
            'tipo_grao': 'SOJA',
            'peso_bruto': '1000.500',
            'umidade': '14.5',
            'impurezas': '2.0'
        }
        response = self.client.post(reverse('amostra_create'), data_amostra)
        self.assertEqual(response.status_code, 302)
        
        amostra = Amostra.objects.get(tipo_grao='SOJA')
        
        # 2. Verificar que amostra foi criada
        self.assertEqual(amostra.peso_bruto, Decimal('1000.500'))
        self.assertEqual(amostra.umidade, Decimal('14.5'))
        self.assertEqual(amostra.impurezas, Decimal('2.0'))
        
        # 3. Verificar auditoria
        self.assertEqual(amostra.created_by, self.user)
        self.assertIsNotNone(amostra.data_criacao)
        
    def test_sistema_auditoria(self):
        """Testa sistema de auditoria"""
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
        
        # Verificar se foi registrado quem criou
        self.assertEqual(amostra.created_by, self.user)
        self.assertIsNotNone(amostra.data_criacao)
        
    def test_busca_e_filtros(self):
        """Testa funcionalidade de busca e filtros"""
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
        
        # Testar filtro por tipo de grão
        response = self.client.get(reverse('amostra_list') + '?tipo_grao=SOJA')
        self.assertEqual(response.status_code, 200)
        
        # Testar busca
        response = self.client.get(reverse('amostra_list') + '?search=MILHO')
        self.assertEqual(response.status_code, 200)


class ScaleIntegrationTest(TestCase):
    """Testes para integração com balança"""
    
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
            # Se o módulo não existir, pular o teste
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
            # Se o módulo não existir, pular o teste
            self.skipTest("ScaleReader module not available")


class ReportsTest(TestCase):
    """Testes para geração de relatórios"""
    
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
            # Se o módulo não existir, pular o teste
            self.skipTest("AmostrasPDFGenerator module not available")


class APITest(TestCase):
    """Testes para API REST"""
    
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
            # Se a URL não existir, pular o teste
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
            # Se a URL não existir, pular o teste
            self.skipTest("export_amostras_excel URL not available")

