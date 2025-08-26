#!/usr/bin/env python
"""
Script para configurar o arquivo .env de forma segura
Gera um arquivo .env com configurações seguras para desenvolvimento e produção
"""

import os
import secrets
import string
from pathlib import Path


def generate_secret_key(length=50):
    """Gera uma chave secreta segura"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*(-_=+)"
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def create_env_file():
    """Cria o arquivo .env com configurações seguras"""
    
    # Verificar se o arquivo .env já existe
    if os.path.exists('.env'):
        print("⚠️  Arquivo .env já existe!")
        response = input("Deseja sobrescrever? (s/N): ")
        if response.lower() != 's':
            print("❌ Operação cancelada.")
            return
    
    # Gerar chave secreta segura
    secret_key = generate_secret_key()
    
    # Configurações do ambiente
    env_content = f"""# Configurações do Django
SECRET_KEY={secret_key}
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,testserver

# Configurações do Banco de Dados
DATABASE_ENGINE=django.db.backends.sqlite3
DATABASE_NAME=db.sqlite3

# Configurações de Email (para produção)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-de-app

# Configurações de Segurança
CSRF_TRUSTED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173

# Configurações de CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173

# Configurações de Upload
MAX_UPLOAD_SIZE=5242880
ALLOWED_IMAGE_TYPES=jpg,jpeg,png,gif

# Configurações de Senha
PASSWORD_MIN_LENGTH=8
PASSWORD_REQUIRE_UPPERCASE=True
PASSWORD_REQUIRE_LOWERCASE=True
PASSWORD_REQUIRE_NUMBERS=True
PASSWORD_REQUIRE_SPECIAL=True

# Configurações de Sessão
SESSION_COOKIE_AGE=3600
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False

# Configurações de Log
LOG_LEVEL=INFO
LOG_FILE=logs/django.log

# Configurações de Cache (para produção)
CACHE_BACKEND=django.core.cache.backends.locmem.LocMemCache
CACHE_LOCATION=unique-snowflake

# Configurações de API
API_RATE_LIMIT=100
API_RATE_LIMIT_PERIOD=3600

# Configurações de Backup
BACKUP_ENABLED=False
BACKUP_PATH=backups/
BACKUP_RETENTION_DAYS=30
"""
    
    # Criar diretórios necessários
    Path('logs').mkdir(exist_ok=True)
    Path('backups').mkdir(exist_ok=True)
    Path('media').mkdir(exist_ok=True)
    Path('staticfiles').mkdir(exist_ok=True)
    
    # Escrever arquivo .env
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("✅ Arquivo .env criado com sucesso!")
    print("🔑 Nova chave secreta gerada automaticamente")
    print("📁 Diretórios necessários criados")
    print("\n⚠️  IMPORTANTE:")
    print("1. Configure suas credenciais de email no arquivo .env")
    print("2. Nunca commite o arquivo .env no Git")
    print("3. Para produção, altere DEBUG=False")


def create_production_env():
    """Cria configurações para produção"""
    
    print("\n🔧 Configurações para Produção:")
    print("=" * 50)
    
    production_env = """# Configurações de Produção
SECRET_KEY=SUA_CHAVE_SECRETA_MUITO_SEGURA_AQUI
DEBUG=False
ALLOWED_HOSTS=seudominio.com,www.seudominio.com

# Banco de dados PostgreSQL (recomendado para produção)
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=seu_banco
DATABASE_USER=seu_usuario
DATABASE_PASSWORD=sua_senha
DATABASE_HOST=localhost
DATABASE_PORT=5432

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-de-app

# Segurança
CSRF_TRUSTED_ORIGINS=https://seudominio.com,https://www.seudominio.com
CORS_ALLOWED_ORIGINS=https://seudominio.com,https://www.seudominio.com
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Cache Redis (recomendado para produção)
CACHE_BACKEND=django.core.cache.backends.redis.RedisCache
CACHE_LOCATION=redis://127.0.0.1:6379/1

# Logs
LOG_LEVEL=WARNING
LOG_FILE=/var/log/django/app.log

# Backup
BACKUP_ENABLED=True
BACKUP_PATH=/var/backups/django/
BACKUP_RETENTION_DAYS=30
"""
    
    with open('env_production.txt', 'w', encoding='utf-8') as f:
        f.write(production_env)
    
    print("✅ Arquivo env_production.txt criado")
    print("📝 Use essas configurações como base para produção")


def main():
    """Função principal"""
    print("🔧 Configurador de Ambiente Django")
    print("=" * 40)
    
    # Criar arquivo .env para desenvolvimento
    create_env_file()
    
    # Criar configurações para produção
    create_production_env()
    
    print("\n🎉 Configuração concluída!")
    print("\n📋 Próximos passos:")
    print("1. Instale as dependências: pip install -r requirements.txt")
    print("2. Execute as migrações: python manage.py migrate")
    print("3. Crie um superusuário: python manage.py createsuperuser")
    print("4. Inicie o servidor: python manage.py runserver")
    
    print("\n🔒 Segurança:")
    print("- O arquivo .env está no .gitignore")
    print("- Nunca commite credenciais no Git")
    print("- Use variáveis de ambiente em produção")


if __name__ == "__main__":
    main()
