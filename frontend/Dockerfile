# ============================================
# Multi-stage build para otimizar a imagem
# ============================================

# Stage 1: Builder
FROM node:20-alpine as builder

WORKDIR /app

# Copiar package files
COPY package.json package-lock.json ./

# Instalar dependências
RUN npm ci

# Copiar código-fonte
COPY . .

# Build da aplicação
RUN npm run build

# Stage 2: Runtime (Nginx)
FROM nginx:alpine

WORKDIR /usr/share/nginx/html

# Remover config padrão do nginx
RUN rm -rf /etc/nginx/conf.d/default.conf

# Copiar build do stage anterior
COPY --from=builder /app/dist .

# Copiar configuração nginx customizada
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Criar usuário não-root por segurança
RUN addgroup -g 101 -S nginx && \
    adduser -S -D -H -u 101 -h /var/cache/nginx -s /sbin/nologin -G nginx -g nginx nginx

# Configurar permissões
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chown -R nginx:nginx /var/cache/nginx && \
    chown -R nginx:nginx /var/log/nginx && \
    chown -R nginx:nginx /etc/nginx/conf.d && \
    touch /var/run/nginx.pid && \
    chown -R nginx:nginx /var/run/nginx.pid

USER nginx

# Health check
HEALTHCHECK --interval=15s --timeout=5s --retries=5 \
    CMD wget --quiet --tries=1 --spider http://localhost:80 || exit 1

# Expor porta
EXPOSE 80

# Comando para iniciar nginx
CMD ["nginx", "-g", "daemon off;"]
