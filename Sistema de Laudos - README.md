# Sistema de Laudos

Sistema de documentoscopia geração de laudo de analise contestação.

O sistema coleta informações de múltiplas fontes, executa análises especializadas, permite edição manual (prints, imagens e textos), os dados da analise são salvos em um Banco de Dados e o sistema possui uma tela de FrontEnd para importação de documentos e que gera uma prévia visual do laudo de analise, essa tela também possui um botão com a função de exportação do laudo da análise em formato PDF.

O sistema é composto possui uma arquitetura de microserviços e é composto por:

1 - FrontEnd web para a interação do usuário
2 - Backend com a regras de negocios, estruturas de segurnaça e as definições dos endpoints
3 - Banco MySQL para persistencia dos dados
4 - EStá hospedada em um servidor Linux Ubuntu 24.04

## Resumo das Tecnologias utilizadas

Tecnologia | Função
---------- | ------
Python | linguagem principal
FastAPI | API REST
PyMuPDF / pdfplumber | (leitura de PDFs)
PostgreSQL 16 | Banco de dados
SQLAlchemy | ORM
Alembic | Migrations
Pydantic | DTOs / Contratos
Keycloak | Autenticação
OAuth2 | Protocolo
RBAC | Autorização
Celery | Execução assíncrona
Redis | Fila
WeasyPrint | PDF
Docker | Container
Ubuntu | Servidor
Nominatim | Geocoding (lat/lng → nome cidade)
Haversine | Cálculo distância (Localmente)
Leaflet | Renderização mapa (frontend)
Playwright | Screenshot OSM (sem API)

## Resumo da Arquitetura

```text
Frontend (Web)
   ⇅ JSON (DTOs Pydantic)
API (FastAPI)
   ⇅ Services / Use Cases
Domínio (DDD)
   ⇅ Repositórios
Infraestrutura
   ├─ PostgreSQL
   ├─ Keycloak (Auth)
   ├─ Celery + Redis
   └─ Repositorio   
```

## Stack Tecnológico (Python + Linux)

### Infraestrutura

* Ubuntu Server 22.04
* Docker + Docker Compose
* Nginx
* PostgreSQL 16
* Redis

### Backend do Sistema

* Python 3.12
* FastAPI
* Pydantic
* SQLAlchemy 2.0
* Alembic
* Celery + Redis 
* PyMuPDF / pdfplumber (leitura de PDFs)

### Web / Scraping

* Playwright (acesso a sites com login)
* Requests / HTTPX
* Google Maps API

### Frontend (Prévia de Laudo)

* React + Vite
* Quill / TipTap (editor rich-text)
* Drag & Drop (react-dnd)
* Upload de imagens + colar prints (clipboard API)

### GeraPDF

* WeasyPrint ou ReportLab
* Templates HTML → PDF

## Funcionalidades

### Lista de Funcionalidades

1. Ferramenta de Geolocalização


## 1. Ferramenta de Geolocalização

A primeira do sistema é a Ferramenta de Geolocalização, localiza __dois endereço__, plota em um MAP, desenha a rota entre eles mostrandor a distancia e mostra a distancia em KM, vamos utilizar a API do Google Maps e adiciona um comentário sobre a distancia entre os dois endereços.

### Maps & Geolocalização

```text

#Bibliotecas de Geolocalização

OpenStreetMap + Nominatim + Haversine (Open Source e GRÁTIS)
├─ Nominatim: Geocoding (lat/lng → nome cidade)
├─ Haversine: Cálculo distância (100% local)
├─ Leaflet: Renderização mapa (frontend)
└─ Playwright: Screenshot OSM (sem API)
```

### Fluxo da Ferramenta:

#### 1. Importação do Contrato (Tela do Frontend)

* O usuário faz Upload de um contrato digital em formato PDF.
* Deste arquivo em PDF o sistema extrai as seguintes informações do client:
* CPF Cliente.
* Numero do contrato.
* Coordenadas do Endereço de assinatura do contrato
* O sistema salva os dados na Tabela __"dados_contrato"__, do banco __sistema_de_laudos__ da aplicação.
* As coordenadas de assinatura do contrato serão usadas para como o **primeiro endereço**.

#### 2. Extração dados Bureau (Backend)

* Usando o **CPF do Cliente** como chave de consulta o sistema busca em um base de dados MySQL externa as seguintes informações:
* Nome do Cliente.
* Logradouro (nome da rua)
* Telefone.
* CEP
* O sistema salva os dados na Tabela __"dados_bureau"__, do banco __sistema_de_laudos__ da aplicação. 
* O Logadraouro vai ser usado como **segundo endereço**.

### 3. Geração do MAPA

* O sistema usa as Bibliotecas de Geolocalização para calcular a distância e gerar o mapa 
* Insere o Primeiro e Segundo endereço
* Calcula a distancia entre eles
* Gera o Mapa e mostra na tela do FrontEnd a rota demarcando a distância entre os dois endereços.

### 4. Analise do Parecer
* Após plotar na tela o mapa o sistema analisa a distancia entre os dois endereços e de acordo coma distância adiciona um parecer.
* A lista de pareceres será gravada no Banco __sistema_de_laudos__ na tabela pareceres.
* O sistema busca em suas regras internas qual é o parecer que deve ser utilizado, de acordo com a distancia entre os endereços.

<!-- Parecer -->
<!--  Ao confrontarmos os endereços constatamos que a geolocalização da formalização possui até 5 km de distância do endereço
de cadastro do reclamante, conforme consulta em bureau externo. -->
<!-- Tratar ruas que não possuem CEP, só o geral da cidade -->
