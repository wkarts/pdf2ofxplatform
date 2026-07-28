# Arquitetura

```text
Internet
  │
  ▼
CloudPanel / TLS / Reverse Proxy
  │ 127.0.0.1:8080
  ▼
NGINX gateway
  │ FastCGI
  ▼
Laravel
  │ HTTP interno autenticado
  ▼
FastAPI ── Redis/Celery ── Worker Python
                            │
                            ├─ preflight do PDF
                            ├─ extração textual
                            ├─ OCR sob demanda
                            ├─ parser bancário
                            ├─ reconciliação
                            └─ OFX 1.02
```

## Responsabilidades

- **Laravel:** upload, interface, sessão anônima, metadados, status, revisão e
  download;
- **FastAPI:** contrato interno, validação do upload e acesso aos jobs;
- **Celery worker:** processamento pesado, OCR, parser e geração OFX;
- **Redis:** broker Celery, fila Laravel, cache e sessão;
- **PostgreSQL:** somente metadados da conversão;
- **volume `converter_jobs`:** PDF temporário, JSON normalizado e OFX com TTL;
- **cleaner:** remove jobs expirados;
- **CloudPanel:** domínio, TLS e reverse proxy.

## Fluxo

```text
Upload
  → validação de MIME/tamanho/assinatura PDF
  → job assíncrono
  → inspeção rápida com pypdf
  → pdfplumber ou OCR
  → detecção do parser
  → normalização das transações
  → reconciliação
  → OFX
  → revisão/download
  → expiração automática
```

## Privacidade

O banco de dados não armazena PDF, OFX nem lista de transações. Cada conversão
possui um UUID e um identificador de sessão, impedindo que o histórico anônimo
seja exibido para outra sessão do navegador.

## Extensibilidade

Cada banco implementa `StatementParser`, com `detect()` e `parse()`. Os parsers
recebem `ExtractedDocument`; portanto, não dependem de FastAPI, Celery ou
Laravel.
