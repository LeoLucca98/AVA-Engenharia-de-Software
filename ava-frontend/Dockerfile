# ---------- build ----------
FROM node:20-alpine AS build
WORKDIR /app

# Copia os manifests primeiro (para cache de dependências)
COPY package*.json ./

# Se existir package-lock.json, use npm ci; senão, npm install
# Precisa das devDependencies para o build do Angular
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi

# Copia o restante do código
COPY . .

# memória extra para builds grandes (opcional)
ENV NODE_OPTIONS=--max_old_space_size=4096

# Build de produção (ajuste --configuration se necessário)
RUN npm run build -- --configuration=production

# ---------- runtime ----------
FROM nginx:alpine
# Healthcheck básico
HEALTHCHECK CMD wget -qO- http://localhost/healthz || exit 1

# Copia artefatos do Angular para o Nginx
# Caminho conforme angular.json (outputPath: dist/ava-frontend)
COPY --from=build /app/dist/ava-frontend /usr/share/nginx/html

# Usa a configuração completa do Nginx fornecida no projeto
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80