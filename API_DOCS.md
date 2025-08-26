# API Documentation - Gerenciador de Usuários

Esta documentação descreve as rotas da API para integração com React.

## Base URL
```
http://localhost:8000
```

## Endpoints

### 1. Listar Usuários
**GET** `/api/usuarios/`

**Resposta:**
```json
[
  {
    "id": 1,
    "nome": "João Silva",
    "email": "joao@email.com",
    "foto": "/media/fotos/joao.jpg"
  }
]
```

### 2. Criar Usuário
**POST** `/api/usuarios/`

**Body (FormData):**
```javascript
const formData = new FormData();
formData.append('nome', 'João Silva');
formData.append('email', 'joao@email.com');
formData.append('senha', 'Senha123!');
formData.append('foto', file); // opcional
```

**Resposta de Sucesso (201):**
```json
{
  "id": 1,
  "nome": "João Silva",
  "email": "joao@email.com",
  "foto": "/media/fotos/joao.jpg",
  "mensagem": "Usuário criado com sucesso"
}
```

**Resposta de Erro (400):**
```json
{
  "erro": "Senha inválida",
  "detalhes": [
    "A senha deve ter pelo menos um caractere especial."
  ]
}
```

### 3. Buscar Usuário Específico
**GET** `/api/usuarios/{id}/`

**Resposta:**
```json
{
  "id": 1,
  "nome": "João Silva",
  "email": "joao@email.com",
  "foto": "/media/fotos/joao.jpg"
}
```

### 4. Atualizar Usuário
**PUT** `/api/usuarios/{id}/`

**Body (FormData):**
```javascript
const formData = new FormData();
formData.append('nome', 'João Silva Atualizado');
formData.append('email', 'joao.novo@email.com');
formData.append('foto', file); // opcional
```

### 5. Deletar Usuário
**DELETE** `/api/usuarios/{id}/`

**Resposta (204):**
```json
{
  "mensagem": "Usuário deletado com sucesso"
}
```

### 6. Alterar Senha
**POST** `/api/usuarios/{id}/alterar-senha/`

**Body (JSON):**
```json
{
  "senha": "NovaSenha123!"
}
```

**Resposta:**
```json
{
  "mensagem": "Senha alterada com sucesso"
}
```

### 7. Validar Senha
**GET** `/api/validar-senha/?senha=Senha123!`

**Resposta:**
```json
{
  "valida": true,
  "erros": []
}
```

## Requisitos de Senha

A senha deve conter:
- Mínimo de 8 caracteres
- Pelo menos um número
- Pelo menos uma letra
- Pelo menos uma letra maiúscula
- Pelo menos uma letra minúscula
- Pelo menos um caractere especial

## Exemplo de Uso com React

```javascript
// Listar usuários
const getUsuarios = async () => {
  const response = await fetch('http://localhost:8000/api/usuarios/');
  const data = await response.json();
  return data;
};

// Criar usuário
const criarUsuario = async (formData) => {
  const response = await fetch('http://localhost:8000/api/usuarios/', {
    method: 'POST',
    body: formData
  });
  return await response.json();
};

// Validar senha
const validarSenha = async (senha) => {
  const response = await fetch(`http://localhost:8000/api/validar-senha/?senha=${senha}`);
  return await response.json();
};
```

## CORS

A API está configurada para aceitar requisições dos seguintes domínios:
- http://localhost:3000 (React padrão)
- http://localhost:5173 (Vite)
- http://127.0.0.1:3000
- http://127.0.0.1:5173
