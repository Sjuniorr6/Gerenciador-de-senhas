# 🔐 Guia de Autenticação para React

## ✅ **Sistema de Autenticação Implementado**

O Django agora tem **autenticação completa** com proteção de rotas! Aqui está como usar no React:

## 🔧 **Como Funciona**

### **1. Autenticação por Sessão**
- ✅ Login cria sessão no servidor
- ✅ Cookies são enviados automaticamente
- ✅ Middleware verifica autenticação em todas as APIs
- ✅ Rate limiting automático (100 req/hora)

### **2. Rotas Protegidas**
- ✅ **APIs Públicas**: Login, criar admin, validar senha
- ✅ **APIs Protegidas**: Todas as outras (usuários, subcontas, etc.)
- ✅ **Verificação automática** de permissões

## 🚀 **Como Usar no React**

### **1. Configurar Axios**
```javascript
// api.js
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

// Configurar credenciais para cookies
const api = axios.create({
  baseURL: API_BASE,
  withCredentials: true, // IMPORTANTE para cookies
  headers: {
    'Content-Type': 'application/json',
  }
});

// Interceptor para tratar erros de autenticação
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Redirecionar para login
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
```

### **2. Login**
```javascript
// auth.js
import api from './api';

export const login = async (email, senha) => {
  try {
    const response = await api.post('/login/', {
      email,
      senha
    });
    
    if (response.data) {
      // Login bem-sucedido
      localStorage.setItem('user', JSON.stringify(response.data));
      return response.data;
    }
  } catch (error) {
    console.error('Erro no login:', error.response?.data);
    throw error;
  }
};

export const logout = async () => {
  try {
    await api.post('/logout/');
    localStorage.removeItem('user');
    window.location.href = '/login';
  } catch (error) {
    console.error('Erro no logout:', error);
  }
};

export const checkAuth = () => {
  const user = localStorage.getItem('user');
  return user ? JSON.parse(user) : null;
};
```

### **3. Componente de Login**
```jsx
// Login.jsx
import React, { useState } from 'react';
import { login } from './auth';

function Login() {
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const user = await login(email, senha);
      console.log('Login bem-sucedido:', user);
      // Redirecionar para dashboard
      window.location.href = '/dashboard';
    } catch (error) {
      setError(error.response?.data?.erro || 'Erro no login');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>Login</h2>
      {error && <p style={{color: 'red'}}>{error}</p>}
      
      <form onSubmit={handleSubmit}>
        <div>
          <label>Email:</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        
        <div>
          <label>Senha:</label>
          <input
            type="password"
            value={senha}
            onChange={(e) => setSenha(e.target.value)}
            required
          />
        </div>
        
        <button type="submit" disabled={loading}>
          {loading ? 'Entrando...' : 'Entrar'}
        </button>
      </form>
    </div>
  );
}

export default Login;
```

### **4. Componente Protegido**
```jsx
// Dashboard.jsx
import React, { useState, useEffect } from 'react';
import api from './api';
import { checkAuth, logout } from './auth';

function Dashboard() {
  const [usuarios, setUsuarios] = useState([]);
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState(null);

  useEffect(() => {
    const currentUser = checkAuth();
    if (!currentUser) {
      window.location.href = '/login';
      return;
    }
    
    setUser(currentUser);
    carregarUsuarios();
  }, []);

  const carregarUsuarios = async () => {
    try {
      const response = await api.get('/usuarios/');
      setUsuarios(response.data);
    } catch (error) {
      console.error('Erro ao carregar usuários:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
  };

  if (loading) return <div>Carregando...</div>;

  return (
    <div>
      <h2>Dashboard</h2>
      <p>Bem-vindo, {user?.nome}!</p>
      <p>Tipo: {user?.tipo_display}</p>
      
      <button onClick={handleLogout}>Sair</button>
      
      <h3>Usuários</h3>
      <ul>
        {usuarios.map(usuario => (
          <li key={usuario.id}>
            {usuario.nome} - {usuario.email} ({usuario.tipo_display})
          </li>
        ))}
      </ul>
    </div>
  );
}

export default Dashboard;
```

### **5. Roteamento Protegido**
```jsx
// App.jsx
import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login from './Login';
import Dashboard from './Dashboard';
import { checkAuth } from './auth';

// Componente para rotas protegidas
function ProtectedRoute({ children }) {
  const user = checkAuth();
  
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  
  return children;
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route 
          path="/dashboard" 
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } 
        />
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
```

## 🔒 **APIs Protegidas vs Públicas**

### **APIs Públicas (sem autenticação)**
```javascript
// ✅ Não precisam de login
POST /api/login/
POST /api/criar-admin-inicial/
GET  /api/validar-senha/
```

### **APIs Protegidas (precisam de login)**
```javascript
// ❌ Precisam de login
GET    /api/usuarios/
POST   /api/usuarios/
GET    /api/usuarios/{id}/
PUT    /api/usuarios/{id}/
DELETE /api/usuarios/{id}/
POST   /api/usuarios/{id}/alterar-senha/
GET    /api/subcontas/
POST   /api/logout/
```

## 🛡️ **Segurança Implementada**

### **1. Autenticação Automática**
- ✅ Middleware verifica todas as requisições
- ✅ Sessões inválidas são limpas automaticamente
- ✅ Rate limiting (100 req/hora)

### **2. Proteção de Rotas**
- ✅ APIs protegidas retornam 401 se não autenticado
- ✅ Verificação de permissões por tipo de usuário
- ✅ Logs de todas as requisições

### **3. Tratamento de Erros**
```javascript
// Exemplos de respostas de erro
{
  "error": "Usuário não autenticado",
  "message": "Faça login para acessar este recurso"
}

{
  "error": "Rate limit exceeded",
  "message": "Máximo de 100 requisições por hora"
}

{
  "error": "Acesso negado",
  "message": "Apenas administradores podem acessar este recurso"
}
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

## 🚀 **Como Testar**

### **1. Backend**
```bash
python manage.py runserver
```

### **2. Frontend**
```bash
npx create-react-app frontend
cd frontend
npm install axios react-router-dom
npm start
```

### **3. Testar APIs**
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

## ✅ **Vantagens**

1. **Segurança**: Autenticação automática em todas as APIs
2. **Simplicidade**: Cookies gerenciados automaticamente
3. **Rate Limiting**: Proteção contra abuso
4. **Logs**: Monitoramento de todas as requisições
5. **Compatibilidade**: Funciona perfeitamente com React

**O sistema está 100% pronto para React com autenticação completa!** 🎉
