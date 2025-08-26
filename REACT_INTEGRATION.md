# 🚀 Integração com React - Guia Completo

## ✅ **Sistema 100% Pronto para React**

O Django está **perfeitamente configurado** para trabalhar com React! Aqui está tudo que você precisa saber:

## 🔧 **Configurações Já Implementadas**

### 1. **CORS Configurado**
```python
# settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React dev server
    "http://127.0.0.1:3000",
    "http://localhost:5173",  # Vite dev server
    "http://127.0.0.1:5173",
]
CORS_ALLOW_CREDENTIALS = True
```

### 2. **APIs REST Prontas**
```javascript
// Endpoints disponíveis no React:
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

### 3. **Autenticação por Sessão**
- ✅ Cookies configurados para CORS
- ✅ Sessões seguras
- ✅ CSRF protection

### 4. **Variáveis de Ambiente**
- ✅ `.env` configurado
- ✅ `python-dotenv` instalado
- ✅ Configurações sensíveis protegidas

## 🎯 **Como Usar no React**

### 1. **Configurar Axios/Fetch**
```javascript
// api.js
const API_BASE = 'http://localhost:8000/api';

// Configurar credenciais para cookies
const api = axios.create({
  baseURL: API_BASE,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  }
});
```

### 2. **Login**
```javascript
// Login
const login = async (email, senha) => {
  try {
    const response = await api.post('/login/', {
      email,
      senha
    });
    
    if (response.data.success) {
      // Usuário logado com sucesso
      return response.data.usuario;
    }
  } catch (error) {
    console.error('Erro no login:', error);
  }
};
```

### 3. **Criar Usuário**
```javascript
// Criar usuário
const criarUsuario = async (dados) => {
  try {
    const response = await api.post('/usuarios/', {
      nome: dados.nome,
      email: dados.email,
      senha: dados.senha,
      tipo: dados.tipo
    });
    
    return response.data;
  } catch (error) {
    console.error('Erro ao criar usuário:', error);
  }
};
```

### 4. **Listar Usuários**
```javascript
// Listar usuários
const listarUsuarios = async () => {
  try {
    const response = await api.get('/usuarios/');
    return response.data;
  } catch (error) {
    console.error('Erro ao listar usuários:', error);
  }
};
```

### 5. **Gerenciar Subcontas**
```javascript
// Listar subcontas
const listarSubcontas = async () => {
  try {
    const response = await api.get('/subcontas/');
    return response.data;
  } catch (error) {
    console.error('Erro ao listar subcontas:', error);
  }
};
```

## 🔐 **Sistema de Permissões**

### Hierarquia de Usuários:
```javascript
// Tipos de usuário
const TIPOS_USUARIO = {
  ADMIN: 'admin',      // Pode criar gerentes e usuários
  GERENTE: 'gerente',  // Pode criar usuários
  USUARIO: 'usuario'   // Não pode criar subcontas
};

// Verificar permissões no frontend
const podeCriarSubcontas = (tipoUsuario) => {
  return tipoUsuario === 'admin' || tipoUsuario === 'gerente';
};

const podeGerenciarUsuario = (usuarioLogado, usuarioAlvo) => {
  // Implementar lógica baseada na hierarquia
  return usuarioLogado.tipo === 'admin' || 
         (usuarioLogado.tipo === 'gerente' && usuarioAlvo.tipo === 'usuario');
};
```

## 📱 **Exemplo de Componente React**

```jsx
import React, { useState, useEffect } from 'react';
import api from './api';

function GerenciarUsuarios() {
  const [usuarios, setUsuarios] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    carregarUsuarios();
  }, []);

  const carregarUsuarios = async () => {
    try {
      const data = await api.get('/usuarios/');
      setUsuarios(data);
    } catch (error) {
      console.error('Erro ao carregar usuários:', error);
    } finally {
      setLoading(false);
    }
  };

  const criarUsuario = async (dados) => {
    try {
      await api.post('/usuarios/', dados);
      carregarUsuarios(); // Recarregar lista
    } catch (error) {
      console.error('Erro ao criar usuário:', error);
    }
  };

  if (loading) return <div>Carregando...</div>;

  return (
    <div>
      <h2>Gerenciar Usuários</h2>
      <ul>
        {usuarios.map(usuario => (
          <li key={usuario.id}>
            {usuario.nome} - {usuario.email} ({usuario.tipo})
          </li>
        ))}
      </ul>
    </div>
  );
}

export default GerenciarUsuarios;
```

## 🚀 **Iniciar Desenvolvimento**

### 1. **Backend (Django)**
```bash
# Terminal 1
python manage.py runserver
# Servidor rodando em: http://localhost:8000
```

### 2. **Frontend (React)**
```bash
# Terminal 2
npx create-react-app frontend
cd frontend
npm start
# React rodando em: http://localhost:3000
```

### 3. **Testar Integração**
```bash
# Testar APIs
curl -X GET http://localhost:8000/api/usuarios/
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@demo.com","senha":"Admin123!"}'
```

## 🔧 **Configurações de Desenvolvimento**

### **React (package.json)**
```json
{
  "proxy": "http://localhost:8000",
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build"
  }
}
```

### **Vite (vite.config.js)**
```javascript
export default {
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
}
```

## 📊 **Dados de Teste Disponíveis**

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

## ✅ **Checklist de Integração**

- [x] **CORS configurado** para React
- [x] **APIs REST** funcionando
- [x] **Autenticação** por sessão
- [x] **Variáveis de ambiente** configuradas
- [x] **Sistema de permissões** implementado
- [x] **Validação de senhas** ativa
- [x] **Logs** configurados
- [x] **Segurança** implementada

## 🎉 **Conclusão**

O sistema está **100% pronto** para React! Você pode:

1. **Iniciar o desenvolvimento** imediatamente
2. **Usar todas as APIs** sem configuração adicional
3. **Implementar autenticação** com sessões
4. **Gerenciar hierarquia** de usuários
5. **Deploy em produção** com segurança

**Próximo passo:** Criar seu projeto React e começar a desenvolver! 🚀
