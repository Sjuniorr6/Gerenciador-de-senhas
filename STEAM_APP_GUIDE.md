# 🎬 App Steam - Gerenciador de Contas de Streaming

## ✅ **App Steam Criado com Sucesso!**

O app **steam** foi criado com funcionalidades completas para gerenciar contas de streaming com compartilhamento e histórico de acessos.

## 🎯 **Funcionalidades Implementadas**

### **📺 Gerenciamento de Contas**
- ✅ **CRUD completo** de contas de streaming
- ✅ **16 plataformas** suportadas (Netflix, Disney+, HBO Max, etc.)
- ✅ **Senhas criptografadas** automaticamente
- ✅ **Upload de fotos** para cada conta
- ✅ **Status de conta** (Ativo, Inativo, Pendente, Expirado)
- ✅ **Data de expiração** com alertas automáticos

### **🤝 Sistema de Compartilhamento**
- ✅ **Compartilhamento** de contas entre usuários
- ✅ **3 níveis de acesso**: Leitura, Acesso Completo, Administrador
- ✅ **Permissões granulares** por usuário
- ✅ **Controle total** do proprietário

### **📊 Histórico e Monitoramento**
- ✅ **Histórico de acessos** com IP e User Agent
- ✅ **Taxa de sucesso** de logins
- ✅ **Observações** para cada acesso
- ✅ **Estatísticas** completas

## 🚀 **APIs Disponíveis**

### **APIs Principais (Protegidas)**
```javascript
// Contas de Streaming
GET    /api/streaming/                    // Listar contas
POST   /api/streaming/                    // Criar conta
GET    /api/streaming/{id}/               // Ver conta
PUT    /api/streaming/{id}/               // Atualizar conta
DELETE /api/streaming/{id}/               // Deletar conta

// Compartilhamento
POST   /api/streaming/{id}/compartilhar/  // Compartilhar conta
DELETE /api/streaming/{id}/descompartilhar/{usuario_id}/ // Remover compartilhamento

// Auxiliares
GET    /api/streaming/plataformas/        // Listar plataformas
GET    /api/streaming/status/             // Listar status
```

## 📋 **Modelo de Dados**

### **ContaStreaming**
```javascript
{
  id: 1,
  nome: "Netflix Premium",
  plataforma: "netflix",
  plataforma_display: "Netflix",
  email: "admin@netflix.com",
  usuario: "admin_user",
  senha: "Netflix123!", // descriptografada apenas na visualização
  foto: "/media/streaming_fotos/netflix.jpg",
  descricao: "Conta Netflix Premium com 4 telas",
  status: "ativo",
  status_display: "Ativo",
  data_criacao: "2025-08-26T16:30:00Z",
  data_expiracao: "2026-08-26",
  ultimo_acesso: "2025-08-26T16:35:00Z",
  proprietario: {
    id: 1,
    nome: "Admin Principal",
    email: "admin@demo.com"
  },
  is_proprietario: true,
  pode_editar: true,
  pode_deletar: true
}
```

### **Plataformas Suportadas**
```javascript
[
  { codigo: "netflix", nome: "Netflix" },
  { codigo: "disney", nome: "Disney+" },
  { codigo: "hbo", nome: "HBO Max" },
  { codigo: "prime", nome: "Amazon Prime" },
  { codigo: "paramount", nome: "Paramount+" },
  { codigo: "starz", nome: "Starz" },
  { codigo: "apple", nome: "Apple TV+" },
  { codigo: "hulu", nome: "Hulu" },
  { codigo: "peacock", nome: "Peacock" },
  { codigo: "crunchyroll", nome: "Crunchyroll" },
  { codigo: "funimation", nome: "Funimation" },
  { codigo: "youtube", nome: "YouTube Premium" },
  { codigo: "spotify", nome: "Spotify" },
  { codigo: "deezer", nome: "Deezer" },
  { codigo: "tidal", nome: "Tidal" },
  { codigo: "outros", nome: "Outros" }
]
```

## 🔧 **Como Usar no React**

### **1. Configurar API**
```javascript
// api.js
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  }
});

export default api;
```

