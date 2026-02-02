# ============================================
# Multi-stage build para otimizar a imagem
# ============================================

# Stage 1: Builder
FROM python:3.12-slim as builder

WORKDIR /build

# Instalar dependências do sistema necessárias
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e criar wheels
COPY requirements.txt .
RUN pip install --user --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.12-slim

WORKDIR /app

# Instalar apenas dependências de runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Criar usuário não-root por segurança
RUN useradd -m -u 1000 appuser

# Copiar pacotes Python do builder com permissões corretas
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local

# Copiar código da aplicação
COPY --chown=appuser:appuser ./app ./app
COPY --chown=appuser:appuser ./migrations ./migrations
COPY --chown=appuser:appuser alembic.ini .

# Configurar PATH
ENV PATH=/home/appuser/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Trocar para usuário não-root
USER appuser

# Health check
HEALTHCHECK --interval=15s --timeout=5s --retries=5 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Expor porta
EXPOSE 8000

# Comando de inicialização
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

