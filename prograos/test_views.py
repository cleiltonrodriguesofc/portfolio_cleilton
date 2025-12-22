from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.middleware.csrf import get_token


@api_view(['GET'])
def get_csrf_token(request):
    """
    endpoint to get csrf token for tests.
    """
    token = get_token(request)
    return Response({'csrf_token': token})


@api_view(['GET'])
def health_check(request):
    """
    endpoint to verify if api is working.
    """
    return Response({
        'status': 'OK',
        'message': 'API do Sistema de Classificação de Grãos está funcionando',
        'version': '1.0.0'
    })