### **2. Serviços de Streaming**
```javascript
// streamingService.js
import api from './api';

export const streamingService = {
  // Listar contas
  listarContas: async () => {
    const response = await api.get('/streaming/');
    return response.data;
  },

  // Criar conta
  criarConta: async (dados) => {
    const formData = new FormData();
    
    // Adicionar campos básicos
    Object.keys(dados).forEach(key => {
      if (key !== 'foto') {
        formData.append(key, dados[key]);
      }
    });
    
    // Adicionar foto se existir
    if (dados.foto) {
      formData.append('foto', dados.foto);
    }
    
    const response = await api.post('/streaming/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      }
    });
    return response.data;
  },

  // Ver conta
  verConta: async (id) => {
    const response = await api.get(`/streaming/${id}/`);
    return response.data;
  },

  // Atualizar conta
  atualizarConta: async (id, dados) => {
    const formData = new FormData();
    
    Object.keys(dados).forEach(key => {
      if (key !== 'foto') {
        formData.append(key, dados[key]);
      }
    });
    
    if (dados.foto) {
      formData.append('foto', dados.foto);
    }
    
    const response = await api.put(`/streaming/${id}/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      }
    });
    return response.data;
  },

  // Deletar conta
  deletarConta: async (id) => {
    await api.delete(`/streaming/${id}/`);
  },

  // Compartilhar conta
  compartilharConta: async (id, email, nivelAcesso = 'leitura') => {
    const response = await api.post(`/streaming/${id}/compartilhar/`, {
      email,
      nivel_acesso: nivelAcesso
    });
    return response.data;
  },

  // Remover compartilhamento
  removerCompartilhamento: async (id, usuarioId) => {
    await api.delete(`/streaming/${id}/descompartilhar/${usuarioId}/`);
  },

  // Listar plataformas
  listarPlataformas: async () => {
    const response = await api.get('/streaming/plataformas/');
    return response.data;
  },

  // Listar status
  listarStatus: async () => {
    const response = await api.get('/streaming/status/');
    return response.data;
  }
};
```

### **3. Componente de Listagem**
```jsx
// StreamingList.jsx
import React, { useState, useEffect } from 'react';
import { streamingService } from './streamingService';

