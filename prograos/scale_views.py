from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
# import serial
import time

class ScaleIntegration:
    """
    class for digital scale integration via usb/serial.
    """
    
    def __init__(self, port='/dev/ttyUSB0', baudrate=9600, timeout=5):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.connection = None
    
    def connect(self):
        """
        establishes connection with the scale.
        
        Returns:
            bool: True se conectado com sucesso, False caso contrário
        """
        try:
            self.connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            time.sleep(2)  # wait for connection stabilization
            return True
        except Exception as e:
            print(f"Erro ao conectar com a balança: {e}")
            return False
    
    def disconnect(self):
        """
        closes the connection with the scale.
        """
        if self.connection and self.connection.is_open:
            self.connection.close()
    
    def read_weight(self):
        """
        reads the weight from the scale.
        
        Returns:
            float: Peso lido da balança ou None em caso de erro
        """
        if not self.connection or not self.connection.is_open:
            return None
        
        try:
            # sends command to request weight (may vary by scale model)
            self.connection.write(b'W\r\n')
            time.sleep(1)
            
            # Lê a resposta
            response = self.connection.readline().decode('utf-8').strip()
            
            # Processa a resposta (formato pode variar conforme o modelo)
            # Exemplo: "W 1.234 kg" -> extrair 1.234
            if response:
                # remove non-numeric characters except dot and comma
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
        lists available serial ports.
        
        Returns:
            list: Lista de portas disponíveis
        """
        try:
            import serial.tools.list_ports
            ports = serial.tools.list_ports.comports()
            return [port.device for port in ports]
        except ImportError:
            # if pyserial is not installed, return common ports
            return ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyACM0', 'COM1', 'COM2', 'COM3']

@login_required
@require_http_methods(["POST"])
def read_scale_weight(request):
    """
    reads the weight from the connected scale.
    """
    try:
        data = json.loads(request.body)
        port = data.get('port', '/dev/ttyUSB0')
        baudrate = data.get('baudrate', 9600)
        
        scale = ScaleIntegration(port=port, baudrate=baudrate)
        
        if not scale.connect():
            return JsonResponse({
                'error': f'could not connect to scale on port {port}'
            }, status=400)
        
        try:
            weight = scale.read_weight()
            
            if weight is not None:
                return JsonResponse({
                    'weight': weight,
                    'unit': 'kg',
                    'port': port,
                    'timestamp': time.time()
                })
            else:
                return JsonResponse({
                    'error': 'could not read weight from scale'
                }, status=400)
        
        finally:
            scale.disconnect()
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'invalid json data'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Erro interno: {str(e)}'}, status=500)

@login_required
@require_http_methods(["GET"])
def list_scale_ports(request):
    """
    lists available serial ports for scale connection.
    """
    scale = ScaleIntegration()
    ports = scale.get_available_ports()
    return JsonResponse({'available_ports': ports})

@login_required
@require_http_methods(["POST"])
def test_scale_connection(request):
    """
    tests connection with the scale.
    """
    try:
        data = json.loads(request.body)
        port = data.get('port', '/dev/ttyUSB0')
        baudrate = data.get('baudrate', 9600)
        
        scale = ScaleIntegration(port=port, baudrate=baudrate)
        
        if scale.connect():
            scale.disconnect()
            return JsonResponse({
                'success': True,
                'message': f'Conexão com a balança estabelecida com sucesso na porta {port}'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': f'Falha ao conectar com a balança na porta {port}'
            }, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Dados JSON inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Erro interno: {str(e)}'}, status=500)

