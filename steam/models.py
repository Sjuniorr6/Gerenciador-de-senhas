from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from usuarios.models import Usuario


class ContaStreaming(models.Model):
    """
    Modelo para gerenciar contas de streaming
    """
    
    PLATAFORMAS_CHOICES = [
        ('netflix', 'Netflix'),
        ('disney', 'Disney+'),
        ('hbo', 'HBO Max'),
        ('prime', 'Amazon Prime'),
        ('paramount', 'Paramount+'),
        ('starz', 'Starz'),
        ('apple', 'Apple TV+'),
        ('hulu', 'Hulu'),
        ('peacock', 'Peacock'),
        ('crunchyroll', 'Crunchyroll'),
        ('funimation', 'Funimation'),
        ('youtube', 'YouTube Premium'),
        ('spotify', 'Spotify'),
        ('deezer', 'Deezer'),
        ('tidal', 'Tidal'),
        ('outros', 'Outros'),
    ]
    
    STATUS_CHOICES = [
        ('ativo', 'Ativo'),
        ('inativo', 'Inativo'),
        ('pendente', 'Pendente'),
        ('expirado', 'Expirado'),
    ]
    
    # Informações básicas
    nome = models.CharField(max_length=100, help_text="Nome da conta")
    plataforma = models.CharField(max_length=20, choices=PLATAFORMAS_CHOICES, default='netflix')
    email = models.EmailField(help_text="Email da conta")
    usuario = models.CharField(max_length=100, blank=True, null=True, help_text="Nome de usuário (se diferente do email)")
    senha = models.CharField(max_length=255, help_text="Senha da conta (será criptografada)")
    
    # Informações adicionais
    foto = models.ImageField(upload_to='streaming_fotos/', blank=True, null=True, help_text="Foto/logo da plataforma")
    descricao = models.TextField(blank=True, null=True, help_text="Descrição adicional da conta")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ativo')
    
    # Datas importantes
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_expiracao = models.DateField(blank=True, null=True, help_text="Data de expiração da conta")
    ultimo_acesso = models.DateTimeField(blank=True, null=True, help_text="Último acesso à conta")
    
    # Relacionamentos
    proprietario = models.ForeignKey(
        Usuario, 
        on_delete=models.CASCADE, 
        related_name='contas_streaming',
        help_text="Usuário que criou/possui esta conta"
    )
    compartilhado_com = models.ManyToManyField(
        Usuario,
        through='CompartilhamentoStreaming',
        related_name='contas_compartilhadas',
        blank=True,
        help_text="Usuários com quem esta conta é compartilhada"
    )
    
    # Configurações
    ativo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Conta de Streaming"
        verbose_name_plural = "Contas de Streaming"
        ordering = ['-data_criacao']
        unique_together = ['email', 'plataforma', 'proprietario']
    
    def __str__(self):
        return f"{self.nome} ({self.get_plataforma_display()})"
    
    def save(self, *args, **kwargs):
        # Criptografar senha se não estiver criptografada
        if self.senha and not self.senha.startswith('pbkdf2_sha256$'):
            self.senha = make_password(self.senha)
        super().save(*args, **kwargs)
    
    def verificar_senha(self, senha_plana):
        """Verifica se a senha fornecida está correta"""
        return check_password(senha_plana, self.senha)
    
    def get_senha_plana(self):
        """Retorna a senha descriptografada (apenas para exibição)"""
        # Em produção, isso deve ser feito com cuidado
        return self.senha
    
    def pode_ser_acessada_por(self, usuario):
        """Verifica se um usuário pode acessar esta conta"""
        if self.proprietario == usuario:
            return True
        
        # Verificar se está compartilhada com o usuário
        return self.compartilhado_com.filter(id=usuario.id).exists()
    
    def adicionar_compartilhamento(self, usuario, nivel_acesso='leitura'):
        """Adiciona um usuário ao compartilhamento"""
        compartilhamento, created = CompartilhamentoStreaming.objects.get_or_create(
            conta=self,
            usuario=usuario,
            defaults={'nivel_acesso': nivel_acesso}
        )
        return compartilhamento
    
    def remover_compartilhamento(self, usuario):
        """Remove um usuário do compartilhamento"""
        self.compartilhado_com.remove(usuario)
    
    def get_usuarios_compartilhados(self):
        """Retorna lista de usuários com quem a conta é compartilhada"""
        return self.compartilhado_com.all()
    
    def esta_expirada(self):
        """Verifica se a conta está expirada"""
        if self.data_expiracao:
            from django.utils import timezone
            return timezone.now().date() > self.data_expiracao
        return False
    
    def atualizar_ultimo_acesso(self):
        """Atualiza a data do último acesso"""
        from django.utils import timezone
        self.ultimo_acesso = timezone.now()
        self.save(update_fields=['ultimo_acesso'])


class CompartilhamentoStreaming(models.Model):
    """
    Modelo intermediário para gerenciar compartilhamentos de contas
    """
    
    NIVEL_ACESSO_CHOICES = [
        ('leitura', 'Apenas Visualização'),
        ('acesso', 'Acesso Completo'),
        ('admin', 'Administrador'),
    ]
    
    conta = models.ForeignKey(ContaStreaming, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    data_compartilhamento = models.DateTimeField(auto_now_add=True)
    nivel_acesso = models.CharField(max_length=10, choices=NIVEL_ACESSO_CHOICES, default='leitura')
    ativo = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['conta', 'usuario']
        verbose_name = "Compartilhamento de Streaming"
        verbose_name_plural = "Compartilhamentos de Streaming"
    
    def __str__(self):
        return f"{self.conta.nome} compartilhada com {self.usuario.nome}"
    
    def pode_editar(self):
        """Verifica se o usuário pode editar a conta"""
        return self.nivel_acesso in ['acesso', 'admin']
    
    def pode_deletar(self):
        """Verifica se o usuário pode deletar a conta"""
        return self.nivel_acesso == 'admin'


class HistoricoAcesso(models.Model):
    """
    Modelo para registrar histórico de acessos às contas
    """
    
    conta = models.ForeignKey(ContaStreaming, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    data_acesso = models.DateTimeField(auto_now_add=True)
    ip_acesso = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    sucesso = models.BooleanField(default=True)
    observacoes = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Histórico de Acesso"
        verbose_name_plural = "Histórico de Acessos"
        ordering = ['-data_acesso']
    
    def __str__(self):
        return f"Acesso de {self.usuario.nome} em {self.conta.nome} - {self.data_acesso}"