function StreamingList() {
  const [contas, setContas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    carregarContas();
  }, []);

  const carregarContas = async () => {
    try {
      const data = await streamingService.listarContas();
      setContas(data);
    } catch (error) {
      setError('Erro ao carregar contas');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleDeletar = async (id) => {
    if (window.confirm('Tem certeza que deseja deletar esta conta?')) {
      try {
        await streamingService.deletarConta(id);
        carregarContas(); // Recarregar lista
      } catch (error) {
        setError('Erro ao deletar conta');
      }
    }
  };

  if (loading) return <div>Carregando contas...</div>;
  if (error) return <div style={{color: 'red'}}>{error}</div>;

  return (
    <div>
      <h2>Minhas Contas de Streaming</h2>
      
      <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '20px'}}>
        {contas.map(conta => (
          <div key={conta.id} style={{border: '1px solid #ddd', padding: '15px', borderRadius: '8px'}}>
            <h3>{conta.nome}</h3>
            <p><strong>Plataforma:</strong> {conta.plataforma_display}</p>
            <p><strong>Email:</strong> {conta.email}</p>
            <p><strong>Status:</strong> {conta.status_display}</p>
            <p><strong>Proprietário:</strong> {conta.proprietario.nome}</p>
            
            {conta.foto && (
              <img src={conta.foto} alt={conta.nome} style={{width: '100px', height: '100px', objectFit: 'cover'}} />
            )}
            
            <div style={{marginTop: '10px'}}>
              <button onClick={() => window.location.href = `/streaming/${conta.id}`}>
                Ver Detalhes
              </button>
              
              {conta.pode_editar && (
                <button onClick={() => window.location.href = `/streaming/${conta.id}/editar`}>
                  Editar
                </button>
              )}
              
              {conta.pode_deletar && (
                <button onClick={() => handleDeletar(conta.id)} style={{backgroundColor: 'red', color: 'white'}}>
                  Deletar
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default StreamingList;
```

### **4. Componente de Criação**
```jsx
// StreamingForm.jsx
import React, { useState, useEffect } from 'react';
import { streamingService } from './streamingService';

function StreamingForm() {
  const [formData, setFormData] = useState({
    nome: '',
    plataforma: 'netflix',
    email: '',
    usuario: '',
    senha: '',
    descricao: '',
    status: 'ativo',
    data_expiracao: '',
    foto: null
  });
  
  const [plataformas, setPlataformas] = useState([]);
  const [status, setStatus] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    carregarDados();
  }, []);

  const carregarDados = async () => {
    try {
      const [plataformasData, statusData] = await Promise.all([
        streamingService.listarPlataformas(),
        streamingService.listarStatus()
      ]);
      setPlataformas(plataformasData);
      setStatus(statusData);
    } catch (error) {
      setError('Erro ao carregar dados');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await streamingService.criarConta(formData);
      alert('Conta criada com sucesso!');
      window.location.href = '/streaming';
    } catch (error) {
      setError(error.response?.data?.erro || 'Erro ao criar conta');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value, files } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: files ? files[0] : value
    }));
  };

  return (
    <div>
      <h2>Criar Nova Conta de Streaming</h2>
      
      {error && <p style={{color: 'red'}}>{error}</p>}
      
      <form onSubmit={handleSubmit}>
        <div>
          <label>Nome da Conta:</label>
          <input
            type="text"
            name="nome"
            value={formData.nome}
            onChange={handleChange}
            required
          />
        </div>
        
        <div>
          <label>Plataforma:</label>
          <select name="plataforma" value={formData.plataforma} onChange={handleChange}>
            {plataformas.map(plat => (
              <option key={plat.codigo} value={plat.codigo}>
                {plat.nome}
              </option>
            ))}
          </select>
        </div>
        
        <div>
          <label>Email:</label>
          <input
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            required
          />
        </div>
        
        <div>
          <label>Usuário (opcional):</label>
          <input
            type="text"
            name="usuario"
            value={formData.usuario}
            onChange={handleChange}
          />
        </div>
        
        <div>
          <label>Senha:</label>
          <input
            type="password"
            name="senha"
            value={formData.senha}
            onChange={handleChange}
            required
          />
        </div>
        
        <div>
          <label>Descrição:</label>
          <textarea
            name="descricao"
            value={formData.descricao}
            onChange={handleChange}
          />
        </div>
        
        <div>
          <label>Status:</label>
          <select name="status" value={formData.status} onChange={handleChange}>
            {status.map(st => (
              <option key={st.codigo} value={st.codigo}>
                {st.nome}
              </option>
            ))}
          </select>
        </div>
        
        <div>
          <label>Data de Expiração:</label>
          <input
            type="date"
            name="data_expiracao"
            value={formData.data_expiracao}
            onChange={handleChange}
          />
        </div>
        
        <div>
          <label>Foto:</label>
          <input
            type="file"
            name="foto"
            accept="image/*"
            onChange={handleChange}
          />
        </div>
        
        <button type="submit" disabled={loading}>
          {loading ? 'Criando...' : 'Criar Conta'}
        </button>
      </form>
    </div>
  );
}

export default StreamingForm;
```

## 📊 **Dados de Teste Criados**

O script `test_steam.py` criou:

- ✅ **4 contas de streaming** (Netflix, Disney+, Spotify, HBO Max)
- ✅ **3 compartilhamentos** entre usuários
- ✅ **3 registros de histórico** de acesso
- ✅ **Estatísticas completas** do sistema

## 🧪 **Como Testar**

### **1. Executar Teste**
```bash
python test_steam.py
```

### **2. Testar APIs**
```bash
# Login
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@demo.com","senha":"Admin123!"}' \
  -c cookies.txt

# Listar contas
curl http://localhost:8000/api/streaming/ -b cookies.txt

# Ver plataformas
curl http://localhost:8000/api/streaming/plataformas/ -b cookies.txt
```

## ✅ **Vantagens do App Steam**

1. **🎯 Foco Específico**: Dedicado apenas para contas de streaming
2. **🔐 Segurança**: Senhas criptografadas automaticamente
3. **🤝 Compartilhamento**: Sistema robusto de permissões
4. **📊 Monitoramento**: Histórico completo de acessos
5. **📱 Flexibilidade**: Suporte a 16 plataformas diferentes
6. **🖼️ Visual**: Upload de fotos para cada conta
7. **⏰ Controle**: Datas de expiração e status
8. **🔒 Proteção**: APIs protegidas com autenticação

**O app steam está 100% funcional e pronto para React!** 🎉
