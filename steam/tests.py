from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from datetime import date, timedelta
import json

from .models import ContaStreaming, CompartilhamentoStreaming, HistoricoAcesso
from usuarios.models import Usuario


class SteamAppTestCase(TestCase):
    """Testes para o app steam"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        # Criar usuários de teste
        self.admin = Usuario.objects.create(
            nome="Admin Teste",
            email="admin@teste.com",
            senha="Admin123!",
            tipo="admin"
        )
        
        self.gerente = Usuario.objects.create(
            nome="Gerente Teste",
            email="gerente@teste.com",
            senha="Gerente123!",
            tipo="gerente"
        )
        
        self.usuario = Usuario.objects.create(
            nome="Usuário Teste",
            email="usuario@teste.com",
            senha="Usuario123!",
            tipo="usuario"
        )
        
        # Criar contas de streaming de teste
        self.conta_netflix = ContaStreaming.objects.create(
            nome="Netflix Premium",
            plataforma="netflix",
            email="admin@netflix.com",
            usuario="admin_user",
            senha="Netflix123!",
            descricao="Conta Netflix Premium com 4 telas",
            status="ativo",
            data_expiracao=date.today() + timedelta(days=365),
            proprietario=self.admin
        )
        
        self.conta_disney = ContaStreaming.objects.create(
            nome="Disney+ Family",
            plataforma="disney",
            email="gerente@disney.com",
            usuario="gerente_user",
            senha="Disney123!",
            descricao="Conta Disney+ para família",
            status="ativo",
            data_expiracao=date.today() + timedelta(days=180),
            proprietario=self.gerente
        )
        
        # Configurar cliente
        self.client = Client()
        
        # Fazer login como admin
        self.client.post(reverse('api_login'), 
            data=json.dumps({
                'email': 'admin@teste.com',
                'senha': 'Admin123!'
            }),
            content_type='application/json'
        )


class ContaStreamingModelTest(SteamAppTestCase):
    """Testes para o modelo ContaStreaming"""
    
    def test_criar_conta_streaming(self):
        """Testa criação de conta de streaming"""
        conta = ContaStreaming.objects.create(
            nome="Spotify Premium",
            plataforma="spotify",
            email="teste@spotify.com",
            senha="Spotify123!",
            proprietario=self.usuario
        )
        
        self.assertEqual(conta.nome, "Spotify Premium")
        self.assertEqual(conta.plataforma, "spotify")
        self.assertEqual(conta.email, "teste@spotify.com")
        self.assertEqual(conta.proprietario, self.usuario)
        self.assertTrue(conta.ativo)
        self.assertEqual(conta.status, "ativo")
    
    def test_senha_criptografada(self):
        """Testa se a senha é criptografada automaticamente"""
        senha_plana = "MinhaSenha123!"
        conta = ContaStreaming.objects.create(
            nome="Teste Criptografia",
            plataforma="netflix",
            email="teste@cripto.com",
            senha=senha_plana,
            proprietario=self.admin
        )
        
        # Verificar se a senha foi criptografada
        self.assertNotEqual(conta.senha, senha_plana)
        self.assertTrue(conta.senha.startswith('pbkdf2_sha256$'))
        
        # Verificar se consegue verificar a senha
        self.assertTrue(conta.verificar_senha(senha_plana))
        self.assertFalse(conta.verificar_senha("SenhaErrada"))
    
    def test_verificar_senha(self):
        """Testa verificação de senha"""
        self.assertTrue(self.conta_netflix.verificar_senha("Netflix123!"))
        self.assertFalse(self.conta_netflix.verificar_senha("SenhaErrada"))
    
    def test_pode_ser_acessada_por(self):
        """Testa verificação de acesso à conta"""
        # Proprietário pode acessar
        self.assertTrue(self.conta_netflix.pode_ser_acessada_por(self.admin))
        
        # Outro usuário não pode acessar
        self.assertFalse(self.conta_netflix.pode_ser_acessada_por(self.usuario))
        
        # Após compartilhamento, usuário pode acessar
        self.conta_netflix.adicionar_compartilhamento(self.usuario, 'leitura')
        self.assertTrue(self.conta_netflix.pode_ser_acessada_por(self.usuario))
    
    def test_esta_expirada(self):
        """Testa verificação de expiração"""
        # Conta com data futura não está expirada
        self.assertFalse(self.conta_netflix.esta_expirada())
        
        # Conta com data passada está expirada
        conta_expirada = ContaStreaming.objects.create(
            nome="Conta Expirada",
            plataforma="netflix",
            email="expirada@teste.com",
            senha="Senha123!",
            data_expiracao=date.today() - timedelta(days=1),
            proprietario=self.admin
        )
        self.assertTrue(conta_expirada.esta_expirada())
    
    def test_atualizar_ultimo_acesso(self):
        """Testa atualização do último acesso"""
        self.assertIsNone(self.conta_netflix.ultimo_acesso)
        
        self.conta_netflix.atualizar_ultimo_acesso()
        self.assertIsNotNone(self.conta_netflix.ultimo_acesso)


class CompartilhamentoStreamingModelTest(SteamAppTestCase):
    """Testes para o modelo CompartilhamentoStreaming"""
    
    def test_adicionar_compartilhamento(self):
        """Testa adição de compartilhamento"""
        compartilhamento = self.conta_netflix.adicionar_compartilhamento(
            self.usuario, 'acesso'
        )
        
        self.assertEqual(compartilhamento.conta, self.conta_netflix)
        self.assertEqual(compartilhamento.usuario, self.usuario)
        self.assertEqual(compartilhamento.nivel_acesso, 'acesso')
        self.assertTrue(compartilhamento.ativo)
    
    def test_remover_compartilhamento(self):
        """Testa remoção de compartilhamento"""
        # Adicionar compartilhamento
        self.conta_netflix.adicionar_compartilhamento(self.usuario, 'leitura')
        self.assertTrue(self.conta_netflix.pode_ser_acessada_por(self.usuario))
        
        # Remover compartilhamento
        self.conta_netflix.remover_compartilhamento(self.usuario)
        self.assertFalse(self.conta_netflix.pode_ser_acessada_por(self.usuario))
    
    def test_permissoes_compartilhamento(self):
        """Testa permissões de compartilhamento"""
        # Nível leitura
        compartilhamento_leitura = CompartilhamentoStreaming.objects.create(
            conta=self.conta_netflix,
            usuario=self.usuario,
            nivel_acesso='leitura'
        )
        self.assertFalse(compartilhamento_leitura.pode_editar())
        self.assertFalse(compartilhamento_leitura.pode_deletar())
        
        # Nível acesso
        compartilhamento_acesso = CompartilhamentoStreaming.objects.create(
            conta=self.conta_disney,
            usuario=self.admin,
            nivel_acesso='acesso'
        )
        self.assertTrue(compartilhamento_acesso.pode_editar())
        self.assertFalse(compartilhamento_acesso.pode_deletar())
        
        # Nível admin
        compartilhamento_admin = CompartilhamentoStreaming.objects.create(
            conta=self.conta_disney,
            usuario=self.usuario,
            nivel_acesso='admin'
        )
        self.assertTrue(compartilhamento_admin.pode_editar())
        self.assertTrue(compartilhamento_admin.pode_deletar())


class HistoricoAcessoModelTest(SteamAppTestCase):
    """Testes para o modelo HistoricoAcesso"""
    
    def test_criar_historico_acesso(self):
        """Testa criação de histórico de acesso"""
        historico = HistoricoAcesso.objects.create(
            conta=self.conta_netflix,
            usuario=self.admin,
            ip_acesso="192.168.1.100",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            sucesso=True,
            observacoes="Acesso normal"
        )
        
        self.assertEqual(historico.conta, self.conta_netflix)
        self.assertEqual(historico.usuario, self.admin)
        self.assertEqual(historico.ip_acesso, "192.168.1.100")
        self.assertTrue(historico.sucesso)
        self.assertEqual(historico.observacoes, "Acesso normal")


class SteamAPITest(SteamAppTestCase):
    """Testes para as APIs do steam"""
    
    def test_listar_contas_streaming(self):
        """Testa listagem de contas de streaming"""
        response = self.client.get(reverse('steam:streaming_list_create'))
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verificar se retorna as contas do admin
        self.assertEqual(len(data), 1)  # Apenas a conta do admin
        self.assertEqual(data[0]['nome'], "Netflix Premium")
        self.assertEqual(data[0]['plataforma'], "netflix")
        self.assertTrue(data[0]['is_proprietario'])
    
    def test_criar_conta_streaming(self):
        """Testa criação de conta de streaming via API"""
        dados = {
            'nome': 'Nova Conta',
            'plataforma': 'spotify',
            'email': 'nova@spotify.com',
            'senha': 'NovaSenha123!',
            'descricao': 'Conta de teste'
        }
        
        response = self.client.post(
            reverse('steam:streaming_list_create'),
            data=json.dumps(dados),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        data = response.json()
        
        self.assertEqual(data['nome'], 'Nova Conta')
        self.assertEqual(data['plataforma'], 'spotify')
        self.assertEqual(data['email'], 'nova@spotify.com')
        self.assertTrue(data['is_proprietario'])
        
        # Verificar se foi criada no banco
        conta = ContaStreaming.objects.get(email='nova@spotify.com')
        self.assertEqual(conta.proprietario, self.admin)
    
    def test_criar_conta_sem_dados_obrigatorios(self):
        """Testa criação de conta sem dados obrigatórios"""
        dados = {
            'nome': 'Conta Incompleta',
            'plataforma': 'netflix'
            # Faltando email e senha
        }
        
        response = self.client.post(
            reverse('steam:streaming_list_create'),
            data=json.dumps(dados),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('erro', data)
    
    def test_ver_conta_streaming(self):
        """Testa visualização de conta específica"""
        response = self.client.get(
            reverse('steam:streaming_detail', kwargs={'pk': self.conta_netflix.id})
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data['nome'], 'Netflix Premium')
        self.assertEqual(data['email'], 'admin@netflix.com')
        self.assertEqual(data['senha'], 'Netflix123!')  # Senha descriptografada
        self.assertTrue(data['is_proprietario'])
    
    def test_ver_conta_inexistente(self):
        """Testa visualização de conta que não existe"""
        response = self.client.get(
            reverse('steam:streaming_detail', kwargs={'pk': 99999})
        )
        
        self.assertEqual(response.status_code, 404)
    
    def test_ver_conta_sem_permissao(self):
        """Testa visualização de conta sem permissão"""
        # Fazer login como usuário diferente
        self.client.post(reverse('api_login'), 
            data=json.dumps({
                'email': 'usuario@teste.com',
                'senha': 'Usuario123!'
            }),
            content_type='application/json'
        )
        
        response = self.client.get(
            reverse('steam:streaming_detail', kwargs={'pk': self.conta_netflix.id})
        )
        
        self.assertEqual(response.status_code, 403)
    
    def test_atualizar_conta_streaming(self):
        """Testa atualização de conta de streaming"""
        dados = {
            'nome': 'Netflix Atualizado',
            'descricao': 'Descrição atualizada'
        }
        
        response = self.client.put(
            reverse('steam:streaming_detail', kwargs={'pk': self.conta_netflix.id}),
            data=json.dumps(dados),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data['nome'], 'Netflix Atualizado')
        self.assertEqual(data['descricao'], 'Descrição atualizada')
        
        # Verificar se foi atualizada no banco
        self.conta_netflix.refresh_from_db()
        self.assertEqual(self.conta_netflix.nome, 'Netflix Atualizado')
    
    def test_deletar_conta_streaming(self):
        """Testa exclusão de conta de streaming"""
        response = self.client.delete(
            reverse('steam:streaming_detail', kwargs={'pk': self.conta_netflix.id})
        )
        
        self.assertEqual(response.status_code, 204)
        
        # Verificar se foi marcada como inativa no banco
        self.conta_netflix.refresh_from_db()
        self.assertFalse(self.conta_netflix.ativo)
    
    def test_compartilhar_conta(self):
        """Testa compartilhamento de conta"""
        dados = {
            'email': 'usuario@teste.com',
            'nivel_acesso': 'acesso'
        }
        
        response = self.client.post(
            reverse('steam:streaming_compartilhar', kwargs={'pk': self.conta_netflix.id}),
            data=json.dumps(dados),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        data = response.json()
        
        self.assertEqual(data['usuario']['email'], 'usuario@teste.com')
        self.assertEqual(data['nivel_acesso'], 'acesso')
        
        # Verificar se foi criado no banco
        compartilhamento = CompartilhamentoStreaming.objects.get(
            conta=self.conta_netflix,
            usuario=self.usuario
        )
        self.assertEqual(compartilhamento.nivel_acesso, 'acesso')
    
    def test_compartilhar_conta_usuario_inexistente(self):
        """Testa compartilhamento com usuário que não existe"""
        dados = {
            'email': 'inexistente@teste.com',
            'nivel_acesso': 'leitura'
        }
        
        response = self.client.post(
            reverse('steam:streaming_compartilhar', kwargs={'pk': self.conta_netflix.id}),
            data=json.dumps(dados),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 404)
    
    def test_compartilhar_conta_sem_permissao(self):
        """Testa compartilhamento sem ser proprietário"""
        # Fazer login como usuário diferente
        self.client.post(reverse('api_login'), 
            data=json.dumps({
                'email': 'usuario@teste.com',
                'senha': 'Usuario123!'
            }),
            content_type='application/json'
        )
        
        dados = {
            'email': 'gerente@teste.com',
            'nivel_acesso': 'leitura'
        }
        
        response = self.client.post(
            reverse('steam:streaming_compartilhar', kwargs={'pk': self.conta_netflix.id}),
            data=json.dumps(dados),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 403)
    
    def test_remover_compartilhamento(self):
        """Testa remoção de compartilhamento"""
        # Primeiro compartilhar a conta
        self.conta_netflix.adicionar_compartilhamento(self.usuario, 'leitura')
        
        response = self.client.delete(
            reverse('steam:streaming_descompartilhar', kwargs={
                'pk': self.conta_netflix.id,
                'usuario_id': self.usuario.id
            })
        )
        
        self.assertEqual(response.status_code, 204)
        
        # Verificar se foi removido do banco
        self.assertFalse(
            self.conta_netflix.compartilhado_com.filter(id=self.usuario.id).exists()
        )
    
    def test_listar_plataformas(self):
        """Testa listagem de plataformas"""
        response = self.client.get(reverse('steam:streaming_plataformas'))
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verificar se retorna as plataformas
        self.assertGreater(len(data), 0)
        plataformas = [p['codigo'] for p in data]
        self.assertIn('netflix', plataformas)
        self.assertIn('disney', plataformas)
        self.assertIn('spotify', plataformas)
    
    def test_listar_status(self):
        """Testa listagem de status"""
        response = self.client.get(reverse('steam:streaming_status'))
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verificar se retorna os status
        self.assertGreater(len(data), 0)
        status_list = [s['codigo'] for s in data]
        self.assertIn('ativo', status_list)
        self.assertIn('inativo', status_list)
        self.assertIn('pendente', status_list)
        self.assertIn('expirado', status_list)


class SteamAPIAuthenticationTest(TestCase):
    """Testes de autenticação para as APIs do steam"""
    
    def setUp(self):
        """Configuração inicial"""
        self.client = Client()
        self.admin = Usuario.objects.create(
            nome="Admin Teste",
            email="admin@teste.com",
            senha="Admin123!",
            tipo="admin"
        )
        
        self.conta = ContaStreaming.objects.create(
            nome="Conta Teste",
            plataforma="netflix",
            email="teste@netflix.com",
            senha="Senha123!",
            proprietario=self.admin
        )
    
    def test_acesso_sem_autenticacao(self):
        """Testa acesso às APIs sem autenticação"""
        # Listar contas
        response = self.client.get(reverse('steam:streaming_list_create'))
        self.assertEqual(response.status_code, 401)
        
        # Ver conta específica
        response = self.client.get(
            reverse('steam:streaming_detail', kwargs={'pk': self.conta.id})
        )
        self.assertEqual(response.status_code, 401)
        
        # Listar plataformas
        response = self.client.get(reverse('steam:streaming_plataformas'))
        self.assertEqual(response.status_code, 401)
        
        # Listar status
        response = self.client.get(reverse('steam:streaming_status'))
        self.assertEqual(response.status_code, 401)
    
    def test_acesso_com_autenticacao(self):
        """Testa acesso às APIs com autenticação"""
        # Fazer login
        self.client.post(reverse('api_login'), 
            data=json.dumps({
                'email': 'admin@teste.com',
                'senha': 'Admin123!'
            }),
            content_type='application/json'
        )
        
        # Listar contas
        response = self.client.get(reverse('steam:streaming_list_create'))
        self.assertEqual(response.status_code, 200)
        
        # Ver conta específica
        response = self.client.get(
            reverse('steam:streaming_detail', kwargs={'pk': self.conta.id})
        )
        self.assertEqual(response.status_code, 200)
        
        # Listar plataformas
        response = self.client.get(reverse('steam:streaming_plataformas'))
        self.assertEqual(response.status_code, 200)
        
        # Listar status
        response = self.client.get(reverse('steam:streaming_status'))
        self.assertEqual(response.status_code, 200)


class SteamIntegrationTest(SteamAppTestCase):
    """Testes de integração para o app steam"""
    
    def test_fluxo_completo_conta_streaming(self):
        """Testa fluxo completo de criação, edição e exclusão de conta"""
        # 1. Criar conta
        dados_criacao = {
            'nome': 'Conta Integração',
            'plataforma': 'spotify',
            'email': 'integracao@spotify.com',
            'senha': 'Integracao123!',
            'descricao': 'Conta para teste de integração'
        }
        
        response = self.client.post(
            reverse('steam:streaming_list_create'),
            data=json.dumps(dados_criacao),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        
        conta_id = response.json()['id']
        
        # 2. Verificar se foi criada
        response = self.client.get(
            reverse('steam:streaming_detail', kwargs={'pk': conta_id})
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['nome'], 'Conta Integração')
        
        # 3. Atualizar conta
        dados_atualizacao = {
            'nome': 'Conta Integração Atualizada',
            'descricao': 'Descrição atualizada'
        }
        
        response = self.client.put(
            reverse('steam:streaming_detail', kwargs={'pk': conta_id}),
            data=json.dumps(dados_atualizacao),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        # 4. Verificar atualização
        response = self.client.get(
            reverse('steam:streaming_detail', kwargs={'pk': conta_id})
        )
        data = response.json()
        self.assertEqual(data['nome'], 'Conta Integração Atualizada')
        
        # 5. Compartilhar conta
        dados_compartilhamento = {
            'email': 'usuario@teste.com',
            'nivel_acesso': 'leitura'
        }
        
        response = self.client.post(
            reverse('steam:streaming_compartilhar', kwargs={'pk': conta_id}),
            data=json.dumps(dados_compartilhamento),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        
        # 6. Deletar conta
        response = self.client.delete(
            reverse('steam:streaming_detail', kwargs={'pk': conta_id})
        )
        self.assertEqual(response.status_code, 204)
        
        # 7. Verificar se foi deletada (soft delete)
        response = self.client.get(
            reverse('steam:streaming_detail', kwargs={'pk': conta_id})
        )
        self.assertEqual(response.status_code, 404)
    
    def test_compartilhamento_e_acesso(self):
        """Testa fluxo de compartilhamento e acesso"""
        # 1. Admin compartilha conta com usuário
        dados_compartilhamento = {
            'email': 'usuario@teste.com',
            'nivel_acesso': 'acesso'
        }
        
        response = self.client.post(
            reverse('steam:streaming_compartilhar', kwargs={'pk': self.conta_netflix.id}),
            data=json.dumps(dados_compartilhamento),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        
        # 2. Usuário faz login
        self.client.post(reverse('api_login'), 
            data=json.dumps({
                'email': 'usuario@teste.com',
                'senha': 'Usuario123!'
            }),
            content_type='application/json'
        )
        
        # 3. Usuário lista suas contas (incluindo compartilhadas)
        response = self.client.get(reverse('steam:streaming_list_create'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verificar se a conta compartilhada aparece na lista
        contas_compartilhadas = [c for c in data if not c['is_proprietario']]
        self.assertEqual(len(contas_compartilhadas), 1)
        self.assertEqual(contas_compartilhadas[0]['nome'], 'Netflix Premium')
        
        # 4. Usuário acessa a conta compartilhada
        response = self.client.get(
            reverse('steam:streaming_detail', kwargs={'pk': self.conta_netflix.id})
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data['is_proprietario'])
        self.assertTrue(data['pode_editar'])  # Nível 'acesso' permite edição
        
        # 5. Usuário tenta deletar (não deve conseguir)
        response = self.client.delete(
            reverse('steam:streaming_detail', kwargs={'pk': self.conta_netflix.id})
        )
        self.assertEqual(response.status_code, 403)
    
    def test_estatisticas_e_historico(self):
        """Testa criação de estatísticas e histórico"""
        # 1. Criar alguns acessos
        HistoricoAcesso.objects.create(
            conta=self.conta_netflix,
            usuario=self.admin,
            ip_acesso="192.168.1.100",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            sucesso=True,
            observacoes="Acesso normal"
        )
        
        HistoricoAcesso.objects.create(
            conta=self.conta_netflix,
            usuario=self.admin,
            ip_acesso="192.168.1.101",
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 14_0)",
            sucesso=False,
            observacoes="Senha incorreta"
        )
        
        # 2. Verificar estatísticas
        total_acessos = HistoricoAcesso.objects.count()
        acessos_sucesso = HistoricoAcesso.objects.filter(sucesso=True).count()
        acessos_falha = HistoricoAcesso.objects.filter(sucesso=False).count()
        
        self.assertEqual(total_acessos, 2)
        self.assertEqual(acessos_sucesso, 1)
        self.assertEqual(acessos_falha, 1)
        
        # 3. Verificar taxa de sucesso
        taxa_sucesso = (acessos_sucesso / total_acessos) * 100
        self.assertEqual(taxa_sucesso, 50.0)
        
        # 4. Verificar se os acessos estão associados corretamente
        acessos_conta = HistoricoAcesso.objects.filter(conta=self.conta_netflix)
        self.assertEqual(acessos_conta.count(), 2)
        
        acessos_admin = HistoricoAcesso.objects.filter(usuario=self.admin)
        self.assertEqual(acessos_admin.count(), 2)
