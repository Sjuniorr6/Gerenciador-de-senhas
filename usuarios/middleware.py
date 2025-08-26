"""
Middleware para autenticação automática
Verifica se o usuário está logado em todas as requisições
"""

from django.http import JsonResponse
from .models import Usuario


class AuthenticationMiddleware:
    """
    Middleware para verificar autenticação em APIs
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Verificar se é uma requisição para API
        if request.path.startswith('/api/'):
            # APIs públicas que não precisam de autenticação
            public_apis = [
                '/api/login/',
                '/api/criar-admin-inicial/',
                '/api/validar-senha/',
            ]
            
            # Se não for API pública, verificar autenticação
            if request.path not in public_apis:
                usuario_id = request.session.get('usuario_logado_id')
                
                if not usuario_id:
                    return JsonResponse({
                        'error': 'Usuário não autenticado',
                        'message': 'Faça login para acessar este recurso'
                    }, status=401)
                
                try:
                    usuario = Usuario.objects.get(id=usuario_id, ativo=True)
                    request.usuario_logado = usuario
                except Usuario.DoesNotExist:
                    # Limpar sessão inválida
                    request.session.flush()
                    return JsonResponse({
                        'error': 'Sessão inválida',
                        'message': 'Usuário não encontrado ou inativo'
                    }, status=401)
        
        response = self.get_response(request)
        return response


class RateLimitMiddleware:
    """
    Middleware para limitar taxa de requisições
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Implementação básica de rate limiting
        # Em produção, use Redis ou similar
        
        if request.path.startswith('/api/'):
            # Contar requisições por sessão
            request_count = request.session.get('request_count', 0)
            last_request = request.session.get('last_request_time', 0)
            
            import time
            current_time = time.time()
            
            # Reset se passou 1 hora
            if current_time - last_request > 3600:
                request_count = 0
            
            # Limite de 100 requisições por hora
            if request_count >= 100:
                return JsonResponse({
                    'error': 'Rate limit exceeded',
                    'message': 'Máximo de 100 requisições por hora'
                }, status=429)
            
            # Incrementar contador
            request.session['request_count'] = request_count + 1
            request.session['last_request_time'] = current_time
        
        response = self.get_response(request)
        return response


class LoggingMiddleware:
    """
    Middleware para logar requisições
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Log da requisição
        if request.path.startswith('/api/'):
            import logging
            logger = logging.getLogger('api_access')
            
            usuario_id = request.session.get('usuario_logado_id', 'anonymous')
            logger.info(f"API Request: {request.method} {request.path} by user {usuario_id}")
        
        response = self.get_response(request)
        
        # Log da resposta
        if request.path.startswith('/api/'):
            import logging
            logger = logging.getLogger('api_access')
            logger.info(f"API Response: {response.status_code} for {request.path}")
        
        return response
