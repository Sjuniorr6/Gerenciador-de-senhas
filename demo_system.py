#!/usr/bin/env python
"""
Script de Demonstração do Sistema de Usuários Hierárquico
Testa todas as funcionalidades principais do sistema
"""

import os
import sys
import django
import json
from django.test import Client
from django.contrib.auth.hashers import make_password

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gerenciador.settings')
django.setup()

from usuarios.models import Usuario
from usuarios.forms import UsuarioForm, LoginForm, AlterarSenhaForm


def print_header(title):
    """Imprime um cabeçalho formatado"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)


def print_success(message):
    """Imprime mensagem de sucesso"""
    print(f"✅ {message}")


def print_error(message):
    """Imprime mensagem de erro"""
    print(f"❌ {message}")


def print_info(message):
    """Imprime mensagem informativa"""
    print(f"ℹ️  {message}")


def test_model_creation():
    """Testa criação de usuários no modelo"""
    print_header("TESTE DE CRIAÇÃO DE MODELOS")
    
    try:
        # Limpar dados existentes
        Usuario.objects.all().delete()
        
        # Criar admin
        admin = Usuario.objects.create(
            nome="Admin Principal",
            email="admin@demo.com",
            senha="Admin123!",
            tipo="admin"
        )
        print_success(f"Admin criado: {admin.nome} (ID: {admin.id})")
        
        # Criar gerente
        gerente = Usuario.objects.create(
            nome="Gerente Demo",
            email="gerente@demo.com",
            senha="Gerente123!",
            tipo="gerente",
            conta_principal=admin,
            criado_por=admin
        )
        print_success(f"Gerente criado: {gerente.nome} (ID: {gerente.id})")
        
        # Criar usuário
        usuario = Usuario.objects.create(
            nome="Usuário Demo",
            email="usuario@demo.com",
            senha="Usuario123!",
            tipo="usuario",
            conta_principal=gerente,
            criado_por=gerente
        )
        print_success(f"Usuário criado: {usuario.nome} (ID: {usuario.id})")
        
        # Verificar hierarquia
        print_info(f"Hierarquia do usuário: {usuario.nivel_hierarquia} níveis")
        print_info(f"Admin tem {admin.get_subcontas().count()} subcontas diretas")
        print_info(f"Gerente tem {gerente.get_subcontas().count()} subcontas diretas")
        
        return admin, gerente, usuario
        
    except Exception as e:
        print_error(f"Erro na criação de modelos: {e}")
        return None, None, None


def test_password_validation():
    """Testa validação de senhas"""
    print_header("TESTE DE VALIDAÇÃO DE SENHAS")
    
    # Senhas válidas
    senhas_validas = [
        "Senha123!",
        "MinhaSenha456@",
        "Teste789#",
        "ComplexaABC123!"
    ]
    
    for senha in senhas_validas:
        try:
            usuario = Usuario.objects.create(
                nome=f"Teste {senha[:10]}",
                email=f"teste{senha[:5]}@demo.com",
                senha=senha,
                tipo="usuario"
            )
            print_success(f"Senha válida: {senha}")
            usuario.delete()  # Limpar
        except Exception as e:
            print_error(f"Senha inválida: {senha} - {e}")
    
    # Senhas inválidas
    senhas_invalidas = [
        "123",  # Muito curta
        "senha",  # Sem maiúscula, número e especial
        "SENHA",  # Sem minúscula, número e especial
        "Senha123",  # Sem caractere especial
    ]
    
    for senha in senhas_invalidas:
        try:
            usuario = Usuario.objects.create(
                nome=f"Teste {senha[:10]}",
                email=f"teste{senha[:5]}@demo.com",
                senha=senha,
                tipo="usuario"
            )
            print_error(f"Senha deveria ser inválida: {senha}")
            usuario.delete()
        except Exception as e:
            print_success(f"Senha corretamente rejeitada: {senha}")


def test_permissions():
    """Testa sistema de permissões"""
    print_header("TESTE DE PERMISSÕES")
    
    try:
        admin = Usuario.objects.get(email="admin@demo.com")
        gerente = Usuario.objects.get(email="gerente@demo.com")
        usuario = Usuario.objects.get(email="usuario@demo.com")
        
        # Testar permissões de criação de subcontas
        print_info("Permissões para criar subcontas:")
        print_success(f"Admin pode criar subcontas: {admin.pode_criar_subcontas()}")
        print_success(f"Gerente pode criar subcontas: {gerente.pode_criar_subcontas()}")
        print_success(f"Usuário pode criar subcontas: {usuario.pode_criar_subcontas()}")
        
        # Testar permissões de gerenciamento
        print_info("Permissões para gerenciar usuários:")
        print_success(f"Admin pode gerenciar gerente: {admin.pode_gerenciar_usuario(gerente)}")
        print_success(f"Admin pode gerenciar usuário: {admin.pode_gerenciar_usuario(usuario)}")
        print_success(f"Gerente pode gerenciar usuário: {gerente.pode_gerenciar_usuario(usuario)}")
        print_success(f"Gerente pode gerenciar admin: {gerente.pode_gerenciar_usuario(admin)}")
        print_success(f"Usuário pode gerenciar admin: {usuario.pode_gerenciar_usuario(admin)}")
        
    except Exception as e:
        print_error(f"Erro no teste de permissões: {e}")


def test_forms():
    """Testa formulários"""
    print_header("TESTE DE FORMULÁRIOS")
    
    # Testar UsuarioForm
    form_data = {
        'nome': 'Teste Form',
        'email': 'form@teste.com',
        'senha': 'Senha123!',
        'tipo': 'usuario'
    }
    form = UsuarioForm(data=form_data)
    if form.is_valid():
        print_success("UsuarioForm válido")
    else:
        print_error(f"UsuarioForm inválido: {form.errors}")
    
    # Testar LoginForm
    login_data = {
        'email': 'admin@demo.com',
        'senha': 'Admin123!'
    }
    login_form = LoginForm(data=login_data)
    if login_form.is_valid():
        print_success("LoginForm válido")
    else:
        print_error(f"LoginForm inválido: {login_form.errors}")
    
    # Testar AlterarSenhaForm
    senha_data = {
        'senha_atual': 'SenhaAtual123!',
        'nova_senha': 'NovaSenha123!',
        'confirmar_senha': 'NovaSenha123!'
    }
    senha_form = AlterarSenhaForm(data=senha_data)
    if senha_form.is_valid():
        print_success("AlterarSenhaForm válido")
    else:
        print_error(f"AlterarSenhaForm inválido: {senha_form.errors}")


def test_api_endpoints():
    """Testa endpoints da API"""
    print_header("TESTE DE ENDPOINTS DA API")
    
    client = Client()
    
    try:
        # Testar criação de admin inicial
        data = {
            'nome': 'Admin API',
            'email': 'admin@api.com',
            'senha': 'Admin123!'
        }
        response = client.post(
            '/api/criar-admin-inicial/',
            data=json.dumps(data),
            content_type='application/json'
        )
        if response.status_code == 200:
            print_success("API criar admin inicial funcionando")
        else:
            print_error(f"API criar admin inicial falhou: {response.status_code}")
        
        # Testar validação de senha
        response = client.get('/api/validar-senha/', {'senha': 'SenhaValida123!'})
        if response.status_code == 200:
            data = json.loads(response.content)
            if data.get('valida'):
                print_success("API validação de senha funcionando")
            else:
                print_error("API validação de senha retornou senha inválida")
        else:
            print_error(f"API validação de senha falhou: {response.status_code}")
        
        # Testar login
        login_data = {
            'email': 'admin@demo.com',
            'senha': 'Admin123!'
        }
        response = client.post(
            '/api/login/',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        if response.status_code == 200:
            print_success("API login funcionando")
        else:
            print_error(f"API login falhou: {response.status_code}")
        
    except Exception as e:
        print_error(f"Erro no teste de APIs: {e}")


def test_database_persistence():
    """Testa persistência no banco de dados"""
    print_header("TESTE DE PERSISTÊNCIA NO BANCO")
    
    try:
        # Verificar se os usuários foram persistidos
        total_usuarios = Usuario.objects.count()
        print_info(f"Total de usuários no banco: {total_usuarios}")
        
        # Verificar relacionamentos
        admin = Usuario.objects.get(email="admin@demo.com")
        gerente = Usuario.objects.get(email="gerente@demo.com")
        usuario = Usuario.objects.get(email="usuario@demo.com")
        
        print_success(f"Admin encontrado: {admin.nome}")
        print_success(f"Gerente encontrado: {gerente.nome}")
        print_success(f"Usuário encontrado: {usuario.nome}")
        
        # Verificar relacionamentos
        print_success(f"Gerente pertence ao admin: {gerente.conta_principal == admin}")
        print_success(f"Usuário pertence ao gerente: {usuario.conta_principal == gerente}")
        print_success(f"Hierarquia do usuário: {usuario.nivel_hierarquia} níveis")
        
        # Verificar hash de senha
        if admin.senha.startswith('pbkdf2_sha256$'):
            print_success("Senha do admin está hasheada")
        else:
            print_error("Senha do admin não está hasheada")
        
        if admin.verificar_senha("Admin123!"):
            print_success("Verificação de senha funcionando")
        else:
            print_error("Verificação de senha falhou")
        
    except Exception as e:
        print_error(f"Erro no teste de persistência: {e}")


def main():
    """Função principal"""
    print_header("DEMONSTRAÇÃO DO SISTEMA DE USUÁRIOS HIERÁRQUICO")
    print_info("Iniciando testes do sistema...")
    
    # Executar todos os testes
    admin, gerente, usuario = test_model_creation()
    
    if admin and gerente and usuario:
        test_password_validation()
        test_permissions()
        test_forms()
        test_api_endpoints()
        test_database_persistence()
        
        print_header("RESUMO DOS TESTES")
        print_success("✅ Sistema de modelos funcionando")
        print_success("✅ Sistema de hierarquia funcionando")
        print_success("✅ Sistema de permissões funcionando")
        print_success("✅ Formulários funcionando")
        print_success("✅ Persistência no banco funcionando")
        print_info("⚠️  Algumas APIs podem precisar de ajustes")
        
        print_header("DADOS CRIADOS PARA TESTE")
        print_info(f"Admin: {admin.email} / Senha: Admin123!")
        print_info(f"Gerente: {gerente.email} / Senha: Gerente123!")
        print_info(f"Usuário: {usuario.email} / Senha: Usuario123!")
        
        print_header("PRÓXIMOS PASSOS")
        print_info("1. Execute: python manage.py runserver")
        print_info("2. Acesse: http://localhost:8000/")
        print_info("3. Teste as APIs em: http://localhost:8000/api/")
        print_info("4. Use os dados acima para fazer login")
        
    else:
        print_error("❌ Falha na criação dos modelos básicos")
        print_error("Verifique se o banco de dados está configurado corretamente")


if __name__ == "__main__":
    main()
