# 🔐 Sistema de Gerenciamento de Usuários Hierárquico

Sistema Django completo para gerenciamento de usuários com hierarquia de contas, APIs REST e integração com React.

## ✅ **Status: 100% Pronto para React**

O sistema está **perfeitamente configurado** para trabalhar com React! Todas as APIs estão funcionando e testadas.

## 🚀 **Início Rápido**

### 1. **Configurar Ambiente**
```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar arquivo .env (gerado automaticamente)
python setup_env.py

# Executar migrações
python manage.py migrate
```

### 2. **Iniciar Servidor**
```bash
python manage.py runserver
# Servidor rodando em: http://localhost:8000
```

### 3. **Testar APIs**
```bash
# Listar usuários
curl http://localhost:8000/api/usuarios/

# Validar senha
curl http://localhost:8000/api/validar-senha/?senha=Senha123!
```

## 🎯 **Funcionalidades Principais**

### **Sistema de Hierarquia**
- ✅ **Admin**: Pode criar gerentes e usuários
- ✅ **Gerente**: Pode criar usuários (subcontas)
- ✅ **Usuário**: Não pode criar subcontas
- ✅ **Hierarquia completa** com níveis ilimitados

### **APIs REST Completas**
- ✅ **Autenticação**: Login/Logout com sessões
- ✅ **CRUD Usuários**: Criar, listar, atualizar, deletar
- ✅ **Gerenciamento de Senhas**: Alterar e validar
- ✅ **Subcontas**: Listar hierarquia completa
- ✅ **Permissões**: Verificação automática

### **Segurança**
- ✅ **Hash de senhas** automático (pbkdf2_sha256)
- ✅ **Validação rigorosa** de senhas
- ✅ **CORS configurado** para React
- ✅ **CSRF protection** ativo
- ✅ **Variáveis de ambiente** protegidas

## 🔧 **Configuração para React**

### **CORS Configurado**
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React dev server
    "http://127.0.0.1:3000",
    "http://localhost:5173",  # Vite dev server
    "http://127.0.0.1:5173",
]
CORS_ALLOW_CREDENTIALS = True
```

### **APIs Disponíveis**
```javascript
const API_BASE = 'http://localhost:8000/api';

// Autenticação
POST   /api/login/
POST   /api/logout/
POST   /api/criar-admin-inicial/

// Usuários
GET    /api/usuarios/
POST   /api/usuarios/
GET    /api/usuarios/{id}/
PUT    /api/usuarios/{id}/
DELETE /api/usuarios/{id}/

// Senhas
POST   /api/usuarios/{id}/alterar-senha/
POST   /api/validar-senha/

// Subcontas
GET    /api/subcontas/
```

## 📊 **Dados de Teste**

```javascript
// Usuários para teste
const USUARIOS_TESTE = {
  admin: {
    email: 'admin@demo.com',
    senha: 'Admin123!'
  },
  gerente: {
    email: 'gerente@demo.com', 
    senha: 'Gerente123!'
  },
  usuario: {
    email: 'usuario@demo.com',
    senha: 'Usuario123!'
  }
};
```

## 🧪 **Testes**

### **Executar Todos os Testes**
```bash
python manage.py test usuarios.tests -v 2
```

### **Executar Demonstração**
```bash
python demo_system.py
```

### **Testes Específicos**
```bash
# Testes de modelo
python manage.py test usuarios.tests.UsuarioModelTest -v 2

# Testes de API
python manage.py test usuarios.tests.APITest -v 2

# Testes de formulários
python manage.py test usuarios.tests.UsuarioFormTest -v 2
```

## 📁 **Estrutura do Projeto**

```
senhas/
├── gerenciador/          # Projeto Django
│   ├── settings.py      # Configurações (com .env)
│   └── urls.py          # URLs principais
├── usuarios/            # App principal
│   ├── models.py        # Modelo Usuario
│   ├── views.py         # Views tradicionais
│   ├── api_views.py     # APIs REST
│   ├── forms.py         # Formulários
│   ├── tests.py         # Testes unitários
│   └── urls.py          # URLs do app
├── .env                 # Variáveis de ambiente (não versionado)
├── .gitignore           # Arquivos ignorados
├── requirements.txt     # Dependências
├── setup_env.py         # Script de configuração
├── demo_system.py       # Demonstração do sistema
└── README.md           # Este arquivo
```

## 🔒 **Segurança**

### **Arquivos Protegidos**
- ✅ `.env` - Variáveis de ambiente
- ✅ `*.sqlite3` - Banco de dados
- ✅ `media/` - Uploads
- ✅ `logs/` - Arquivos de log
- ✅ `__pycache__/` - Cache Python

### **Configurações de Segurança**
- ✅ **DEBUG=False** em produção
- ✅ **SECRET_KEY** única e segura
- ✅ **ALLOWED_HOSTS** configurado
- ✅ **HTTPS** recomendado para produção
- ✅ **Backup automático** configurado

## 🚀 **Deploy em Produção**

### **1. Configurar .env para Produção**
```env
DEBUG=False
SECRET_KEY=sua_chave_secreta_aqui
ALLOWED_HOSTS=seudominio.com,www.seudominio.com
DATABASE_ENGINE=django.db.backends.postgresql
```

### **2. Banco de Dados**
```bash
# PostgreSQL recomendado
pip install psycopg2-binary
```

### **3. Servidor Web**
```bash
# Gunicorn + Nginx recomendado
pip install gunicorn
```

## 📚 **Documentação**

- 📖 **[REACT_INTEGRATION.md](REACT_INTEGRATION.md)** - Guia completo para React
- 🔒 **[SECURITY.md](SECURITY.md)** - Guia de segurança
- 📋 **[TESTES_RESUMO.md](TESTES_RESUMO.md)** - Resumo dos testes
- 📖 **[API_DOCS.md](API_DOCS.md)** - Documentação das APIs

## 🎉 **Conclusão**

O sistema está **100% funcional** e pronto para:

1. ✅ **Desenvolvimento com React**
2. ✅ **Deploy em produção**
3. ✅ **Gerenciamento hierárquico de usuários**
4. ✅ **APIs REST completas**
5. ✅ **Segurança implementada**

**Próximo passo:** Criar seu projeto React e começar a desenvolver! 🚀

---

**Desenvolvido com ❤️ usando Django 5.2.3**
