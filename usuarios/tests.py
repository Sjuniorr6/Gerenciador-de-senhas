from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.hashers import make_password, check_password
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from .models import Usuario
from .forms import UsuarioForm, LoginForm, AlterarSenhaForm, CriarAdminInicialForm
import json
import os


class UsuarioModelTest(TestCase):
    """Testes para o modelo Usuario"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        self.admin = Usuario.objects.create(
            nome="Admin Teste",
            email="admin@teste.com",
            senha=make_password("Admin123!"),
            tipo="admin"
        )
        
        self.gerente = Usuario.objects.create(
            nome="Gerente Teste",
            email="gerente@teste.com",
            senha=make_password("Gerente123!"),
            tipo="gerente",
            conta_principal=self.admin,
            criado_por=self.admin
        )
        
        self.usuario = Usuario.objects.create(
            nome="Usuário Teste",
            email="usuario@teste.com",
            senha=make_password("Usuario123!"),
            tipo="usuario",
            conta_principal=self.gerente,
            criado_por=self.gerente
        )

    def test_criacao_usuario(self):
        """Testa a criação básica de usuário"""
        self.assertEqual(self.admin.nome, "Admin Teste")
        self.assertEqual(self.admin.email, "admin@teste.com")
        self.assertEqual(self.admin.tipo, "admin")
        self.assertTrue(self.admin.ativo)
        self.assertIsNotNone(self.admin.data_criacao)

    def test_hash_senha_automatico(self):
        """Testa se a senha é hasheada automaticamente"""
        usuario = Usuario.objects.create(
            nome="Teste Hash",
            email="hash@teste.com",
            senha="Senha123!",
            tipo="usuario"
        )
        self.assertTrue(usuario.senha.startswith('pbkdf2_sha256$'))
        self.assertTrue(usuario.verificar_senha("Senha123!"))

    def test_verificar_senha(self):
        """Testa a verificação de senha"""
        self.assertTrue(self.admin.verificar_senha("Admin123!"))
        self.assertFalse(self.admin.verificar_senha("SenhaErrada"))

    def test_pode_criar_subcontas(self):
        """Testa permissões para criar subcontas"""
        self.assertTrue(self.admin.pode_criar_subcontas())
        self.assertTrue(self.gerente.pode_criar_subcontas())
        self.assertFalse(self.usuario.pode_criar_subcontas())

    def test_pode_gerenciar_usuario(self):
        """Testa permissões para gerenciar usuários"""
        # Admin pode gerenciar qualquer um
        self.assertTrue(self.admin.pode_gerenciar_usuario(self.gerente))
        self.assertTrue(self.admin.pode_gerenciar_usuario(self.usuario))
        
        # Gerente pode gerenciar suas subcontas
        self.assertTrue(self.gerente.pode_gerenciar_usuario(self.usuario))
        self.assertFalse(self.gerente.pode_gerenciar_usuario(self.admin))
        
        # Usuário não pode gerenciar ninguém
        self.assertFalse(self.usuario.pode_gerenciar_usuario(self.admin))
        self.assertFalse(self.usuario.pode_gerenciar_usuario(self.gerente))

    def test_get_subcontas(self):
        """Testa obtenção de subcontas diretas"""
        subcontas_admin = self.admin.get_subcontas()
        self.assertEqual(subcontas_admin.count(), 1)
        self.assertIn(self.gerente, subcontas_admin)
        
        subcontas_gerente = self.gerente.get_subcontas()
        self.assertEqual(subcontas_gerente.count(), 1)
        self.assertIn(self.usuario, subcontas_gerente)

    def test_get_todas_subcontas(self):
        """Testa obtenção de todas as subcontas (recursivo)"""
        todas_subcontas_admin = self.admin.get_todas_subcontas()
        self.assertEqual(todas_subcontas_admin.count(), 2)
        self.assertIn(self.gerente, todas_subcontas_admin)
        self.assertIn(self.usuario, todas_subcontas_admin)

    def test_hierarquia_completa(self):
        """Testa obtenção da hierarquia completa"""
        hierarquia_usuario = self.usuario.get_hierarquia_completa()
        self.assertEqual(len(hierarquia_usuario), 3)
        self.assertEqual(hierarquia_usuario[0], self.admin)
        self.assertEqual(hierarquia_usuario[1], self.gerente)
        self.assertEqual(hierarquia_usuario[2], self.usuario)

    def test_nivel_hierarquia(self):
        """Testa cálculo do nível na hierarquia"""
        self.assertEqual(self.admin.nivel_hierarquia, 0)
        self.assertEqual(self.gerente.nivel_hierarquia, 1)
        self.assertEqual(self.usuario.nivel_hierarquia, 2)

    def test_str_representation(self):
        """Testa representação string do modelo"""
        self.assertEqual(str(self.admin), "Admin Teste (Administrador)")
        self.assertEqual(str(self.gerente), "Gerente Teste (Gerente)")
        self.assertEqual(str(self.usuario), "Usuário Teste (Usuário)")


class UsuarioFormTest(TestCase):
    """Testes para os formulários"""
    
    def test_usuario_form_valid(self):
        """Testa formulário de usuário válido"""
        form_data = {
            'nome': 'Teste Form',
            'email': 'form@teste.com',
            'senha': 'Senha123!',
            'tipo': 'usuario'
        }
        form = UsuarioForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_usuario_form_invalid(self):
        """Testa formulário de usuário inválido"""
        form_data = {
            'nome': '',  # Campo obrigatório vazio
            'email': 'email_invalido',
            'senha': '123',  # Senha muito curta
            'tipo': 'tipo_invalido'
        }
        form = UsuarioForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('nome', form.errors)
        self.assertIn('email', form.errors)

    def test_login_form_valid(self):
        """Testa formulário de login válido"""
        form_data = {
            'email': 'teste@teste.com',
            'senha': 'Senha123!'
        }
        form = LoginForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_alterar_senha_form_valid(self):
        """Testa formulário de alterar senha válido"""
        form_data = {
            'senha_atual': 'SenhaAtual123!',
            'nova_senha': 'NovaSenha123!',
            'confirmar_senha': 'NovaSenha123!'
        }
        form = AlterarSenhaForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_alterar_senha_form_senhas_diferentes(self):
        """Testa formulário de alterar senha com senhas diferentes"""
        form_data = {
            'senha_atual': 'SenhaAtual123!',
            'nova_senha': 'NovaSenha123!',
            'confirmar_senha': 'SenhaDiferente123!'
        }
        form = AlterarSenhaForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)


class APITest(TestCase):
    """Testes para as APIs"""
    
    def setUp(self):
        """Configuração inicial para os testes de API"""
        self.client = Client()
        
        # Criar admin para testes
        self.admin = Usuario.objects.create(
            nome="Admin API",
            email="admin@api.com",
            senha=make_password("Admin123!"),
            tipo="admin"
        )
        
        # Criar gerente
        self.gerente = Usuario.objects.create(
            nome="Gerente API",
            email="gerente@api.com",
            senha=make_password("Gerente123!"),
            tipo="gerente",
            conta_principal=self.admin,
            criado_por=self.admin
        )

    def test_criar_admin_inicial_api(self):
        """Testa API de criação do admin inicial"""
        # Primeiro admin
        data = {
            'nome': 'Admin Inicial',
            'email': 'admin@inicial.com',
            'senha': 'Admin123!'
        }
        response = self.client.post(
            reverse('api_criar_admin_inicial'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        # Tentar criar segundo admin (deve falhar)
        response = self.client.post(
            reverse('api_criar_admin_inicial'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_login_api(self):
        """Testa API de login"""
        # Login válido
        data = {
            'email': 'admin@api.com',
            'senha': 'Admin123!'
        }
        response = self.client.post(
            reverse('api_login'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        # Login inválido
        data = {
            'email': 'admin@api.com',
            'senha': 'SenhaErrada'
        }
        response = self.client.post(
            reverse('api_login'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401)

    def test_usuario_list_create_api(self):
        """Testa API de listagem e criação de usuários"""
        # Fazer login primeiro
        session = self.client.session
        session['usuario_logado_id'] = self.admin.id
        session.save()
        
        # Listar usuários
        response = self.client.get(reverse('api_usuarios'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('usuarios', data)
        
        # Criar usuário
        novo_usuario_data = {
            'nome': 'Novo Usuário',
            'email': 'novo@usuario.com',
            'senha': 'Novo123!',
            'tipo': 'usuario'
        }
        response = self.client.post(
            reverse('api_usuarios'),
            data=json.dumps(novo_usuario_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        
        # Verificar se foi criado
        self.assertTrue(Usuario.objects.filter(email='novo@usuario.com').exists())

    def test_usuario_detail_api(self):
        """Testa API de detalhes, atualização e exclusão de usuário"""
        # Fazer login
        session = self.client.session
        session['usuario_logado_id'] = self.admin.id
        session.save()
        
        # Buscar usuário
        response = self.client.get(reverse('api_usuario_detail', args=[self.gerente.id]))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['nome'], 'Gerente API')
        
        # Atualizar usuário
        update_data = {
            'nome': 'Gerente Atualizado',
            'email': 'gerente@atualizado.com'
        }
        response = self.client.put(
            reverse('api_usuario_detail', args=[self.gerente.id]),
            data=json.dumps(update_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        # Verificar atualização
        self.gerente.refresh_from_db()
        self.assertEqual(self.gerente.nome, 'Gerente Atualizado')

    def test_alterar_senha_api(self):
        """Testa API de alteração de senha"""
        # Fazer login
        session = self.client.session
        session['usuario_logado_id'] = self.admin.id
        session.save()
        
        # Alterar senha
        data = {
            'senha_atual': 'Admin123!',
            'nova_senha': 'NovaSenha123!'
        }
        response = self.client.post(
            reverse('api_alterar_senha', args=[self.admin.id]),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        # Verificar se a senha foi alterada
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.verificar_senha('NovaSenha123!'))

    def test_validar_senha_api(self):
        """Testa API de validação de senha"""
        # Senha válida
        response = self.client.get(
            reverse('api_validar_senha'),
            {'senha': 'SenhaValida123!'}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['valida'])
        
        # Senha inválida
        response = self.client.get(
            reverse('api_validar_senha'),
            {'senha': '123'}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertFalse(data['valida'])

    def test_subcontas_api(self):
        """Testa API de subcontas"""
        # Fazer login
        session = self.client.session
        session['usuario_logado_id'] = self.admin.id
        session.save()
        
        # Buscar subcontas
        response = self.client.get(reverse('api_subcontas'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('subcontas', data)
        self.assertEqual(len(data['subcontas']), 1)  # Apenas o gerente

    def test_logout_api(self):
        """Testa API de logout"""
        # Fazer login primeiro
        session = self.client.session
        session['usuario_logado_id'] = self.admin.id
        session.save()
        
        # Fazer logout
        response = self.client.post(reverse('api_logout'))
        self.assertEqual(response.status_code, 200)
        
        # Verificar se a sessão foi limpa
        session = self.client.session
        self.assertNotIn('usuario_logado_id', session)


class ViewTest(TestCase):
    """Testes para as views tradicionais"""
    
    def setUp(self):
        """Configuração inicial para os testes de view"""
        self.client = Client()
        self.admin = Usuario.objects.create(
            nome="Admin View",
            email="admin@view.com",
            senha=make_password("Admin123!"),
            tipo="admin"
        )

    def test_create_view_get(self):
        """Testa view create com GET"""
        # Sem login
        response = self.client.get(reverse('create'))
        self.assertEqual(response.status_code, 200)
        
        # Com login
        session = self.client.session
        session['usuario_logado_id'] = self.admin.id
        session.save()
        
        response = self.client.get(reverse('create'))
        self.assertEqual(response.status_code, 200)

    def test_create_view_post(self):
        """Testa view create com POST"""
        # Fazer login
        session = self.client.session
        session['usuario_logado_id'] = self.admin.id
        session.save()
        
        # Criar usuário
        data = {
            'nome': 'Usuário View',
            'email': 'usuario@view.com',
            'senha': 'Usuario123!',
            'tipo': 'usuario'
        }
        response = self.client.post(reverse('create'), data)
        self.assertEqual(response.status_code, 302)  # Redirect
        
        # Verificar se foi criado
        self.assertTrue(Usuario.objects.filter(email='usuario@view.com').exists())

    def test_login_view(self):
        """Testa view de login"""
        # GET
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        
        # POST válido
        data = {
            'email': 'admin@view.com',
            'senha': 'Admin123!'
        }
        response = self.client.post(reverse('login'), data)
        self.assertEqual(response.status_code, 302)  # Redirect
        
        # Verificar se fez login
        session = self.client.session
        self.assertIn('usuario_logado_id', session)

    def test_logout_view(self):
        """Testa view de logout"""
        # Fazer login primeiro
        session = self.client.session
        session['usuario_logado_id'] = self.admin.id
        session.save()
        
        # Fazer logout
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Redirect
        
        # Verificar se fez logout
        session = self.client.session
        self.assertNotIn('usuario_logado_id', session)

    def test_alterar_senha_view(self):
        """Testa view de alterar senha"""
        # GET
        response = self.client.get(reverse('alterar_senha', args=[self.admin.id]))
        self.assertEqual(response.status_code, 200)
        
        # POST
        data = {
            'senha': 'NovaSenha123!'
        }
        response = self.client.post(reverse('alterar_senha', args=[self.admin.id]), data)
        self.assertEqual(response.status_code, 302)  # Redirect
        
        # Verificar se a senha foi alterada
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.verificar_senha('NovaSenha123!'))


class IntegrationTest(TestCase):
    """Testes de integração para fluxos completos"""
    
    def test_fluxo_completo_criacao_hierarquia(self):
        """Testa fluxo completo de criação de hierarquia de usuários"""
        # 1. Criar admin inicial via API
        data = {
            'nome': 'Admin Principal',
            'email': 'admin@principal.com',
            'senha': 'Admin123!'
        }
        response = self.client.post(
            reverse('api_criar_admin_inicial'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        admin = Usuario.objects.get(email='admin@principal.com')
        
        # 2. Login como admin
        session = self.client.session
        session['usuario_logado_id'] = admin.id
        session.save()
        
        # 3. Criar gerente via API
        gerente_data = {
            'nome': 'Gerente Principal',
            'email': 'gerente@principal.com',
            'senha': 'Gerente123!',
            'tipo': 'gerente'
        }
        response = self.client.post(
            reverse('api_usuarios'),
            data=json.dumps(gerente_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        
        gerente = Usuario.objects.get(email='gerente@principal.com')
        
        # 4. Verificar hierarquia
        self.assertEqual(gerente.conta_principal, admin)
        self.assertEqual(gerente.criado_por, admin)
        self.assertEqual(gerente.nivel_hierarquia, 1)
        
        # 5. Login como gerente
        session = self.client.session
        session['usuario_logado_id'] = gerente.id
        session.save()
        
        # 6. Criar usuário via API (como gerente)
        usuario_data = {
            'nome': 'Usuário Final',
            'email': 'usuario@final.com',
            'senha': 'Usuario123!',
            'tipo': 'usuario'
        }
        response = self.client.post(
            reverse('api_usuarios'),
            data=json.dumps(usuario_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        
        usuario = Usuario.objects.get(email='usuario@final.com')
        
        # 7. Verificar hierarquia completa
        self.assertEqual(usuario.conta_principal, gerente)
        self.assertEqual(usuario.criado_por, gerente)
        self.assertEqual(usuario.nivel_hierarquia, 2)
        
        # 8. Verificar subcontas do admin
        subcontas_admin = admin.get_todas_subcontas()
        self.assertEqual(subcontas_admin.count(), 2)
        self.assertIn(gerente, subcontas_admin)
        self.assertIn(usuario, subcontas_admin)

    def test_persistencia_banco_dados(self):
        """Testa persistência completa no banco de dados"""
        # Criar usuários
        admin = Usuario.objects.create(
            nome="Admin Persistência",
            email="admin@persistencia.com",
            senha="Admin123!",
            tipo="admin"
        )
        
        gerente = Usuario.objects.create(
            nome="Gerente Persistência",
            email="gerente@persistencia.com",
            senha="Gerente123!",
            tipo="gerente",
            conta_principal=admin,
            criado_por=admin
        )
        
        # Verificar persistência
        self.assertEqual(Usuario.objects.count(), 2)
        
        # Recarregar do banco
        admin_db = Usuario.objects.get(id=admin.id)
        gerente_db = Usuario.objects.get(id=gerente.id)
        
        # Verificar dados
        self.assertEqual(admin_db.nome, "Admin Persistência")
        self.assertEqual(gerente_db.conta_principal, admin_db)
        self.assertEqual(gerente_db.nivel_hierarquia, 1)
        
        # Verificar relacionamentos
        self.assertIn(gerente_db, admin_db.get_subcontas())
        self.assertIn(gerente_db, admin_db.get_todas_subcontas())

    def test_validacao_senha_completa(self):
        """Testa validação completa de senhas"""
        # Senhas válidas
        senhas_validas = [
            "Senha123!",
            "MinhaSenha456@",
            "Teste789#",
            "ComplexaABC123!"
        ]
        
        for senha in senhas_validas:
            response = self.client.get(
                reverse('api_validar_senha'),
                {'senha': senha}
            )
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.content)
            self.assertTrue(data['valida'], f"Senha '{senha}' deveria ser válida")
        
        # Senhas inválidas
        senhas_invalidas = [
            "123",  # Muito curta
            "senha",  # Sem maiúscula, número e especial
            "SENHA",  # Sem minúscula, número e especial
            "Senha123",  # Sem caractere especial
            "senha123!",  # Sem maiúscula
            "SENHA123!",  # Sem minúscula
            "SenhaABC!",  # Sem número
        ]
        
        for senha in senhas_invalidas:
            response = self.client.get(
                reverse('api_validar_senha'),
                {'senha': senha}
            )
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.content)
            self.assertFalse(data['valida'], f"Senha '{senha}' deveria ser inválida")


class PerformanceTest(TestCase):
    """Testes de performance para grandes volumes de dados"""
    
    def test_criacao_multiplos_usuarios(self):
        """Testa criação de múltiplos usuários"""
        admin = Usuario.objects.create(
            nome="Admin Performance",
            email="admin@performance.com",
            senha="Admin123!",
            tipo="admin"
        )
        
        # Criar 100 usuários
        for i in range(100):
            Usuario.objects.create(
                nome=f"Usuário {i}",
                email=f"usuario{i}@teste.com",
                senha="Usuario123!",
                tipo="usuario",
                conta_principal=admin,
                criado_por=admin
            )
        
        # Verificar se todos foram criados
        self.assertEqual(Usuario.objects.count(), 101)  # 100 + admin
        
        # Verificar subcontas do admin
        subcontas = admin.get_todas_subcontas()
        self.assertEqual(subcontas.count(), 100)

    def test_hierarquia_profunda(self):
        """Testa hierarquia com muitos níveis"""
        # Criar hierarquia: Admin -> Gerente1 -> Gerente2 -> ... -> Usuario
        admin = Usuario.objects.create(
            nome="Admin Hierarquia",
            email="admin@hierarquia.com",
            senha="Admin123!",
            tipo="admin"
        )
        
        atual = admin
        for i in range(10):  # 10 níveis de hierarquia
            novo = Usuario.objects.create(
                nome=f"Gerente Nível {i}",
                email=f"gerente{i}@hierarquia.com",
                senha="Gerente123!",
                tipo="gerente",
                conta_principal=atual,
                criado_por=atual
            )
            atual = novo
        
        # Criar usuário final
        usuario_final = Usuario.objects.create(
            nome="Usuário Final",
            email="usuario@final.com",
            senha="Usuario123!",
            tipo="usuario",
            conta_principal=atual,
            criado_por=atual
        )
        
        # Verificar nível hierárquico
        self.assertEqual(usuario_final.nivel_hierarquia, 11)
        
        # Verificar hierarquia completa
        hierarquia = usuario_final.get_hierarquia_completa()
        self.assertEqual(len(hierarquia), 12)  # 11 + usuário final
        
        # Verificar se admin consegue ver todos
        todas_subcontas = admin.get_todas_subcontas()
        self.assertEqual(todas_subcontas.count(), 11)  # 10 gerentes + 1 usuário
