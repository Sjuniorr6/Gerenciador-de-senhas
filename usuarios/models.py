from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
# Create your models here.
class Usuario(models.Model):
    TIPO_CHOICES = [
        ('admin', 'Administrador'),
        ('gerente', 'Gerente'),
        ('usuario', 'Usuário'),
    ]
    
    nome = models.CharField(max_length=50)
    email = models.EmailField(max_length=50, unique=True)
    senha = models.CharField(max_length=128)  # Aumentado para hash
    foto = models.ImageField(upload_to='fotos', null=True, blank=True)
    
    # Campos para hierarquia
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='usuario')
    conta_principal = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcontas')
    criado_por = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='usuarios_criados')
    data_criacao = models.DateTimeField(default=timezone.now)
    ativo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"{self.nome} ({self.get_tipo_display()})"
    
    def save(self, *args, **kwargs):
        # Hash da senha se não estiver hasheada
        if not self.senha.startswith('pbkdf2_sha256$'):
            self.senha = make_password(self.senha)
        super().save(*args, **kwargs)
    
    def verificar_senha(self, senha_plana):
        """Verifica se a senha está correta"""
        return check_password(senha_plana, self.senha)
    
    def pode_criar_subcontas(self):
        """Verifica se o usuário pode criar subcontas"""
        return self.tipo in ['admin', 'gerente']
    
    def pode_gerenciar_usuario(self, usuario_alvo):
        """Verifica se pode gerenciar outro usuário"""
        if self.tipo == 'admin':
            return True
        elif self.tipo == 'gerente':
            # Gerente só pode gerenciar usuários que ele criou ou que são subcontas dele
            return usuario_alvo.criado_por == self or usuario_alvo.conta_principal == self
        return False
    
    def get_subcontas(self):
        """Retorna todas as subcontas diretas"""
        return Usuario.objects.filter(conta_principal=self, ativo=True)
    
    def get_todas_subcontas(self):
        """Retorna todas as subcontas (recursivo)"""
        subcontas = self.get_subcontas()
        for subconta in subcontas:
            subcontas = subcontas.union(subconta.get_todas_subcontas())
        return subcontas
    
    def get_hierarquia_completa(self):
        """Retorna a hierarquia completa do usuário"""
        if self.conta_principal:
            return self.conta_principal.get_hierarquia_completa() + [self]
        return [self]
    
    @property
    def nivel_hierarquia(self):
        """Retorna o nível na hierarquia (0 = raiz)"""
        if self.conta_principal:
            return self.conta_principal.nivel_hierarquia + 1
        return 0