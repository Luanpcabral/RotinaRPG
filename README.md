# Productivity App

Um aplicativo de produtividade gamificado com sistema de pets, conquistas e tarefas.

## Funcionalidades

- Sistema de tarefas com XP e moedas
- Pets colecionáveis com diferentes raridades
- Sistema de conquistas
- Timer Pomodoro
- Loja virtual
- Sistema de níveis e avatares

## Tecnologias

- **Backend**: Flask + SQLAlchemy
- **Frontend**: React + Vite
- **Banco de dados**: SQLite
- **Estilo**: CSS personalizado

## Como executar

### Desenvolvimento local

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Execute a aplicação:
```bash
python src/main.py
```

3. Acesse: http://localhost:5001

### Deploy

O projeto está configurado para deploy automático. Qualquer push para a branch main irá atualizar a versão online.

## Estrutura do projeto

```
src/
├── main.py              # Arquivo principal da aplicação
├── models/              # Modelos do banco de dados
├── routes/              # Rotas da API
├── utils/               # Utilitários
└── static/              # Frontend buildado
```

## API Endpoints

- `/api/user` - Gerenciamento de usuários
- `/api/tasks` - Sistema de tarefas
- `/api/achievements` - Conquistas
- `/api/store` - Loja virtual
- `/api/timer` - Timer Pomodoro
- `/api/pets` - Sistema de pets

