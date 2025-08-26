from django.shortcuts import render, redirect, get_object_or_404
from .models import Usuario
from .forms import UsuarioForm, LoginForm, AlterarSenhaForm, CriarAdminInicialForm, FiltroUsuarioForm
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json


def _validar_senha(senha: str) -> list[str]:
    erros = []
    if not senha:
        erros.append('Informe uma senha.')
        return erros

    if len(senha) < 8:
        erros.append('A senha deve ter pelo menos 8 caracteres.')
    if not any(c.isdigit() for c in senha):
        erros.append('A senha deve ter pelo menos um número.')
    if not any(c.isalpha() for c in senha):
        erros.append('A senha deve ter pelo menos uma letra.')
    if not any(c.isupper() for c in senha):
        erros.append('A senha deve ter pelo menos uma letra maiúscula.')
    if not any(c.islower() for c in senha):
        erros.append('A senha deve ter pelo menos uma letra minúscula.')
    # caractere especial = não alfanumérico
    if not any(not c.isalnum() for c in senha):
        erros.append('A senha deve ter pelo menos um caractere especial.')

    return erros




def create(requests):
    if requests.method == 'GET':
        # Busca usuário logado (simulado - você pode implementar autenticação real)
        usuario_logado_id = requests.session.get('usuario_logado_id')
        if usuario_logado_id:
            usuario_logado = get_object_or_404(Usuario, id=usuario_logado_id)
            # Se for admin, mostra todos. Se for gerente, mostra só suas subcontas
            if usuario_logado.tipo == 'admin':
                usuarios = Usuario.objects.filter(ativo=True)
            else:
                usuarios = usuario_logado.get_todas_subcontas()
        else:
            usuarios = Usuario.objects.filter(ativo=True)
        
        return render(requests, 'create.html', {
            'Usuarios': usuarios,
            'usuario_logado': usuario_logado if usuario_logado_id else None
        })
    
    elif requests.method == 'POST':
        nome = requests.POST.get('nome')
        email = requests.POST.get('email')
        senha = requests.POST.get('senha')
        foto = requests.FILES.get('foto')
        tipo = requests.POST.get('tipo', 'usuario')
        
        # Verifica se há usuário logado
        usuario_logado_id = requests.session.get('usuario_logado_id')
        if not usuario_logado_id:
            messages.error(requests, 'Você precisa estar logado para criar usuários.')
            return redirect('create')
        
        usuario_logado = get_object_or_404(Usuario, id=usuario_logado_id)
        
        # Verifica permissões
        if not usuario_logado.pode_criar_subcontas():
            messages.error(requests, 'Você não tem permissão para criar usuários.')
            return redirect('create')
        
        erros = _validar_senha(senha)
        if erros:
            contexto = {
                'Usuarios': usuario_logado.get_todas_subcontas(),
                'erros': erros,
                'val_nome': nome,
                'val_email': email,
                'usuario_logado': usuario_logado
            }
            return render(requests, 'create.html', contexto)
        
        # Cria o usuário
        usuario = Usuario(
            nome=nome,
            email=email,
            senha=senha,
            foto=foto,
            tipo=tipo,
            conta_principal=usuario_logado,
            criado_por=usuario_logado
        )
        usuario.save()
        
        messages.success(requests, f'Usuário {nome} criado com sucesso!')
        return redirect('create')
                
      
      
      
      
                
def alterar_senha(request, id):
    usuario = get_object_or_404(Usuario, id=id)

    if request.method == 'GET':
        return render(request, 'alterar_senha.html', {'usuario': usuario})

    elif request.method == 'POST':
        senha = request.POST.get('senha', '')
        erros = _validar_senha(senha)

        if erros:
            return render(request, 'alterar_senha.html', {'usuario': usuario, 'erros': erros})

        usuario.senha = senha
        usuario.save()
        messages.success(request, 'Senha alterada com sucesso!')
        return redirect('create')


def login(request):
    """View para login de usuário"""
    if request.method == 'GET':
        form = LoginForm()
        return render(request, 'login.html', {'form': form})
    
    elif request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            senha = form.cleaned_data['senha']
            
            try:
                usuario = Usuario.objects.get(email=email, ativo=True)
                if usuario.verificar_senha(senha):
                    request.session['usuario_logado_id'] = usuario.id
                    messages.success(request, f'Bem-vindo, {usuario.nome}!')
                    return redirect('create')
                else:
                    messages.error(request, 'Senha incorreta.')
            except Usuario.DoesNotExist:
                messages.error(request, 'Usuário não encontrado.')
        
        return render(request, 'login.html', {'form': form})


def logout(request):
    """View para logout"""
    if 'usuario_logado_id' in request.session:
        del request.session['usuario_logado_id']
    messages.success(request, 'Logout realizado com sucesso!')
    return redirect('create')


def gerenciar_subcontas(request):
    """View para gerenciar subcontas"""
    usuario_logado_id = request.session.get('usuario_logado_id')
    if not usuario_logado_id:
        messages.error(request, 'Você precisa estar logado.')
        return redirect('create')
    
    usuario_logado = get_object_or_404(Usuario, id=usuario_logado_id)
    
    if not usuario_logado.pode_criar_subcontas():
        messages.error(request, 'Você não tem permissão para gerenciar subcontas.')
        return redirect('create')
    
    subcontas = usuario_logado.get_subcontas()
    
    return render(request, 'gerenciar_subcontas.html', {
        'usuario_logado': usuario_logado,
        'subcontas': subcontas
    })


@csrf_exempt
def criar_admin_inicial(request):
    """Cria o primeiro administrador do sistema"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            nome = data.get('nome')
            email = data.get('email')
            senha = data.get('senha')
            
            if not all([nome, email, senha]):
                return JsonResponse({'erro': 'Todos os campos são obrigatórios'}, status=400)
            
            # Verifica se já existe algum usuário
            if Usuario.objects.exists():
                return JsonResponse({'erro': 'Já existe um administrador no sistema'}, status=400)
            
            erros = _validar_senha(senha)
            if erros:
                return JsonResponse({'erro': 'Senha inválida', 'detalhes': erros}, status=400)
            
            # Cria o admin inicial
            admin = Usuario(
                nome=nome,
                email=email,
                senha=senha,
                tipo='admin'
            )
            admin.save()
            
            return JsonResponse({
                'mensagem': 'Administrador criado com sucesso!',
                'id': admin.id
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'erro': 'JSON inválido'}, status=400)
        except Exception as e:
            return JsonResponse({'erro': str(e)}, status=500)
    
    return JsonResponse({'erro': 'Método não permitido'}, status=405)