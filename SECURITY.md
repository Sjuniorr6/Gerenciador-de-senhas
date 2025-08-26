# 🔒 Guia de Segurança

## ⚠️ Informações Sensíveis

### O que NÃO deve ser versionado:

1. **Arquivo `.env`** - Contém todas as variáveis de ambiente sensíveis
2. **Banco de dados** - Arquivos `.sqlite3`, `.db`, `.sql`
3. **Arquivos de mídia** - Uploads de usuários, fotos
4. **Logs** - Arquivos de log do sistema
5. **Chaves privadas** - Certificados SSL, chaves de API
6. **Credenciais** - Senhas, tokens, chaves de acesso

### O que está protegido pelo `.gitignore`:

```gitignore
# Arquivos de ambiente
.env
.env.local
.env.development
.env.test
.env.production

# Banco de dados
*.sqlite3
*.db
*.sql

# Arquivos de mídia
media/
uploads/
fotos/

# Logs
logs/
*.log

# Cache e arquivos temporários
__pycache__/
*.pyc
*.pyo
*.pyd
```

## 🔧 Configuração Segura

### 1. Configurar o ambiente:

```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar arquivo .env
python setup_env.py
```

### 2. Configurações obrigatórias no `.env`:

```env
# Chave secreta (gerada automaticamente)
SECRET_KEY=sua_chave_secreta_aqui

# Configurações de segurança
DEBUG=False  # Para produção
ALLOWED_HOSTS=seudominio.com,www.seudominio.com

# Banco de dados
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=seu_banco
DATABASE_USER=seu_usuario
DATABASE_PASSWORD=sua_senha

# Email
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-de-app
```

## 🛡️ Boas Práticas de Segurança

### 1. **Senhas e Autenticação:**
- ✅ Use senhas fortes (8+ caracteres, maiúsculas, minúsculas, números, especiais)
- ✅ Hash automático de senhas (já implementado)
- ✅ Sessões seguras com timeout
- ✅ CSRF protection ativado

### 2. **Configurações de Produção:**
- ✅ `DEBUG=False`
- ✅ `SECRET_KEY` única e segura
- ✅ `ALLOWED_HOSTS` configurado corretamente
- ✅ HTTPS habilitado
- ✅ Cookies seguros

### 3. **Banco de Dados:**
- ✅ Use PostgreSQL em produção
- ✅ Backup automático configurado
- ✅ Usuário com privilégios mínimos
- ✅ Conexão criptografada

### 4. **Upload de Arquivos:**
- ✅ Validação de tipos de arquivo
- ✅ Limite de tamanho (5MB)
- ✅ Armazenamento seguro
- ✅ Sanitização de nomes

### 5. **APIs:**
- ✅ Rate limiting configurado
- ✅ Validação de entrada
- ✅ Autenticação por sessão
- ✅ CORS configurado corretamente

## 🚨 Checklist de Segurança

### Antes do Deploy:

- [ ] `DEBUG=False` no `.env`
- [ ] `SECRET_KEY` única e segura
- [ ] `ALLOWED_HOSTS` configurado
- [ ] Banco de dados PostgreSQL
- [ ] HTTPS configurado
- [ ] Backup automático ativado
- [ ] Logs configurados
- [ ] Rate limiting ativado
- [ ] Validação de senhas ativada
- [ ] CSRF protection ativado

### Monitoramento:

- [ ] Logs de erro configurados
- [ ] Monitoramento de tentativas de login
- [ ] Backup regular testado
- [ ] Atualizações de segurança
- [ ] Auditoria de permissões

## 🔐 Configurações de Senha

O sistema implementa validação rigorosa de senhas:

```python
# Configurações no .env
PASSWORD_MIN_LENGTH=8
PASSWORD_REQUIRE_UPPERCASE=True
PASSWORD_REQUIRE_LOWERCASE=True
PASSWORD_REQUIRE_NUMBERS=True
PASSWORD_REQUIRE_SPECIAL=True
```

### Requisitos de Senha:
- Mínimo 8 caracteres
- Pelo menos 1 letra maiúscula
- Pelo menos 1 letra minúscula
- Pelo menos 1 número
- Pelo menos 1 caractere especial

## 📧 Configuração de Email

Para funcionalidades de email (recuperação de senha, notificações):

```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-de-app
```

**Nota:** Para Gmail, use "Senha de App" em vez da senha normal.

## 🔄 Backup e Recuperação

### Backup Automático:
```env
BACKUP_ENABLED=True
BACKUP_PATH=/var/backups/django/
BACKUP_RETENTION_DAYS=30
```

### Backup Manual:
```bash
# Backup do banco
python manage.py dumpdata > backup.json

# Backup de arquivos
tar -czf media_backup.tar.gz media/
```

## 🚀 Deploy Seguro

### 1. **Servidor:**
- Use HTTPS
- Configure firewall
- Mantenha sistema atualizado
- Use servidor WSGI (Gunicorn)

### 2. **Banco de Dados:**
- PostgreSQL em produção
- Backup automático
- Conexão criptografada
- Usuário com privilégios mínimos

### 3. **Arquivos Estáticos:**
- Servidos por servidor web (Nginx)
- Cache configurado
- Compressão ativada

### 4. **Monitoramento:**
- Logs centralizados
- Alertas de erro
- Monitoramento de performance
- Auditoria de acesso

## 📞 Suporte de Segurança

Se encontrar vulnerabilidades:

1. **Não abra issues públicos** com informações sensíveis
2. **Reporte diretamente** para o mantenedor
3. **Inclua detalhes** da vulnerabilidade
4. **Aguarde resposta** antes de divulgar

## 📚 Recursos Adicionais

- [Django Security](https://docs.djangoproject.com/en/stable/topics/security/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
