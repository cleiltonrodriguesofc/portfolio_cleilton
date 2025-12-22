from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
# import serial
import time

from .scale_integration import ScaleIntegration

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

