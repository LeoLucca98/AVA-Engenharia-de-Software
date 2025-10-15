# AVA Frontend - Angular Application

Frontend Angular para o AVA (Adaptive Virtual Assistant) - uma plataforma de aprendizado adaptativo com recomendações inteligentes.

## 🚀 Características

- **Angular 17** com standalone components
- **Angular Material** para UI/UX moderna
- **Autenticação JWT** com refresh automático
- **Roteamento protegido** com guards
- **Interceptors HTTP** para autenticação e tratamento de erros
- **Responsive design** para mobile e desktop
- **Docker** para containerização
- **Proxy configuration** para desenvolvimento

## 📁 Estrutura do Projeto

```
ava-frontend/
├── src/
│   ├── app/
│   │   ├── auth/                    # Módulo de autenticação
│   │   │   ├── login/              # Página de login
│   │   │   ├── register/           # Página de registro
│   │   │   └── auth.routes.ts      # Rotas de autenticação
│   │   ├── core/                   # Serviços e guards
│   │   │   ├── guards/             # Guards de autenticação
│   │   │   ├── interceptors/       # Interceptors HTTP
│   │   │   └── services/           # Serviços de API
│   │   ├── dashboard/              # Dashboard principal
│   │   ├── courses/                # Módulo de cursos
│   │   ├── lesson/                 # Visualizador de lições
│   │   ├── recommendations/        # Página de recomendações
│   │   ├── shared/                 # Componentes compartilhados
│   │   │   ├── components/         # Componentes reutilizáveis
│   │   │   └── models/             # Interfaces e tipos
│   │   ├── app.component.ts        # Componente principal
│   │   └── app.routes.ts           # Rotas principais
│   ├── environments/               # Configurações de ambiente
│   ├── index.html                  # HTML principal
│   ├── main.ts                     # Bootstrap da aplicação
│   └── styles.scss                 # Estilos globais
├── Dockerfile                      # Configuração Docker
├── nginx.conf                      # Configuração Nginx
├── proxy.conf.json                 # Proxy para desenvolvimento
├── package.json                    # Dependências e scripts
└── README.md                       # Este arquivo
```

## 🛠️ Pré-requisitos

- **Node.js** >= 18.0.0
- **npm** >= 8.0.0
- **Angular CLI** >= 17.0.0
- **Docker** (opcional, para containerização)

## 📦 Instalação

### 1. Clonar o Repositório

```bash
git clone <repository-url>
cd ava-frontend
```

### 2. Instalar Dependências

```bash
npm install
```

### 3. Configurar Ambiente

```bash
# Copiar arquivo de exemplo
cp src/environments/environment.example.ts src/environments/environment.ts

# Editar configurações se necessário
nano src/environments/environment.ts
```

## 🚀 Scripts Disponíveis

### Desenvolvimento

```bash
# Iniciar servidor de desenvolvimento com proxy
npm run dev

# Iniciar servidor de desenvolvimento padrão
npm start

# Build para desenvolvimento
npm run build

# Build para produção
npm run build:prod
```

### Testes

```bash
# Executar testes unitários
npm test

# Executar testes em modo CI
npm run test:ci

# Executar testes E2E
npm run e2e
```

### Qualidade de Código

```bash
# Executar linter
npm run lint

# Corrigir problemas de lint automaticamente
npm run lint:fix
```

### Produção

```bash
# Servir build de produção localmente
npm run serve:prod
```

## 🔧 Configuração

### Variáveis de Ambiente

O arquivo `src/environments/environment.ts` contém as configurações da aplicação:

```typescript
export const environment = {
  production: false,
  apiBaseUrl: 'http://localhost:8080',
  apiEndpoints: {
    auth: {
      login: '/auth/login/',
      register: '/auth/register/',
      refresh: '/auth/token/refresh/',
      user: '/auth/user/'
    },
    learning: {
      courses: '/learning/courses/',
      myCourses: '/learning/enrollments/my_courses/',
      // ... outros endpoints
    },
    recommendations: {
      recommendations: '/rec/recommendations/',
      userRecommendations: '/rec/recommendations/user'
    }
  },
  appConfig: {
    appName: 'AVA - Adaptive Virtual Assistant',
    version: '1.0.0',
    defaultPageSize: 20,
    tokenRefreshInterval: 300000, // 5 minutos
    sessionTimeout: 3600000 // 1 hora
  }
};
```

### Proxy para Desenvolvimento

O arquivo `proxy.conf.json` configura o proxy para redirecionar requisições para o API Gateway:

```json
{
  "/auth/*": {
    "target": "http://localhost:8080",
    "secure": false,
    "changeOrigin": true,
    "logLevel": "debug"
  },
  "/learning/*": {
    "target": "http://localhost:8080",
    "secure": false,
    "changeOrigin": true,
    "logLevel": "debug"
  },
  "/rec/*": {
    "target": "http://localhost:8080",
    "secure": false,
    "changeOrigin": true,
    "logLevel": "debug"
  }
}
```

## 🐳 Docker

### Build da Imagem

```bash
# Build da imagem
docker build -t ava-frontend .

# Build com tag específica
docker build -t ava-frontend:1.0.0 .
```

### Executar Container

