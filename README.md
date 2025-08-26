# 🔐 Sistema de Gerenciamento de Usuários Hierárquico

Sistema Django completo para gerenciamento de usuários com hierarquia de contas, APIs REST, autenticação e integração com React.

## ✅ **Status: 100% Pronto para React com Autenticação**

O sistema está **perfeitamente configurado** para trabalhar com React! Todas as APIs estão funcionando, protegidas e testadas.

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

### 3. **Testar Autenticação**
```bash
# Testar login
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@demo.com","senha":"Admin123!"}'

# Testar API protegida (sem login)
curl http://localhost:8000/api/usuarios/
# Deve retornar 401 - Usuário não autenticado
```

## 🔐 **Sistema de Autenticação**

### **Funcionalidades Implementadas**
- ✅ **Autenticação por Sessão** com cookies
- ✅ **Middleware automático** para verificar login
- ✅ **Rate Limiting** (100 requisições/hora)
- ✅ **Logs automáticos** de todas as requisições
- ✅ **Proteção de rotas** automática
- ✅ **APIs públicas e protegidas**

### **APIs Públicas (sem login)**
```javascript
POST /api/login/              // Login
POST /api/criar-admin-inicial/ // Criar primeiro admin
GET  /api/validar-senha/       // Validar senha
```

### **APIs Protegidas (precisam de login)**
```javascript
GET    /api/usuarios/          // Listar usuários
POST   /api/usuarios/          // Criar usuário
GET    /api/usuarios/{id}/     // Ver usuário
PUT    /api/usuarios/{id}/     // Atualizar usuário
DELETE /api/usuarios/{id}/     // Deletar usuário
POST   /api/usuarios/{id}/alterar-senha/ // Alterar senha
GET    /api/subcontas/         // Listar subcontas
POST   /api/logout/            // Logout
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
- ✅ **Rate limiting** automático
- ✅ **Logs de acesso** completos

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

### **Configuração Axios no React**
```javascript
const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  withCredentials: true, // IMPORTANTE para cookies
  headers: {
    'Content-Type': 'application/json',
  }
});
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

### **Testar Autenticação**
```bash
# Testar login
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@demo.com","senha":"Admin123!"}'

# Testar API protegida (sem login)
curl http://localhost:8000/api/usuarios/
# Deve retornar 401

# Testar API protegida (com login)
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@demo.com","senha":"Admin123!"}' \
  -c cookies.txt

curl http://localhost:8000/api/usuarios/ -b cookies.txt
# Deve retornar lista de usuários
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
│   ├── api_views.py     # APIs REST (PROTEGIDAS)
│   ├── middleware.py    # Middleware de autenticação
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
- ✅ **Rate limiting** ativo
- ✅ **Logs de acesso** completos

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
- 🔐 **[REACT_AUTH_GUIDE.md](REACT_AUTH_GUIDE.md)** - Guia de autenticação para React
- 🔒 **[SECURITY.md](SECURITY.md)** - Guia de segurança
- 📋 **[TESTES_RESUMO.md](TESTES_RESUMO.md)** - Resumo dos testes
- 📖 **[API_DOCS.md](API_DOCS.md)** - Documentação das APIs

## 🎉 **Conclusão**

O sistema está **100% funcional** e pronto para:

1. ✅ **Desenvolvimento com React** (com autenticação completa)
2. ✅ **Deploy em produção** (com segurança)
3. ✅ **Gerenciamento hierárquico** de usuários
4. ✅ **APIs REST protegidas** e funcionais
5. ✅ **Autenticação automática** em todas as rotas

**Próximo passo:** Criar seu projeto React e começar a desenvolver! 🚀

---

**Desenvolvido com ❤️ usando Django 5.2.3**
