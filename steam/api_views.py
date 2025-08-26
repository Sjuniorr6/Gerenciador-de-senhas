from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from functools import wraps
from .models import ContaStreaming, CompartilhamentoStreaming, HistoricoAcesso
from usuarios.models import Usuario
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


@api_view(['GET', 'POST'])
@parser_classes([JSONParser, MultiPartParser, FormParser])
@require_login
def streaming_list_create(request):
    """
    Lista todas as contas de streaming ou cria uma nova
    """
    usuario_logado = request.usuario_logado
    
    if request.method == 'GET':
        # Buscar contas do usuário e compartilhadas com ele
        contas_proprias = ContaStreaming.objects.filter(
            proprietario=usuario_logado, 
            ativo=True
        )
        
        contas_compartilhadas = ContaStreaming.objects.filter(
            compartilhado_com=usuario_logado,
            ativo=True
        )
        
        # Combinar as duas querysets
        todas_contas = list(contas_proprias) + list(contas_compartilhadas)
        
        data = []
        for conta in todas_contas:
            # Verificar se é proprietário ou compartilhado
            is_proprietario = conta.proprietario == usuario_logado
            
            data.append({
                'id': conta.id,
                'nome': conta.nome,
                'plataforma': conta.plataforma,
                'plataforma_display': conta.get_plataforma_display(),
                'email': conta.email,
                'usuario': conta.usuario,
                'foto': conta.foto.url if conta.foto else None,
                'descricao': conta.descricao,
                'status': conta.status,
                'status_display': conta.get_status_display(),
                'data_criacao': conta.data_criacao,
                'data_expiracao': conta.data_expiracao,
                'ultimo_acesso': conta.ultimo_acesso,
                'proprietario': {
                    'id': conta.proprietario.id,
                    'nome': conta.proprietario.nome,
                    'email': conta.proprietario.email,
                },
                'is_proprietario': is_proprietario,
                'pode_editar': is_proprietario or conta.compartilhado_com.filter(
                    id=usuario_logado.id
                ).first().nivel_acesso in ['acesso', 'admin'] if not is_proprietario else True,
                'pode_deletar': is_proprietario or conta.compartilhado_com.filter(
                    id=usuario_logado.id
                ).first().nivel_acesso == 'admin' if not is_proprietario else True,
            })
        
        return Response(data)
    
    elif request.method == 'POST':
        # Pega os dados do request
        nome = request.data.get('nome')
        plataforma = request.data.get('plataforma', 'netflix')
        email = request.data.get('email')
        usuario = request.data.get('usuario', '')
        senha = request.data.get('senha')
        foto = request.FILES.get('foto')
        descricao = request.data.get('descricao', '')
        status = request.data.get('status', 'ativo')
        data_expiracao = request.data.get('data_expiracao')
        
        # Validação básica
        if not nome or not email or not senha:
            return Response({
                'erro': 'Nome, email e senha são obrigatórios'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar se já existe uma conta com mesmo email e plataforma
        if ContaStreaming.objects.filter(
            email=email, 
            plataforma=plataforma, 
            proprietario=usuario_logado
        ).exists():
            return Response({
                'erro': 'Já existe uma conta com este email nesta plataforma'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Criar a conta
        try:
            conta = ContaStreaming(
                nome=nome,
                plataforma=plataforma,
                email=email,
                usuario=usuario,
                senha=senha,  # O modelo já faz o hash
                foto=foto,
                descricao=descricao,
                status=status,
                data_expiracao=data_expiracao,
                proprietario=usuario_logado
            )
            conta.save()
            
            return Response({
                'id': conta.id,
                'nome': conta.nome,
                'plataforma': conta.plataforma,
                'plataforma_display': conta.get_plataforma_display(),
                'email': conta.email,
                'usuario': conta.usuario,
                'foto': conta.foto.url if conta.foto else None,
                'descricao': conta.descricao,
                'status': conta.status,
                'status_display': conta.get_status_display(),
                'data_criacao': conta.data_criacao,
                'data_expiracao': conta.data_expiracao,
                'proprietario': {
                    'id': conta.proprietario.id,
                    'nome': conta.proprietario.nome,
                    'email': conta.proprietario.email,
                },
                'is_proprietario': True,
                'pode_editar': True,
                'pode_deletar': True,
                'mensagem': 'Conta de streaming criada com sucesso'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'erro': 'Erro ao criar conta de streaming',
                'detalhes': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'PUT', 'DELETE'])
@parser_classes([JSONParser, MultiPartParser, FormParser])
@require_login
def streaming_detail(request, pk):
    """
    Retorna, atualiza ou deleta uma conta de streaming específica
    """
    usuario_logado = request.usuario_logado
    
    try:
        conta = get_object_or_404(ContaStreaming, pk=pk, ativo=True)
    except ContaStreaming.DoesNotExist:
        return Response({
            'erro': 'Conta de streaming não encontrada'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Verificar se o usuário pode acessar esta conta
    if not conta.pode_ser_acessada_por(usuario_logado):
        return Response({
            'erro': 'Você não tem permissão para acessar esta conta'
        }, status=status.HTTP_403_FORBIDDEN)
    
    is_proprietario = conta.proprietario == usuario_logado
    compartilhamento = None
    if not is_proprietario:
        compartilhamento = conta.compartilhado_com.filter(id=usuario_logado.id).first()
    
    if request.method == 'GET':
        data = {
            'id': conta.id,
            'nome': conta.nome,
            'plataforma': conta.plataforma,
            'plataforma_display': conta.get_plataforma_display(),
            'email': conta.email,
            'usuario': conta.usuario,
            'senha': conta.get_senha_plana(),  # Senha descriptografada
            'foto': conta.foto.url if conta.foto else None,
            'descricao': conta.descricao,
            'status': conta.status,
            'status_display': conta.get_status_display(),
            'data_criacao': conta.data_criacao,
            'data_expiracao': conta.data_expiracao,
            'ultimo_acesso': conta.ultimo_acesso,
            'proprietario': {
                'id': conta.proprietario.id,
                'nome': conta.proprietario.nome,
                'email': conta.proprietario.email,
            },
            'is_proprietario': is_proprietario,
            'pode_editar': is_proprietario or (compartilhamento and compartilhamento.pode_editar()),
            'pode_deletar': is_proprietario or (compartilhamento and compartilhamento.pode_deletar()),
        }
        return Response(data)
    
    elif request.method == 'PUT':
        # Verificar permissões de edição
        if not is_proprietario and not (compartilhamento and compartilhamento.pode_editar()):
            return Response({
                'erro': 'Você não tem permissão para editar esta conta'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Atualizar campos
        if 'nome' in request.data:
            conta.nome = request.data['nome']
        if 'plataforma' in request.data:
            conta.plataforma = request.data['plataforma']
        if 'email' in request.data:
            conta.email = request.data['email']
        if 'usuario' in request.data:
            conta.usuario = request.data['usuario']
        if 'senha' in request.data:
            conta.senha = request.data['senha']  # O modelo já faz o hash
        if 'descricao' in request.data:
            conta.descricao = request.data['descricao']
        if 'status' in request.data:
            conta.status = request.data['status']
        if 'data_expiracao' in request.data:
            conta.data_expiracao = request.data['data_expiracao']
        
        # Atualizar foto se fornecida
        if 'foto' in request.FILES:
            conta.foto = request.FILES['foto']
        
        conta.save()
        
        return Response({
            'id': conta.id,
            'nome': conta.nome,
            'plataforma': conta.plataforma,
            'plataforma_display': conta.get_plataforma_display(),
            'email': conta.email,
            'usuario': conta.usuario,
            'foto': conta.foto.url if conta.foto else None,
            'descricao': conta.descricao,
            'status': conta.status,
            'status_display': conta.get_status_display(),
            'data_expiracao': conta.data_expiracao,
            'mensagem': 'Conta de streaming atualizada com sucesso'
        })
    
    elif request.method == 'DELETE':
        # Verificar permissões de exclusão
        if not is_proprietario and not (compartilhamento and compartilhamento.pode_deletar()):
            return Response({
                'erro': 'Você não tem permissão para deletar esta conta'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Soft delete (marcar como inativo)
        conta.ativo = False
        conta.save()
        
        return Response({
            'mensagem': 'Conta de streaming deletada com sucesso'
        }, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@parser_classes([JSONParser])
@require_login
def streaming_compartilhar(request, pk):
    """
    Compartilha uma conta de streaming com outro usuário
    """
    usuario_logado = request.usuario_logado
    
    try:
        conta = get_object_or_404(ContaStreaming, pk=pk, ativo=True)
    except ContaStreaming.DoesNotExist:
        return Response({
            'erro': 'Conta de streaming não encontrada'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Apenas o proprietário pode compartilhar
    if conta.proprietario != usuario_logado:
        return Response({
            'erro': 'Apenas o proprietário pode compartilhar esta conta'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Dados do compartilhamento
    email_usuario = request.data.get('email')
    nivel_acesso = request.data.get('nivel_acesso', 'leitura')
    
    if not email_usuario:
        return Response({
            'erro': 'Email do usuário é obrigatório'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Buscar usuário
    try:
        usuario_compartilhar = Usuario.objects.get(email=email_usuario, ativo=True)
    except Usuario.DoesNotExist:
        return Response({
            'erro': 'Usuário não encontrado'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Não pode compartilhar consigo mesmo
    if usuario_compartilhar == usuario_logado:
        return Response({
            'erro': 'Você não pode compartilhar uma conta consigo mesmo'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Verificar se já está compartilhada
    if conta.compartilhado_com.filter(id=usuario_compartilhar.id).exists():
        return Response({
            'erro': 'Esta conta já está compartilhada com este usuário'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Criar compartilhamento
    try:
        compartilhamento = conta.adicionar_compartilhamento(usuario_compartilhar, nivel_acesso)
        
        return Response({
            'id': compartilhamento.id,
            'conta': {
                'id': conta.id,
                'nome': conta.nome,
                'plataforma': conta.get_plataforma_display(),
            },
            'usuario': {
                'id': usuario_compartilhar.id,
                'nome': usuario_compartilhar.nome,
                'email': usuario_compartilhar.email,
            },
            'nivel_acesso': compartilhamento.nivel_acesso,
            'data_compartilhamento': compartilhamento.data_compartilhamento,
            'mensagem': 'Conta compartilhada com sucesso'
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'erro': 'Erro ao compartilhar conta',
            'detalhes': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@require_login
def streaming_descompartilhar(request, pk, usuario_id):
    """
    Remove o compartilhamento de uma conta com um usuário
    """
    usuario_logado = request.usuario_logado
    
    try:
        conta = get_object_or_404(ContaStreaming, pk=pk, ativo=True)
    except ContaStreaming.DoesNotExist:
        return Response({
            'erro': 'Conta de streaming não encontrada'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Apenas o proprietário pode remover compartilhamento
    if conta.proprietario != usuario_logado:
        return Response({
            'erro': 'Apenas o proprietário pode remover compartilhamentos'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        usuario_remover = Usuario.objects.get(id=usuario_id, ativo=True)
    except Usuario.DoesNotExist:
        return Response({
            'erro': 'Usuário não encontrado'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Verificar se está compartilhada
    if not conta.compartilhado_com.filter(id=usuario_remover.id).exists():
        return Response({
            'erro': 'Esta conta não está compartilhada com este usuário'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Remover compartilhamento
    conta.remover_compartilhamento(usuario_remover)
    
    return Response({
        'mensagem': 'Compartilhamento removido com sucesso'
    }, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@require_login
def streaming_plataformas(request):
    """
    Retorna lista de plataformas disponíveis
    """
    plataformas = []
    for choice in ContaStreaming.PLATAFORMAS_CHOICES:
        plataformas.append({
            'codigo': choice[0],
            'nome': choice[1]
        })
    
    return Response(plataformas)


@api_view(['GET'])
@require_login
def streaming_status(request):
    """
    Retorna lista de status disponíveis
    """
    status_list = []
    for choice in ContaStreaming.STATUS_CHOICES:
        status_list.append({
            'codigo': choice[0],
            'nome': choice[1]
        })
    
    return Response(status_list)
