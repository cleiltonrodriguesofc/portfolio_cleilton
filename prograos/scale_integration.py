import serial
import time
import json
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

class ScaleIntegration:
    """
    Classe para integração com balança digital via USB/Serial.
    """
    
    def __init__(self, port='/dev/ttyUSB0', baudrate=9600, timeout=5):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.connection = None
    
    def connect(self):
        """
        Estabelece conexão com a balança.
        
        Returns:
            bool: True se conectado com sucesso, False caso contrário
        """
        try:
            self.connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            time.sleep(2)  # Aguarda estabilização da conexão
            return True
        except Exception as e:
            print(f"Erro ao conectar com a balança: {e}")
            return False
    
    def disconnect(self):
        """
        Fecha a conexão com a balança.
        """
        if self.connection and self.connection.is_open:
            self.connection.close()
    
    def read_weight(self):
        """
        Lê o peso da balança.
        
        Returns:
            float: Peso lido da balança ou None em caso de erro
        """
        if not self.connection or not self.connection.is_open:
            return None
        
        try:
            # Envia comando para solicitar peso (pode variar conforme o modelo da balança)
            self.connection.write(b'W\\r\\n')
            time.sleep(1)
            
            # Lê a resposta
            response = self.connection.readline().decode('utf-8').strip()
            
            # Processa a resposta (formato pode variar conforme o modelo)
            # Exemplo: "W 1.234 kg" -> extrair 1.234
            if response:
                # Remove caracteres não numéricos exceto ponto e vírgula
                weight_str = ''.join(c for c in response if c.isdigit() or c in '.,')
                weight_str = weight_str.replace(',', '.')
                
                if weight_str:
                    return float(weight_str)
            
            return None
            
        except Exception as e:
            print(f"Erro ao ler peso da balança: {e}")
            return None
    
    def get_available_ports(self):
        """
        Lista as portas seriais disponíveis.
        
        Returns:
            list: Lista de portas disponíveis
        """
        import serial.tools.list_ports
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_scale_ports(request):
    """
    Lista as portas seriais disponíveis para conexão com balança.
    """
    scale = ScaleIntegration()
    ports = scale.get_available_ports()
    return Response({'available_ports': ports})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def read_scale_weight(request):
    """
    Lê o peso da balança conectada.
    
    Body:
    {
        "port": "/dev/ttyUSB0",  # opcional, usa padrão se não informado
        "baudrate": 9600         # opcional, usa padrão se não informado
    }
    """
    port = request.data.get('port', '/dev/ttyUSB0')
    baudrate = request.data.get('baudrate', 9600)
    
    scale = ScaleIntegration(port=port, baudrate=baudrate)
    
    if not scale.connect():
        return Response(
            {'error': f'Não foi possível conectar com a balança na porta {port}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        weight = scale.read_weight()
        
        if weight is not None:
            return Response({
                'weight': weight,
                'unit': 'kg',
                'port': port,
                'timestamp': time.time()
            })
        else:
            return Response(
                {'error': 'Não foi possível ler o peso da balança'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    finally:
        scale.disconnect()

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_scale_connection(request):
    """
    Testa a conexão com a balança.
    
    Body:
    {
        "port": "/dev/ttyUSB0",  # opcional
        "baudrate": 9600         # opcional
    }
    """
    port = request.data.get('port', '/dev/ttyUSB0')
    baudrate = request.data.get('baudrate', 9600)
    
    scale = ScaleIntegration(port=port, baudrate=baudrate)
    
    if scale.connect():
        scale.disconnect()
        return Response({
            'success': True,
            'message': f'Conexão com a balança estabelecida com sucesso na porta {port}'
        })
    else:
        return Response({
            'success': False,
            'message': f'Falha ao conectar com a balança na porta {port}'
        }, status=status.HTTP_400_BAD_REQUEST)

