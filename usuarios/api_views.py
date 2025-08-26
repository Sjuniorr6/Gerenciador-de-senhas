from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from functools import wraps
from .models import Usuario
from .views import _validar_senha
from django.contrib.auth.hashers import make_password
import json


# Decorator para verificar se usuário está logado
def require_login(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
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
            request.session.flush()
            return JsonResponse({
                'error': 'Sessão inválida',
                'message': 'Usuário não encontrado ou inativo'
            }, status=401)
        
        return view_func(request, *args, **kwargs)
    return wrapper


# Decorator para verificar permissões
def require_permission(permission_type):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not hasattr(request, 'usuario_logado'):
                return JsonResponse({
                    'error': 'Usuário não autenticado'
                }, status=401)
            
            usuario = request.usuario_logado
            
            if permission_type == 'admin' and usuario.tipo != 'admin':
                return JsonResponse({
                    'error': 'Acesso negado',
                    'message': 'Apenas administradores podem acessar este recurso'
                }, status=403)
            
            elif permission_type == 'gerente' and usuario.tipo not in ['admin', 'gerente']:
                return JsonResponse({
                    'error': 'Acesso negado',
                    'message': 'Apenas gerentes e administradores podem acessar este recurso'
                }, status=403)
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


@api_view(['GET', 'POST'])
@parser_classes([JSONParser, MultiPartParser, FormParser])
@require_login
def usuario_list_create(request):
    """
    Lista todos os usuários ou cria um novo usuário
    """
    if request.method == 'GET':
        # Busca usuário logado (simulado)
        usuario_logado_id = request.session.get('usuario_logado_id')
        
        if usuario_logado_id:
            usuario_logado = get_object_or_404(Usuario, id=usuario_logado_id)
            if usuario_logado.tipo == 'admin':
                usuarios = Usuario.objects.filter(ativo=True)
            else:
                usuarios = usuario_logado.get_todas_subcontas()
        else:
            usuarios = Usuario.objects.filter(ativo=True)
        
        data = []
        for usuario in usuarios:
            data.append({
                'id': usuario.id,
                'nome': usuario.nome,
                'email': usuario.email,
                'tipo': usuario.tipo,
                'tipo_display': usuario.get_tipo_display(),
                'foto': usuario.foto.url if usuario.foto else None,
                'conta_principal': usuario.conta_principal.nome if usuario.conta_principal else None,
                'criado_por': usuario.criado_por.nome if usuario.criado_por else None,
                'data_criacao': usuario.data_criacao,
                'nivel_hierarquia': usuario.nivel_hierarquia,
            })
        return Response(data)
    
    elif request.method == 'POST':
        # Pega os dados do request
        nome = request.data.get('nome')
        email = request.data.get('email')
        senha = request.data.get('senha')
        foto = request.FILES.get('foto')
        tipo = request.data.get('tipo', 'usuario')
        
        # Validação básica
        if not nome or not email or not senha:
            return Response({
                'erro': 'Nome, email e senha são obrigatórios'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verifica se há usuário logado
        usuario_logado_id = request.session.get('usuario_logado_id')
        if not usuario_logado_id:
            return Response({
                'erro': 'Você precisa estar logado para criar usuários'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        usuario_logado = get_object_or_404(Usuario, id=usuario_logado_id)
        
        # Verifica permissões
        if not usuario_logado.pode_criar_subcontas():
            return Response({
                'erro': 'Você não tem permissão para criar usuários'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Validação de senha
        erros_senha = _validar_senha(senha)
        if erros_senha:
            return Response({
                'erro': 'Senha inválida',
                'detalhes': erros_senha
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verifica se email já existe
        if Usuario.objects.filter(email=email).exists():
            return Response({
                'erro': 'Email já cadastrado'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Cria o usuário
        try:
            usuario = Usuario(
                nome=nome,
                email=email,
                senha=senha,  # O modelo já faz o hash
                foto=foto,
                tipo=tipo,
                conta_principal=usuario_logado,
                criado_por=usuario_logado
            )
            usuario.save()
            
            return Response({
                'id': usuario.id,
                'nome': usuario.nome,
                'email': usuario.email,
                'tipo': usuario.tipo,
                'tipo_display': usuario.get_tipo_display(),
                'foto': usuario.foto.url if usuario.foto else None,
                'conta_principal': usuario.conta_principal.nome,
                'mensagem': 'Usuário criado com sucesso'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'erro': 'Erro ao criar usuário',
                'detalhes': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'PUT', 'DELETE'])
@parser_classes([JSONParser, MultiPartParser, FormParser])
@require_login
def usuario_detail(request, pk):
    """
    Retorna, atualiza ou deleta um usuário específico
    """
    try:
        usuario = get_object_or_404(Usuario, pk=pk)
    except Usuario.DoesNotExist:
        return Response({
            'erro': 'Usuário não encontrado'
        }, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        data = {
            'id': usuario.id,
            'nome': usuario.nome,
            'email': usuario.email,
            'foto': usuario.foto.url if usuario.foto else None,
        }
        return Response(data)
    
    elif request.method == 'PUT':
        nome = request.data.get('nome', usuario.nome)
        email = request.data.get('email', usuario.email)
        foto = request.FILES.get('foto', usuario.foto)
        
        # Verifica se email já existe (exceto para o próprio usuário)
        if email != usuario.email and Usuario.objects.filter(email=email).exists():
            return Response({
                'erro': 'Email já cadastrado'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        usuario.nome = nome
        usuario.email = email
        if foto:
            usuario.foto = foto
        usuario.save()
        
        return Response({
            'id': usuario.id,
            'nome': usuario.nome,
            'email': usuario.email,
            'foto': usuario.foto.url if usuario.foto else None,
            'mensagem': 'Usuário atualizado com sucesso'
        })
    
    elif request.method == 'DELETE':
        usuario.delete()
        return Response({
            'mensagem': 'Usuário deletado com sucesso'
        }, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@parser_classes([JSONParser, MultiPartParser, FormParser])
def alterar_senha_api(request, pk):
    """
    Altera a senha de um usuário específico
    """
    try:
        usuario = get_object_or_404(Usuario, pk=pk)
    except Usuario.DoesNotExist:
        return Response({
            'erro': 'Usuário não encontrado'
        }, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'POST':
        senha = request.data.get('senha')
        
        if not senha:
            return Response({
                'erro': 'Senha é obrigatória'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validação de senha
        erros_senha = _validar_senha(senha)
        if erros_senha:
            return Response({
                'erro': 'Senha inválida',
                'detalhes': erros_senha
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Atualiza a senha
        usuario.senha = make_password(senha)
        usuario.save()
        
        return Response({
            'mensagem': 'Senha alterada com sucesso'
        })


@api_view(['GET'])
def validar_senha_api(request):
    """
    Valida uma senha sem salvar
    """
    senha = request.GET.get('senha', '')
    erros = _validar_senha(senha)
    
    return Response({
        'valida': len(erros) == 0,
        'erros': erros
    })


@api_view(['POST'])
@parser_classes([JSONParser])
def login_api(request):
    """
    Login de usuário via API
    """
    email = request.data.get('email')
    senha = request.data.get('senha')
    
    if not email or not senha:
        return Response({
            'erro': 'Email e senha são obrigatórios'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        usuario = Usuario.objects.get(email=email, ativo=True)
        if usuario.verificar_senha(senha):
            request.session['usuario_logado_id'] = usuario.id
            return Response({
                'id': usuario.id,
                'nome': usuario.nome,
                'email': usuario.email,
                'tipo': usuario.tipo,
                'tipo_display': usuario.get_tipo_display(),
                'mensagem': 'Login realizado com sucesso'
            })
        else:
            return Response({
                'erro': 'Senha incorreta'
            }, status=status.HTTP_401_UNAUTHORIZED)
    except Usuario.DoesNotExist:
        return Response({
            'erro': 'Usuário não encontrado'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def logout_api(request):
    """
    Logout de usuário via API
    """
    if 'usuario_logado_id' in request.session:
        del request.session['usuario_logado_id']
    
    return Response({
        'mensagem': 'Logout realizado com sucesso'
    })


@api_view(['GET'])
@require_login
def subcontas_api(request):
    """
    Lista subcontas do usuário logado
    """
    usuario_logado_id = request.session.get('usuario_logado_id')
    if not usuario_logado_id:
        return Response({
            'erro': 'Você precisa estar logado'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    usuario_logado = get_object_or_404(Usuario, id=usuario_logado_id)
    
    if not usuario_logado.pode_criar_subcontas():
        return Response({
            'erro': 'Você não tem permissão para ver subcontas'
        }, status=status.HTTP_403_FORBIDDEN)
    
    subcontas = usuario_logado.get_subcontas()
    data = []
    
    for subconta in subcontas:
        data.append({
            'id': subconta.id,
            'nome': subconta.nome,
            'email': subconta.email,
            'tipo': subconta.tipo,
            'tipo_display': subconta.get_tipo_display(),
            'foto': subconta.foto.url if subconta.foto else None,
            'data_criacao': subconta.data_criacao,
            'nivel_hierarquia': subconta.nivel_hierarquia,
        })
    
    return Response(data)


@api_view(['POST'])
@parser_classes([JSONParser])
def criar_admin_inicial_api(request):
    """
    Cria o primeiro administrador do sistema via API
    """
    nome = request.data.get('nome')
    email = request.data.get('email')
    senha = request.data.get('senha')
    
    if not all([nome, email, senha]):
        return Response({
            'erro': 'Todos os campos são obrigatórios'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Verifica se já existe algum usuário
    if Usuario.objects.exists():
        return Response({
            'erro': 'Já existe um administrador no sistema'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    erros = _validar_senha(senha)
    if erros:
        return Response({
            'erro': 'Senha inválida',
            'detalhes': erros
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Cria o admin inicial
    admin = Usuario(
        nome=nome,
        email=email,
        senha=senha,
        tipo='admin'
    )
    admin.save()
    
    return Response({
        'id': admin.id,
        'nome': admin.nome,
        'email': admin.email,
        'tipo': admin.tipo,
        'mensagem': 'Administrador criado com sucesso!'
    }, status=status.HTTP_201_CREATED)