```bash
# Executar em modo desenvolvimento
docker run -p 4200:80 ava-frontend

# Executar em background
docker run -d -p 4200:80 --name ava-frontend ava-frontend
```

### Docker Compose

```yaml
version: '3.8'
services:
  ava-frontend:
    build:
      context: ./ava-frontend
      dockerfile: Dockerfile
    ports:
      - "4200:80"
    environment:
      - NODE_ENV=production
    networks:
      - ava_net
```

## 🔐 Autenticação

### Fluxo de Autenticação

1. **Login/Registro** via AuthService
2. **Armazenamento de tokens** em sessionStorage
3. **Refresh automático** de tokens
4. **Interceptors** para anexar Authorization header
5. **Guards** para proteger rotas

### Exemplo de Uso

```typescript
// Login
this.authService.login({ email, password }).subscribe({
  next: (response) => {
    // Token armazenado automaticamente
    this.router.navigate(['/dashboard']);
  },
  error: (error) => {
    // Tratamento de erro
  }
});

// Verificar autenticação
if (this.authService.isAuthenticated()) {
  // Usuário autenticado
}

// Obter usuário atual
const user = this.authService.getCurrentUser();
```

## 🎨 UI/UX

### Angular Material

A aplicação utiliza Angular Material para componentes de UI:

- **MatToolbar** - Barra de navegação
- **MatSidenav** - Menu lateral
- **MatCard** - Cards de conteúdo
- **MatButton** - Botões
- **MatFormField** - Campos de formulário
- **MatSnackBar** - Notificações
- **MatProgressSpinner** - Loading indicators

### Tema Customizado

```scss
// Cores personalizadas
$custom-primary: mat-palette($mat-indigo);
$custom-accent: mat-palette($mat-pink, A200, A100, A400);
$custom-warn: mat-palette($mat-red);

$custom-theme: mat-light-theme((
  color: (
    primary: $custom-primary,
    accent: $custom-accent,
    warn: $custom-warn,
  )
));
```

### Responsive Design

A aplicação é totalmente responsiva com breakpoints:

- **Mobile**: < 768px
- **Tablet**: 768px - 1024px
- **Desktop**: > 1024px

## 📱 Páginas e Funcionalidades

### 1. **Login/Registro**
- Formulários com validação
- Integração com AuthService
- Redirecionamento automático

### 2. **Dashboard**
- Cards de cursos matriculados
- Recomendações personalizadas
- Cursos populares
- Estatísticas de progresso

### 3. **Cursos**
- Listagem de cursos disponíveis
- Filtros e busca
- Detalhes do curso
- Sistema de matrícula

### 4. **Lições**
- Visualizador de conteúdo
- Marcação de progresso
- Navegação entre lições
- Recursos adicionais

### 5. **Recomendações**
- Lista de recomendações
- Explicação do algoritmo
- Ações de interesse

## 🔄 Gerenciamento de Estado

### AuthService
- Estado do usuário atual
- Tokens de autenticação
- Refresh automático

### Serviços de API
- LearningApiService - Cursos e progresso
- RecApiService - Recomendações
- Cache de dados quando apropriado

## 🧪 Testes

### Testes Unitários

```bash
# Executar todos os testes
npm test

# Executar testes com coverage
npm run test:ci
```

### Testes E2E

```bash
# Executar testes E2E
npm run e2e
```

## 📊 Monitoramento

### Health Check

A aplicação expõe um endpoint de health check:

```bash
curl http://localhost:4200/health
```

### Logs

Logs são configurados no Nginx para produção:

- **Access logs**: `/var/log/nginx/access.log`
- **Error logs**: `/var/log/nginx/error.log`

## 🚀 Deploy

### Desenvolvimento

```bash
# Iniciar com proxy
npm run dev

# Acessar em http://localhost:4200
```

### Produção

```bash
# Build de produção
npm run build:prod

# Servir com Nginx
npm run serve:prod
```

### Docker

```bash
# Build e execução
docker build -t ava-frontend .
docker run -p 4200:80 ava-frontend
```

## 🔧 Troubleshooting

### Problemas Comuns

#### **Erro de CORS**
- Verificar se o API Gateway está rodando
- Confirmar configuração do proxy
- Verificar headers CORS no backend

#### **Erro de Autenticação**
- Verificar se os tokens estão sendo armazenados
- Confirmar configuração do JWT
- Verificar interceptors

#### **Erro de Build**
- Limpar cache: `npm run clean`
- Reinstalar dependências: `rm -rf node_modules && npm install`
- Verificar versões do Node.js e npm

#### **Erro de Proxy**
- Verificar se o API Gateway está acessível
- Confirmar configuração do proxy.conf.json
- Verificar logs do Angular CLI

### Comandos de Debug

```bash
# Verificar versões
node --version
npm --version
ng version

# Limpar cache
npm run clean
ng cache clean

# Verificar configuração
ng config
```

## 📚 Documentação Adicional

- [Angular Documentation](https://angular.io/docs)
- [Angular Material](https://material.angular.io/)
- [Angular CLI](https://cli.angular.io/)
- [Docker Documentation](https://docs.docker.com/)

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🆘 Suporte

Para suporte e dúvidas:

1. Verifique a documentação
2. Consulte os issues do repositório
3. Abra uma nova issue se necessário
4. Entre em contato com a equipe de desenvolvimento
